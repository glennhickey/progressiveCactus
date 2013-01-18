#!/usr/bin/env python

# Progressive Cactus Package
# Copyright (C) 2009-2012 by Glenn Hickey (hickey@soe.ucsc.edu)
# and Benedict Paten (benedictpaten@gmail.com)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import os
import sys
import xml.etree.ElementTree as ET
import math
import time
import random
import copy
from optparse import OptionParser
from optparse import OptionGroup
import imp
import string

from sonLib.nxtree import NXTree
from sonLib.nxnewick import NXNewick

# parse the input seqfile for progressive cactus.  this file is in the
# format of:
#   newick tree
#   name sequencePath
#   name sequencePath
#   ...
# example:
#
# (human, (dog, cat));
# human /hive/seq/human
# dog /users/name/fasta/dog.fa
# cat /tmp/cat/
class SeqFile:
    rootName = 'ProgressiveCactusRoot'
    branchLen = 1
    def __init__(self, path=None):
        if path is not None:
            self.parseFile(path)

    def parseFile(self, path):
        if not os.path.isfile(path):
            raise RuntimeError("File not found: %s" % path)
        self.tree = None
        self.pathMap = dict()
        seqFile = open(path, "r")
        for l in seqFile:
            line = l.strip()
            if line:
                if line[0] == "#":
                    continue
                tokens = line.split()
                if self.tree is None and (len(tokens) == 1 or line[0] == '('):
                    newickParser = NXNewick()
                    try:
                        self.tree = newickParser.parseString(line)
                    except:
                        raise RuntimeError("Failed to parse newick tree: %s" %
                                           line)
                elif line[0] != '(' and len(tokens) >= 2:
                    name = tokens[0]
                    path = string.join(tokens[1:])
                    if name in self.pathMap:
                        raise RuntimeError("Duplicate name found: %s" % name)
                    self.pathMap[name] = path
                elif len(tokens) > 0:
                    sys.stderr.write("Skipping line %s\n" % l)
        
        if self.tree is None:
            self.starTree()
        self.tree.setName(self.tree.getRootId(), SeqFile.rootName)
        self.cleanTree()
        self.validate()

    def starTree(self):
        self.tree = NXTree()
        label = 0
        self.tree.nxDg.add_node(label)
        self.tree.rootId = label
        self.tree.setName(label, SeqFile.rootName)
        for name in self.pathMap.keys():
            label += 1
            self.tree.nxDg.add_edge(0, label)
            self.tree.setName(label, name)
            self.tree.setWeight(0, label, SeqFile.branchLen)
        
    def validate(self):
        if len([i for i in self.tree.postOrderTraversal()]) <= 2:
            raise RuntimeError("At least two valid leaf genomes required in"
                               " input tree")
        for node in self.tree.postOrderTraversal():
            if self.tree.isLeaf(node):
                name = self.tree.getName(node)
                if name not in self.pathMap:
                    raise RuntimeError("No sequence specified for %s" % name)
                else:
                    path = self.pathMap[name]
                    if not os.path.exists:
                        raise RuntimeError("Sequence path not found: %s" % path)

    # remove leaves that do not have sequence data associated with them
    def cleanTree(self):
        numLeaves = 0
        removeList = []
        for node in self.tree.postOrderTraversal():
            if self.tree.isLeaf(node):
                name = self.tree.getName(node)
                if name not in self.pathMap:
                    removeList.append(node)
                numLeaves += 1
        if numLeaves < 2:
            raise RuntimeError("At least two valid leaf genomes required in"
                               " input tree")
        if len(removeList) == numLeaves:
            raise RuntimeError("No sequence path specified for any leaves in the tree")
        for leaf in removeList:
             sys.stderr.write("No sequence path found for %s: skipping\n" % (
                 self.tree.getName(leaf)))
             self.tree.removeLeaf(leaf)

        for node in self.tree.postOrderTraversal():
            if self.tree.hasParent(node):
                parent = self.tree.getParent(node)
                if self.tree.getWeight(parent, node) is None:
                    sys.stderr.write(
                        "No branch length for %s: setting to %d\n" % (
                            self.tree.getName(node), SeqFile.branchLen))
                    self.tree.setWeight(parent, node, SeqFile.branchLen)
                    

    # create the cactus_workflow_experiment xml element which serves as
    # the root node of the experiment template file needed by
    # cactus_createMultiCactusProject.  Note the element is incomplete
    # until the cactus_disk child element has been added
    def toXMLElement(self):
        assert self.tree is not None
        elem = ET.Element("cactus_workflow_experiment")
        seqString = ""
        for node in self.tree.postOrderTraversal():
            if self.tree.isLeaf(node):
                name = self.tree.getName(node)
                path = self.pathMap[name]
                path.replace(" ", "\ ")
                seqString += os.path.abspath(path) + " "
        elem.attrib["sequences"] = seqString
        elem.attrib["species_tree"] = NXNewick().writeString(self.tree)
        elem.attrib["config"] = "defaultProgressive"
        return elem
