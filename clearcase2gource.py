#!/usr/bin/python
"""
   Take the output of the clear case history command and turn it into something usable by gource

   Three Step approach

   Step 1
   ------
   Get the history out of clear case
   cleartool setview yourView
   cd /vob/location
   cleartool lshistory -all -fmt "Element: %n| Date: %d| User:%u| Operation: %e| Object:%[type]p| SimpleType: %m| OperationKind: %o\n" > cc_history
   
   Step 2
   ------
   Run this script
   tac cc_history | ./cc-gsource-conv.py  > gource.log
   Use tac instread of cat because the result of the lshistory comes out backward.

   Step 3
   ------
   gource gource.log
   You may want to customize the gource parameters.
"""
 
import sys
import time
import re

fileTypesWeCareAbout = [ 'compressed_file', 'compressed_text_file', 'file',
'html', 'text_file', 'xml']


def processDate(date):
   """Process the date string into a unix time. Note location isn't handle correctly it goes into local time"""
   d = date[:-6]
   d = time.strptime(d, "%Y-%m-%dT%H:%M:%S")
   return int(time.mktime(d))

def processElement(d):
   """
      Split up the Element into the file name, branch name and version
      Version to be used to detect when a file is created.
   """
   e = d['Element']
   splitElement = e.split("@@")
   d['FileName'] = splitElement[0]
   d['StreamName'] = splitElement[1]
   # StreamName starts with /main/ which we aren't interested in.
   # Remove the /main/ (slice on 5 because there are 5 chars in /main/)
   d['StreamName'] = d['StreamName'][5:]

   # When the operations is a checkin (which is the only operation this script is interested in)
   # then the stream names ends with a version number /x.
   # Assumption: When the version is /1 it means the checkin just added content to a new file
   # as such mark the element as created.
   # Note: I have noticed some logs that have a double set of @@ in them, don't know why that 
   # happens but if it does we will get the wrong version number here. The stream name maybe wrong also.
   matchObj = re.search(r'\d+$', d['StreamName'])   
   
   if matchObj:
       # Stream ends with a version number to split it
       d['Version'] = matchObj.group()
       # Plus one on the version string because need to get rid of the trailing /
       d['StreamName'] = d['StreamName'][:-(len(d['Version']) + 1)]
   else:
       d['Version'] = None

def processLineIntoTuple(line):
   """Take the line and split it out into a dictionary"""
   d = {}
   for i in line.split("|"):
      l = i.split(":",1)
      if (len(l)) == 2:
         d[l[0].strip()] = l[1].strip()
      else:
         d[l[0].strip()] = ""

 

   return d

def processOperationType(d):
    """
       Take the entry and determine what the operation type for gource should be (A, M, D)
    """
    # A Checkin of a version 1 on a stream is assumed to add the file to that stream
    if d['Version'] == "1":
        d['OperationType'] = "A"
    else:
        d['OperationType'] = "M"

    return d

def UseThis(d):
   try:
      if d['OperationKind'] != "checkin":
         return 0
      if d['Object'] not in fileTypesWeCareAbout:
         return 0
   except:
      return 0

   return 1

def printInGourceFormat(d):
   """
      Output the dictionary in gourse format. Assumed to be a line that we are interested in.
      Fundamentally this is a line that has a checkin on it
   """
   print '%d|%s|%s|%s%s' % (d['Date'], d['User'], d['OperationType'], d['StreamName'], d['FileName'])


for x in sys.stdin.readlines():
   d = processLineIntoTuple(x)
   if UseThis(d):
      d['Date'] = processDate(d['Date'])
      processElement(d)
      processOperationType(d)
      printInGourceFormat(d)

