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
import psutil
import networkx

from sonLib.bioio import logger
from sonLib.bioio import setLoggingFromOptions
from sonLib.bioio import getTempDirectory
from sonLib.bioio import system

from jobTree.scriptTree.target import Target 
from jobTree.scriptTree.stack import Stack

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
    parser.add_option_group(ktGroup)
                       
                       
                       
    
 
    return parser

def validateOptions(options):
    if options.database != "tokyo_cabinet" and\
       options.database != "kyoto_tyocoon":
        raise RuntimeError("Invalid database type: %s" % options.database)

def parseOptionsFile(path):
    if not os.path.isfile(path):
        raise RuntimeError("Options File not found: %s" % path)
    args = []
    optFile = open(path, "r")
    for l in optFile:
        line = l.rstrip()
        if line:
            args += line.split()

def runResume(jtPath):
    pass

def runCactus(workDir):
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
        if os.path.exists(jtPath):
            print("jobTree found in %s: attempting to resume..\n"
                  " (if you want to start from scratch, make sure the supplied"
                  "\n workDir doesn't exist or doesn't contain a /jobTree"
                  " sub directory)\n" % workDir)
            runResume(jtPath)
        else:
            projWrapper = ProjectWrapper(options, seqFile, workDir)
            projWrapper.writeXml()
            runCactus(workDir)
            
        return 0
    except RuntimeError, e:
        print "Error: " + str(e)
        return -1

if __name__ == '__main__':
    sys.exit(main())
