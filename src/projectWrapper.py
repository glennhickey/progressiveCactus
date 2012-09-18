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
import string
import socket

from sonLib.bioio import system

from seqFile import SeqFile
from cactus.progressive.experimentWrapper import ExperimentWrapper
from cactus.progressive.configWrapper import ConfigWrapper
from cactus.shared.common import cactusRootPath


# Wrap up the cactus_progressive interface:
# - intialize the working directory
# - create Experiment file from seqfile and options
# - create Config file from options
# - run cactus_createMultiCactusProject
# - now ready to launch cactus progressive
class ProjectWrapper:
    alignmentDirName = 'progressiveAlignment'
    def __init__(self, options, seqFile, workingDir):
        self.options = options
        self.seqFile = seqFile
        self.workingDir = workingDir
        self.configWrapper = None
        self.experimentWrapper = None
        self.processConfig()
        self.processExperiment()

    def processConfig(self):
        # read in the default right out of cactus
        dir = os.path.join(cactusRootPath(), "progressive")
        configPath = os.path.join(dir, "cactus_progressive_workflow_config.xml")
        configXml = ET.parse(configPath).getroot()
        self.configWrapper = ConfigWrapper(configXml)
        # here we can go through the options and apply some to the config

    def processExperiment(self):
        expXml = self.seqFile.toXMLElement()
        #create the cactus disk
        cdElem = ET.SubElement(expXml, "cactus_disk")
        database = self.options.database
        assert database == "kyoto_tycoon" or database == "tokyo_cabinet"
        confElem = ET.SubElement(cdElem, "st_kv_database_conf")
        confElem.attrib["type"] = database
        dbElem = ET.SubElement(confElem, database)

        if self.options.database == "kyoto_tycoon":
            dbElem.attrib["host"] = self.options.host
            dbElem.attrib["port"] = self.options.port
            
        self.experimentWrapper = ExperimentWrapper(expXml)

    def writeXml(self):
        if not os.path.exists(self.workingDir):
            os.makedirs(self.workingDir)
        if not os.path.isdir(self.workingDir):
            raise RuntimeError("Error creating workDir %s" % self.workingDir)
        
        configPath = os.path.abspath(
            os.path.join(self.workingDir, "config.xml"))
        expPath = os.path.abspath(
            os.path.join(self.workingDir, "expTemplate.xml"))
        self.experimentWrapper.setConfigPath(configPath)
        self.configWrapper.writeXML(configPath)
        self.experimentWrapper.writeXML(expPath)

        projPath = os.path.join(self.workingDir,
                                ProjectWrapper.alignmentDirName)
        if os.path.exists(projPath):
            system("rm -rf %s" % projPath)

        system("cactus_createMultiCactusProject.py %s %s" % (expPath, projPath))
        
        
        

        
        
