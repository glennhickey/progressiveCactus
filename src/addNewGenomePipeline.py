#!/usr/bin/env python
from optparse import OptionParser
import sys
import networkx as NX
from sonLib.bioio import getTempDirectory
from sonLib.nxtree import NXTree
from sonLib.nxnewick import NXNewick
from hal.stats.halStats import getHalTree
from progressiveCactus import main as progressiveCactusMain
from cactus.progressive.multiCactusTree import MultiCactusTree
import subprocess
import os

def usage():
    sys.stderr.write("usage: %s addToNode or %s addToBranch\n" % (sys.argv[0],
                                                                  sys.argv[0]))
    sys.stderr.write("addToNode arguments: halFile parentName leafName leafPath"
                     + " leafDistance\n")
    sys.stderr.write("addToBranch arguments: halFile parentName childName "
                     + "intermediateName leafName leafPath "
                     + "intermediate-leafDist parent-intermediateDistance\n")
    sys.exit(1)

def createSeqFile(tree, pathMap, outPath, outgroup=None):
    outFile = open(outPath, 'w')
    botTreeString = NXNewick().writeString(tree)
    outFile.write(botTreeString + '\n')
    for (name, path) in pathMap.items():
        seqLine = "%s %s\n" % (name, path)
        if name == outgroup:
            seqLine = "*" + seqLine
        outFile.write(seqLine)

def extractFasta(halFile, genome, outPath):
    command = "hal2fasta %s %s --outFaPath %s" % (halFile, genome, outPath)
    p = subprocess.Popen(command.split())
    p.wait()
    if p.returncode:
        sys.stderr.write("command %s failed with return code %d\n" % (command,
                                                                  p.returncode))
        sys.exit(1)

def runProgressiveCactus(seqFile, outPath, extraArgs=[]):
    progressiveCactusMain(extraArgs + [seqFile, getTempDirectory(), outPath])

def runAddToBranch(halPath, botHalPath, topHalPath, parentName, childName,
                       intermediateName, leafName, parentDist, leafDist):
    command = "halAddToBranch %s %s %s %s %s %s %s %f %f" % (halPath,
                        botHalPath, topHalPath, parentName, intermediateName,
                        childName, leafName, parentDist, leafDist)
    p = subprocess.Popen(command.split())
    p.wait()
    if p.returncode:
        sys.stderr.write("command %s failed with return code %d\n" % (command,
                                                                  p.returncode))
        sys.exit(1)

def runAddToNode(halPath, realignHalPath, parentName, leafName, leafDist):
    command = "halAddToNode %s %s %s %s %f" % (halPath, realignHalPath,
                                               parentName, leafName, leafDist)
    p = subprocess.Popen(command.split())
    p.wait()
    if p.returncode:
        sys.stderr.write("command %s failed with return code %d\n" % (command,
                                                                  p.returncode))
        sys.exit(1)

def addToNode(args, extraArgs):
    if len(args) != 7:
        usage()
    pathMap = {}

    halFile = args[2]
    parentName = args[3]
    leafName = args[4]
    pathMap[leafName] = args[5]
    leafDist = float(args[6])

    origTree = MultiCactusTree(NXNewick().parseString(getHalTree(halFile)))
    origTree.nameUnlabeledInternalNodes()
    origTree.computeSubtreeRoots()
    # Create the realignment subtree
    tempDir = getTempDirectory()
    realignSeqFilePath = os.path.join(tempDir, "realignSeqfile")
    tree = origTree.extractSubTree(parentName)
    tree.addOutgroup(leafName, leafDist)
    for node in botTree.postOrderTraversal():
        if botTree.getName(node) == leafName:
            continue
        fastaPath = os.path.join(tempDir, str(node) + '.fa')
        extractFasta(halPath, botTree.getName(node), fastaPath)
        pathMap[botTree.getName(node)] = fastaPath
    createSeqFile(tree, pathMap, realignSeqFilePath)
    realignHalPath = os.path.join(tempDir, "realign.hal")
    runProgressiveCactus(realignSeqFilePath, realignHalPath, extraArgs)
    runAddToNode(halFile, realignHalPath, parentName, leafName, leafDist)

def addToBranch(args, extraArgs):
    if len(args) != 10:
        usage()
    pathMap = {}

    halFile = args[2]
    parentName = args[3]
    childName = args[4]
    intermediateName = args[5]
    leafName = args[6]
    pathMap[leafName] = args[7]
    leafDist = float(args[8])
    parentDist = float(args[9])

    origParentId = -1
    origChildId = -1
    origTree = MultiCactusTree(NXNewick().parseString(getHalTree(halFile)))
    for node in origTree.postOrderTraversal():
        nodeName = origTree.getName(node)
        if nodeName == parentName:
            origParentId = node
        elif nodeName == childName:
            origChildId = node
    parentChildDist = origTree.getWeight(origParentId, origChildId)
    childDist = parentChildDist - parentDist
    assert(childDist > 0)
    tempDir = getTempDirectory()
    pathMap[childName] = os.path.join(tempDir, 'child.fa')
    extractFasta(halFile, childName, pathMap[childName])
    pathMap[parentName] = os.path.join(tempDir, 'parent.fa')
    extractFasta(halFile, parentName, pathMap[parentName])
    botSeqFilePath = os.path.join(tempDir, 'botSeqfile')
    tree = NXTree()
    dg = NX.DiGraph()
    dg.add_edge(0, 1, weight=leafDist)
    dg.add_edge(0, 2, weight=childDist)
    dg.add_edge(0, 3, weight=parentDist)
    tree.loadNetworkXTree(dg)
    tree.setName(0, intermediateName)
    tree.setName(1, leafName)
    tree.setName(2, childName)
    tree.setName(3, parentName)
    createSeqFile(tree, pathMap, botSeqFilePath, outgroup=parentName)
    botHalPath = os.path.join(tempDir, 'bot.hal')
    runProgressiveCactus(botSeqFilePath, botHalPath, extraArgs)
    pathMap[intermediateName] = os.path.join(tempDir, 'intermediate.fa')
    extractFasta(botHalPath, intermediateName, pathMap[intermediateName])

    # Find parent's other children (they need to be included in the top hal
    # file)
    otherChildrenIds = origTree.getChildren(origParentId)
    otherChildren = map(origTree.getName, otherChildrenIds)
    otherChildrenDists = map(lambda x: origTree.getWeight(origTree.getParent(x),
                                                          x),
                             otherChildrenIds)
    # Remove the child that won't be a child of this node after the
    # insertion of the intermediate
    removedChildIdx = otherChildren.index(childName)
    otherChildrenIds.pop(removedChildIdx)
    otherChildren.pop(removedChildIdx)
    otherChildrenDists.pop(removedChildIdx)
    for (i, child) in enumerate(otherChildren):
        childPath = os.path.join(tempDir, 'child%d.fa' % i)
        extractFasta(halFile, child, childPath)
        pathMap[child] = childPath
    tree = NXTree()
    dg = NX.DiGraph()
    dg.add_edge(0, 1, weight=parentDist)
    for (i, child) in enumerate(otherChildren):
        dg.add_edge(0, i + 2, weight=otherChildrenDists[i])
    tree.loadNetworkXTree(dg)
    tree.setName(0, parentName)
    tree.setName(1, intermediateName)
    for (i, child) in enumerate(otherChildren):
        tree.setName(i + 2, child)
    topSeqFilePath = os.path.join(tempDir, 'topSeqfile')
    createSeqFile(tree, pathMap, topSeqFilePath)
    topHalPath = os.path.join(tempDir, 'top.hal')
    runProgressiveCactus(topSeqFilePath, topHalPath, extraArgs)
    runAddToBranch(halFile, botHalPath, topHalPath, parentName, childName,
                       intermediateName, leafName, parentDist, leafDist)

def main():
    args = [arg for arg in sys.argv if arg[:2] != "--"]
    extraArgs = [arg for arg in sys.argv if arg[:2] == "--"]
    if len(args) < 2:
        usage()
    if args[1] == "addToNode":
        addToNode(args, extraArgs)
    elif args[1] == "addToBranch":
        addToBranch(args, extraArgs)
    else:
        usage()

if __name__ == "__main__":
    main()
