#!/usr/bin/env python

# Progressive Cactus Package
# Copyright (C) 2009-2013 by Glenn Hickey (hickey@soe.ucsc.edu)
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
from time import sleep
import signal
import traceback
from threading import Thread

from jobTree.src.master import getJobFileDirName, getConfigFileName
from jobTree.src.jobTreeStatus import parseJobFiles

from cactus.progressive.multiCactusProject import MultiCactusProject
from cactus.progressive.experimentWrapper import ExperimentWrapper
from cactus.pipeline.ktserverControl import pingKtServer

from seqFile import SeqFile
from projectWrapper import ProjectWrapper

###############################################################################
# Keep tabs on how progressive cactus is doing.  In particular look for:
# - errors in jobTreeStatus
# - which ktservers are running
#
# we use this information to detect cases where some kind of failure leads
# ktservers running and nothing else.  the logic for calling these deadlocks is
# - the same ktservers have been running for more than deadlockTime
# - AND no other jobs have been running for this time
# - AND there is some kind of error message in the log
# Make sure I'm a daemon! 
###############################################################################
class JobStatusMonitor(Thread):
    def __init__(self, jobTreePath, projectPath, logPath, pollTime=400,
                 deadlockTime=1200, deadlockCallbackFn=None):
        Thread.__init__(self)
        self.jobTreePath = jobTreePath
        self.projectPath = projectPath
        self.logPath = logPath
        self.pollTime = pollTime
        self.deadlockTime = deadlockTime
        self.deadlockCallbackFn = deadlockCallbackFn
        self.daemon = True

    ###########################################################################
    # Get the active jobs as done by jobTreeStatus, which is the world-renowned
    # expert at doing this. If the same jobs are running as last time we polled
    # add the polltime to sameJobsTime
    ###########################################################################
    def __pollJobTree(self):
        childJobFileToParentJob, childCounts =  {}, {}
        updatedJobFiles, shellJobs = set(), set()
        try:
            parseJobFiles(getJobFileDirName(self.jobTreePath),
                          updatedJobFiles, childJobFileToParentJob,
                          childCounts, shellJobs)
            failedJobs = [ job for job in updatedJobFiles | \
                           set(childCounts.keys()) \
                           if job.remainingRetryCount == 0 ]

            self.curActiveJobs = set()
            for job in updatedJobFiles:
                self.curActiveJobs.add(job.getJobFileName())
            self.failedJobs = max(len(failedJobs), self.failedJobs)

        except:
            self.curActiveJobs = set()

        if len(self.prevActiveJobs) > 0 and len(self.curActiveJobs) > 0 and\
               self.curActiveJobs == self.prevActiveJobs:
            self.sameJobsTime += self.pollTime
        else:
            self.sameJobsTime = 0
            self.prevActiveJobs = set(self.curActiveJobs)

    ###########################################################################
    # Get the active ktservers
    ###########################################################################
    def __pollKtServers(self):
        self.curKtservers = set()
        try:
            mc = MultiCactusProject()
            mc.readXML(self.projectPath)
            for eventName,expPath in mc.expMap.items():
                exp = ExperimentWrapper(ET.parse(expPath).getroot())
                try:
                    if pingKtServer(exp):
                        self.curKtservers.add("%s_%s:%s" % (
                            eventName, exp.getDbHost(), str(exp.getDbPort())))
                except:
                    pass
                try:
                    secElem = exp.getSecondaryDBElem()
                    if secElem is not None and pingKtServer(secElem):
                        self.curKtservers.add("%s_secondary_%s:%s" % (
                            eventName, secElem.getDbHost(),
                            str(secElem.getDbPort())))
                except:
                    pass
                        
        except:
            self.curKtservers = set()
        if len(self.prevKtservers) > 0 and len(self.curKtservers) > 0 and\
               self.curKtservers == self.prevKtservers:
            self.sameKtserversTime += self.pollTime
        else:
            self.prevKtservers = set(self.curKtservers)
            self.sameKtserversTime = 0

                 
    def __resetTimes(self):
        self.curActiveJobs = set()
        self.prevActiveJobs = set()
        self.failedJobs = 0
        self.curKtservers = set()
        self.prevKtservers = set()
        self.sameJobsTime = 0
        self.sameKtserversTime = 0

    def __hints(self):
        sys.stderr.write(" It is likely that Progressive Cactus " +
                         "is in a deadlock state and will not finish"+
                         " until the servers or your batch system" +
                         " time out.")
        sys.stderr.write(" Suggestions:\n" +
                         "* look for fatal errors in %s\n" % (
                             self.logPath) +
                         "* jobTreeStatus --jobTree %s --verbose\n"%(
                             self.jobTreePath) +
                         "* check your resource manager to see if " +
                         "any more jobs are queued. maybe your "+
                         "cluster is just busy...\n" +
                         "* if not it's probably time to abort.\n")
        sys.stderr.write("Note that you can (and probably should)" +
                         " kill any trailing ktserver jobs by"
                         " running\n  rm -rf %s" % self.jobTreePath +
                         "\nThey will eventually timeout on their"+
                        " own but it could take days.\n\n")

    ###########################################################################
    # Poll until we hit a deadlock.  If that happens print a warning
    # and call the callback (if specified)
    ###########################################################################
    def run(self):
        self.__resetTimes()
        
        while True:
            sleep(self.pollTime)
            self.__pollJobTree()
            self.__pollKtServers()

            if self.sameJobsTime > self.deadlockTime and\
               self.sameKtserversTime > self.deadlockTime:
                hangTime = min(self.sameJobsTime, self.sameKtserversTime)
                failedJobs = self.failedJobs
                sys.stderr.write("\n\n"
                                 "*****************************************"
                                 "*****************************************\n"
                                 "*****************************************"
                                 "*****************************************\n"
                                 "**                                    ALE"
                                 "RT                                     **\n"
                                 "*****************************************"
                                 "*****************************************\n"
                                 "*****************************************"
                                 "*****************************************\n")
                sys.stderr.write("The only jobs that I have detected running" +
                                 " for at least the past %ds" % hangTime +
                                 " are %d ktservers." % len(self.curKtservers))
                if failedJobs > 0:
                    sys.stderr.write(" Furthermore, there appears to have " +
                                     "been %d failed jobs. " % failedJobs)    
                if self.deadlockCallbackFn is not None:
                    self.deadlockCallbackFn()
                else:
                    self.__hints()
                    self.__resetTimes()
                    self.deadlockTime *= 2
                                                                   



