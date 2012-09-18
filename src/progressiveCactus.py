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
#!/usr/bin/env python

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
import socket

from sonLib.bioio import logger
from sonLib.bioio import setLoggingFromOptions
from sonLib.bioio import getTempDirectory
from sonLib.bioio import system
from sonLib.bioio import popenCatch

from jobTree.scriptTree.target import Target 
from jobTree.scriptTree.stack import Stack

from cactus.progressive.ktserverLauncher import KtserverLauncher
from cactus.progressive.multiCactusProject import MultiCactusProject

from seqFile import SeqFile
from projectWrapper import ProjectWrapper

def initParser():
    usage = "usage: %prog [options] <seqFile> <workDir> <outputHalFile>\n\n"\
             "Required Arguments:\n"\
             "  <seqFile>\t\tFile containing newick tree and seqeunce paths"\
             " paths.\n"\
             "\t\t\t(see documetation or examples for format).\n"\
             "  <workDir>\t\tWorking directory (which can grow "\
             "exteremely large)\n"\
             "  <outputHalFile>\tPath of output alignment in .hal format."
    
    parser = OptionParser(usage=usage)

    #JobTree Options
    jtGroup = OptionGroup(parser, "JobTree Options",
                          "JobTree is a Python framework managing parallel "
                          "processes, used by Progressive Cactus.  These "
                          "options can be used to tune how it works with "
                          "your batch system.")    
    Stack.addJobTreeOptions(jtGroup)
    #Progressive Cactus will handle where the jobtree path is
    jtGroup.remove_option("--jobTree")
    parser.add_option_group(jtGroup)

    #Progressive Cactus Options
    parser.add_option("--optionsFile", dest="optionsFile",
                      help="Text file containing command line options to use as"\
                      " defaults", default=None)
    parser.add_option("--database", dest="database",
                      help="Database type: tokyo_cabinet or kyoto_tycoon",
                      default="tokyo_cabinet")
    parser.add_option("--outputMaf", dest="outputMaf",
                      help="Path of output alignment in .maf format.",
                      default=None)


    #Kyoto Tycoon Options
    ktGroup = OptionGroup(parser, "kyoto_tycoon Options",
                          "Kyoto tycoon provides a client/server framework "
                          "for large in-memory hash tables and is available "
                          "via the --database option.")
    ktGroup.add_option("--host", dest="host",
                       help="host to specifiy for ktserver",
                       default=socket.gethostname())
    ktGroup.add_option("--port", dest="port",
                       help="starting port (lower bound of range) of ktservers",
                       default=1978)
    ktGroup.add_option("--dontCleanKtservers", dest="dontCleanKtservers",
                       action=store_true, default=False)
    parser.add_option_group(ktGroup)
 
    return parser

# Try to weed out errors early by checking options and paths
def validateOptions(options):
    if options.database != "tokyo_cabinet" and\
       options.database != "kyoto_tyocoon":
        raise RuntimeError("Invalid database type: %s" % options.database)

# Convert the jobTree options taken in by the parser back
# out to command line options to pass to progressive cactus
def getJobTreeCommands(jtPath, parser, options):
    cmds = "--jobTree %s" % jtPath
    for optName in parser.option_list:
        og = parser.get_option_group(optName)  
        if og is not None and og.title == "JobTree Options":
            opt = parser.get_option(optName)
            cmds += " " + optName
            if opt.nargs > 0:
                cmds += getattr(options, opt.dest)
    return cmds

# Go through a text file and add every word inside to an arguments list
# which will be prepended to sys.argv.  This way both the file and
# command line are passed to the option parser, with the command line
# getting priority.  Note that whitespace within tokens could be an issue
def parseOptionsFile(path):
    if not os.path.isfile(path):
        raise RuntimeError("Options File not found: %s" % path)
    args = []
    optFile = open(path, "r")
    for l in optFile:
        line = l.rstrip()
        if line:
            args += line.split()

# This source file should always be in progressiveCactus/src.  So
# we return the path to progressiveCactus/environment, which needs
# to be sourced before doing anything. 
def getEnvFilePath():
    path = os.path.dirname(sys.argv[0])
    envFile = os.path.join(path, '..', 'environment')
    assert os.path.isfile(envFile)
    return envFile

# This is a lame attempt at exposing jobTree's resume functionality.
# The current rule says that if a jobTree folder is found, and its status
# can be queried, and it doesn't say there are 0 jobs left... then
# try to load it with jobTreeRun
def canContinue(jtPath):
    try:
        envFile = getEnvFilePath()
        cmd = '. %s && jobTreeStatus --jobTree %s' % (envFile, jtPath)
        output = popenCatch(cmd)
        if output.find('There are 0 jobs currently in job tree') < 0:
            return True
    except:
        return False
    
def runResume(jtPath):
    envFile = getEnvFilePath()
    cmd = '. %s && jobTreeRun --jobTree %s' % (envFile, jtPath)
    system(cmd)

# Run cactus progressive on the project that has been created in workDir.
# Any jobtree options are passed along.  Should probably look at redirecting
# stdout/stderr in the future.
def runCactus(workDir, jtCommands):
    envFile = getEnvFilePath()
    pjPath = os.path.join(workDir, ProjectWrapper.alignmentDirName,
                          '%s_project.xml' % ProjectWrapper.alignmentDirName)
    cmd = '. %s && cactus_progressive.py %s %s' % (envFile, jtCommands, pjPath)
    system(cmd)

def checkCactus(workDir, options):
    pass

# Call cactus2hal to extract a single hal file out of the progressive
# alignmenet in the working directory.  If the maf option was set, we
# just move out the root maf.  
def extractOutput(workDir, outputHalFile, options):
    if options.outputMaf is not None:
        rootPath = os.path.join(workDir, ProjectWrapper.alignmentDirName,
        SeqFile.rootName, seqFile.rootName + '.maf')
        cmd = 'mv %s %s' % (rootPath, options.outputMaf)
        system(cmd)
    envFile = getEnvFilePath()
    pjPath = os.path.join(workDir, ProjectWrapper.alignmentDirName,
                          '%s_project.xml' % ProjectWrapper.alignmentDirName)
    cmd = '. %s && cactus2hal.py %s %s' % (envFile, jtPath, outputHalFile)
    system(cmd)

# Trailing ktservers are constant source of aggravation.  If an error
# occurs during the alignment, we traverse the progressive alignment in
# the working dir and attempt to kill the server for each subtree.
# There is an option, dontCleanKtservers, to prevent this since they
# are frequently useful for debugging.
def cleanKtServers(workDir, options):
    try:
        if options.database == "kyoto_tycoon" and\
               options.dontCleanKtservers == False:
            pjPath = os.path.join(workDir, ProjectWrapper.alignmentDirName,
                                  '%s_project.xml' %
                                  ProjectWrapper.alignmentDirName)
            mcProj = MultiCactusProject()
            mcProj.readXML(pjPath)
            for node,expPath in mcProj.expMap.items():
                try:
                    exp = ExperimentWrapper(ET.parse(expPath))
                    ktserver = KtserverLauncher()
                    ktserver.killServer(exp)
                except:
                    pass
    except:
        pass

def main():
    try:
        parser = initParser()
        options, args = parser.parse_args()
        if len(args) != 3:
            parser.print_help()
            return 1
        if options.optionsFile != None:
            fileArgs = parseOptionsFile(options.optionsFile)
            options, args = parser.parse_args(fileArgs + sys.argv[1:])
            if len(args) != 3:
                raise RuntimeError("Error parsing options file.  Make sure all "
                                   "options have -- prefix")
        setLoggingFromOptions(options)
        seqFile = SeqFile(args[0])
        workDir = args[1]
        outputHalFile = args[2]
        validateOptions(options)

        jtPath = os.path.join(workDir, "jobTree")
        if canContinue(jtPath):
            print("incomplete jobTree found in %s: attempting to resume..\n"
                  " (if you want to start from scratch, delete %s\n"
                  "then rerun)\n" % workDir)
            runResume(jtPath)
        else:
            system("rm -rf %s" % jtPath) 
            projWrapper = ProjectWrapper(options, seqFile, workDir)
            projWrapper.writeXml()
            jtCommands = getJobTreeCommands(jtPath, parser, options)
            runCactus(workDir, jtCommands)
            
        extractOutput(workDir, outputHalFile, options)
        print "Alignment successful.\n" "Temporary data was left in: %s\n" \
              % workdir
        
        return 0
    
    except RuntimeError, e:
        print "Error: " + str(e)
        cleanKtServers(workDir)
        return -1

if __name__ == '__main__':
    sys.exit(main())
