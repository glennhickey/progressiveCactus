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
import socket
import signal
import traceback

from sonLib.bioio import logger
from sonLib.bioio import setLoggingFromOptions
from sonLib.bioio import getTempDirectory
from sonLib.bioio import system
from sonLib.bioio import popenCatch

from jobTree.scriptTree.target import Target 
from jobTree.scriptTree.stack import Stack

from cactus.progressive.ktserverLauncher import KtserverLauncher
from cactus.progressive.multiCactusProject import MultiCactusProject
from cactus.progressive.experimentWrapper import ExperimentWrapper
from cactus.progressive.configWrapper import ConfigWrapper

from seqFile import SeqFile
from projectWrapper import ProjectWrapper

def initParser():
    usage = "usage: runProgressiveCactus.sh [options] <seqFile> <workDir> <outputHalFile>\n\n"\
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
    parser.add_option("--configFile", dest="configFile",
                      help="Specify cactus configuration file",
                      default=None)

    #Kyoto Tycoon Options
    ktGroup = OptionGroup(parser, "kyoto_tycoon Options",
                          "Kyoto tycoon provides a client/server framework "
                          "for large in-memory hash tables and is available "
                          "via the --database option.")
    ktGroup.add_option("--ktHost", dest="ktHost",
                       help="host to specifiy for ktserver",
                       default=socket.gethostname())
    ktGroup.add_option("--ktPort", dest="ktPort",
                       help="starting port (lower bound of range) of ktservers",
                       default=1978)
    ktGroup.add_option("--ktType", dest="ktType",
                       help="Kyoto Tycoon server type "\
                            "(memory, snapshot, or disk)",
                       default='memory')
    # sonlib doesn't allow for spaces in attributes in the db conf
    # which renders this options useless
    #ktGroup.add_option("--ktOpts", dest="ktOpts",
    #                   help="Command line ktserver options",
    #                   default=None)
    ktGroup.add_option("--ktCreateTuning", dest="ktCreateTuning",
                       help="ktserver options when creating db "\
                            "(ex #bnum=30m#msiz=50g)",
                       default=None)
    ktGroup.add_option("--ktOpenTuning", dest="ktOpenTuning",
                       help="ktserver options when opening existing db "\
                            "(ex #opts=ls#ktopts=p)",
                       default=None)
    ktGroup.add_option("--dontCleanKtservers", dest="dontCleanKtservers",
                       action="store_true", default=False)
    parser.add_option_group(ktGroup)
 
    return parser

# Try to weed out errors early by checking options and paths
def validateInput(workDir, outputHalFile, options):
    try:
        if workDir.find(' ') >= 0:
            raise RuntimeError("Cactus does not support spaces in pathnames: %s"
                               % workDir)
        if not os.path.isdir(workDir):
            os.makedirs(workDir)
        if not os.path.isdir(workDir) or not os.access(workDir, os.W_OK):
            raise
    except:
        raise RuntimeError("Can't write to workDir: %s" % workDir)
    try:
        open(outputHalFile, "w")
    except:
        raise RuntimeError("Unable to write to hal: %s" % outputHalFile)
    if options.database != "tokyo_cabinet" and\
        options.database != "kyoto_tycoon":
        raise RuntimeError("Invalid database type: %s" % options.database)
    if options.outputMaf is not None:
        try:
            open(options.outputMaf, "w")
        except:
            raise RuntimeError("Unable to write to maf: %s" % options.outputMaf)
    if options.configFile is not None:
        try:
            ConfigWrapper(ET.parse(options.configFile).getroot())
        except:
            raise RuntimeError("Unable to read config: %s" % options.configFile)
    if options.database == 'kyoto_tycoon':
        if options.ktType.lower() != 'memory' and\
           options.ktType.lower() != 'snapshot' and\
           options.ktType.lower() != 'disk':
            raise RuntimeError("Invalid ktserver type specified: %s. Must be "
                               "memory, snapshot or disk" % options.ktType)    

# Convert the jobTree options taken in by the parser back
# out to command line options to pass to progressive cactus
def getJobTreeCommands(jtPath, parser, options):
    cmds = "--jobTree %s" % jtPath
    for optGroup in parser.option_groups:
        if optGroup.title == "JobTree Options":
            for opt in optGroup.option_list:
                if hasattr(options, opt.dest) and \
                    getattr(options, opt.dest) != optGroup.defaults[opt.dest]:
                    cmds += " %s" % str(opt)
                    if opt.nargs > 0:
                        cmds += " %s" % getattr(options, opt.dest)
    return cmds

# Go through a text file and add every word inside to an arguments list
# which will be prepended to sys.argv.  This way both the file and
# command line are passed to the option parser, with the command line
# getting priority. 
def parseOptionsFile(path):
    if not os.path.isfile(path):
        raise RuntimeError("Options File not found: %s" % path)
    args = []
    optFile = open(path, "r")
    for l in optFile:
        line = l.rstrip()
        if line:
            args += shlex.split(line)

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
        cmd = '. %s && jobTreeStatus --jobTree %s 2>&1' % (envFile, jtPath)
        output = popenCatch(cmd)
        if output.find('There are 0 jobs currently in job tree') < 0:
            return True
    except:
        return False
    
def runResume(workDir, jtPath):
    envFile = getEnvFilePath()
    logFile = os.path.join(workDir, 'cactus.log')
    cmd = '. %s && jobTreeRun --jobTree %s &> %s' % (envFile, jtPath, logFile)
    system(cmd)

# Run cactus progressive on the project that has been created in workDir.
# Any jobtree options are passed along.  Should probably look at redirecting
# stdout/stderr in the future.
def runCactus(workDir, jtCommands):
    envFile = getEnvFilePath()
    pjPath = os.path.join(workDir, ProjectWrapper.alignmentDirName,
                          '%s_project.xml' % ProjectWrapper.alignmentDirName)
    logFile = os.path.join(workDir, 'cactus.log')
    cmd = '. %s && cactus_progressive.py %s %s &> %s' % (envFile, jtCommands,
                                                         pjPath, logFile)
    system(cmd)

def checkCactus(workDir, options):
    pass

# Call cactus2hal to extract a single hal file out of the progressive
# alignmenet in the working directory.  If the maf option was set, we
# just move out the root maf.  
def extractOutput(workDir, outputHalFile, options):
    if options.outputMaf is not None:
        rootPath = os.path.join(workDir, ProjectWrapper.alignmentDirName,
        SeqFile.rootName, SeqFile.rootName + '.maf')
        cmd = 'mv %s %s' % (rootPath, options.outputMaf)
        system(cmd)
    envFile = getEnvFilePath()
    logFile = os.path.join(workDir, 'cactus2hal.log')
    pjPath = os.path.join(workDir, ProjectWrapper.alignmentDirName,
                          '%s_project.xml' % ProjectWrapper.alignmentDirName)
    cmd = '. %s && cactus2hal.py %s %s &> %s' % (envFile, pjPath,
                                                 outputHalFile, logFile)
    system(cmd)

# Trailing ktservers are constant source of aggravation.  If an error
# occurs during the alignment, we traverse the progressive alignment in
# the working dir and attempt to kill the server for each subtree.
# There is an option, dontCleanKtservers, to prevent this since they
# are frequently useful for debugging.
# Note workDir and options are added to cleanKtServers() as closure
# arguments to abide by signal interface
def cleanKtServersCallback(workDir, options):
    def cleanKtServers(signal, frame):
        try:
            if options.database == "kyoto_tycoon" and\
                   options.dontCleanKtservers == False:
                pjPath = os.path.join(workDir, ProjectWrapper.alignmentDirName,
                                      '%s_project.xml' %
                                      ProjectWrapper.alignmentDirName)
                mcProj = MultiCactusProject()
                mcProj.readXML(pjPath)
                sys.stderr.write("Attempting to clean any trailing ktservers.."
                                 " (please be patient)\n\n")
                for node,expPath in mcProj.expMap.items():
                    try:
                        exp = ExperimentWrapper(ET.parse(expPath).getroot())
                        ktserver = KtserverLauncher()
                        ktserver.killServer(exp)
                    except:
                        pass
        except:
            pass
    return cleanKtServers

def main():
    # init as dummy function
    cleanKtFn = lambda x,y:x
    stage = -1
    workDir = None
    try:
        parser = initParser()
        options, args = parser.parse_args()
        if len(args) != 3:
            raise RuntimeError("Error parsing command line. Exactly 3 arguments are required but %d arguments were detected: %s" % (len(args), str(args)))
        
        if options.optionsFile != None:
            fileArgs = parseOptionsFile(options.optionsFile)
            options, args = parser.parse_args(fileArgs + sys.argv[1:])
            if len(args) != 3:
                raise RuntimeError("Error parsing options file.  Make sure all "
                                   "options have -- prefix")
        stage = 0
        setLoggingFromOptions(options)
        seqFile = SeqFile(args[0])
        workDir = args[1]
        outputHalFile = args[2]
        validateInput(workDir, outputHalFile, options)

        cleanKtFn = cleanKtServersCallback(workDir, options)
        signal.signal(signal.SIGINT, cleanKtFn)

        jtPath = os.path.join(workDir, "jobTree")
        stage = 1
        print "\nBeginning Alignment"
        if canContinue(jtPath):
            print("incomplete jobTree found in %s/jobTree: attempting to "
                  "resume..\n"
                  " (if you want to start from scratch, delete %s "
                  "then rerun)\n" % (workDir, workDir))
            runResume(workDir, jtPath)
        else:
            system("rm -rf %s" % jtPath) 
            projWrapper = ProjectWrapper(options, seqFile, workDir)
            projWrapper.writeXml()
            jtCommands = getJobTreeCommands(jtPath, parser, options)
            runCactus(workDir, jtCommands)
        cmd = 'jobTreeStatus --failIfNotComplete --jobTree %s &> /dev/null' %\
              jtPath
        system(cmd)

        stage = 2
        print "Beginning HAL Export"
        extractOutput(workDir, outputHalFile, options)
        print "Success.\n" "Temporary data was left in: %s\n" \
              % workDir
        
        return 0
    
    except RuntimeError, e:
        sys.stderr.write("Error: %s\n\n" % str(e))
        if stage >= 0 and os.path.isdir(workDir):
            sys.stderr.write("Temporary data was left in: %s\n" % workDir)
        if stage == 1:
            sys.stderr.write("More information can be found in %s\n" %
                             os.path.join(workDir, "cactus.log"))
        elif stage == 2:
            sys.stderr.write("More information can be found in %s\n" %
                             os.path.join(workDir, "cactus2hal.log"))
        if stage > 0:
            cleanKtFn(workDir, options)
        return -1

if __name__ == '__main__':
    sys.exit(main())
