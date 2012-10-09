'''
Performs the following functions:

GOING TO BE CRONNED

1. Requests all events from crowded
    - url get results
    - check against existing mongodb = new event, old events
    - handle new events - kick off connectionClient
      - get back server process ID
      - add that to the mongo doc
    - handle old events
      - subProcess.pOpen(kill process ID associated with this)

2. Mods to connectionClient
    - Handle different types of stream filter
    - Optional post-filter for has_key('media_url')
    - Get entites/hashtags from media
    - Call POSTer

3. Build correctly formatted JSON for POST - returns JSON

4. Submit the post and check for good response ({data:[]}) = 0 or 1

5. 
  
'''
import os
import sys
import urllib2
import json
import subprocess
import time
#============================================================================================
# TO ENSURE ALL OF THE FILES CAN SEE ONE ANOTHER.

# Get the directory in which this was executed (current working dir)
cwd = os.getcwd()
wsDir = os.path.dirname(cwd)

# Find out whats in this directory recursively
for root, subFolders, files in os.walk(wsDir):
    # Loop the folders listed in this directory
    for folder in subFolders:
        directory = os.path.join(root, folder)
        if directory.find('.git') == -1:
            if directory not in sys.path:
                sys.path.append(directory)

#===============================================================================
import mdb
from baseUtils import getConfigParameters


def getCrowdedEvents(p, ef):
    ''' Retrieves the currently active events in crowded '''
    
    try:
        req = urllib2.Request(p.crowdedEventsUrl)
        response = urllib2.urlopen(req).read()
    except Exception, e:
        ef.write("Failed to open Crowded events list url")
    
    try:
        events = json.loads(response)
    except:
        events = None
        
    if events.has_key('data'):
        events = events['data']
    return events

#----------------------------------------------------------------------

def getLocalEvents(p, evCollHandle):
    ''' Retrieves the active events stored by this app. '''
    
    # The query into mongo that should only return 1 doc
    res = evCollHandle.find()
    
    try:
        docs = [d for d in res]
    except:
        print "No active events in this app."
        docs = None

    return docs
    
#----------------------------------------------------------------------

def checkEvents(crowded, local):
    ''' Compares crowded and my events. '''
    
    # Format the crowded events into list of objectIds - inEvents
    crowdedEvents = {}
    for ev in crowded:
        crowdedEvents[ev['objectId']] = ev 
    
    # Format my events into list of objectIds - inEvents
    localEvents = {}
    for ev in local:
        localEvents[ev['objectId']] = ev 
    
    # Get newEvents
    oldEventIds = list(set(localEvents.keys()) - set(crowdedEvents.keys()))
    oldEvents = [localEvents[oe] for oe in oldEventIds]
    
    # Get newEvents
    newEventIds = list(set(crowdedEvents.keys()) - set(localEvents.keys()))
    newEvents = [crowdedEvents[ne] for ne in newEventIds]

    return oldEvents, newEvents

#----------------------------------------------------------------------

def formatBBox(bbox):
    ''' Formats the bounding box into n/s/e/w '''
        
    #Example: [[-0.15086429372878282, 51.504755706271219], [-0.10658170627121719, 51.549038293728778]]
    n = bbox[1][1]
    s = bbox[0][1]
    e = bbox[1][0]
    w = bbox[0][0]
    
    return n, s, e, w
    
#----------------------------------------------------------------------

def processNewEvent(p, newEvent):
    ''' Establishes a new stream for this event. '''
    
    # Build the command and arguments    
    command = [p.python, p.streamClient, '-c', p.configFile, '-m', '-o', str(newEvent['objectId'])]
    
    # Extract geo or tag info from the newEvent
    if newEvent['subType'] == 'tag':
        command += ["-t", str(newEvent['objectId'])]
        
    elif newEvent['subType'] == 'geography':
        n,s,e,w = formatBBox(newEvent["bbox"])
        command += ['-n',str(n),'-s',str(s),'-e',str(e),'-w',str(w)]
    
    # Make a call to POpen passing in the filter param
    process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE)
    
    # Get the linux process id (pid) 
    return process.pid
        
#----------------------------------------------------------------------

def createLocalEvent(evCollHandle, event, processId):
    ''' Updates the mongo document with server process Id for later kill. '''
    
    # Add the process id to the existing document
    event['pid'] = processId
    try:
        res = evCollHandle.insert(event)
    except:
        res = "Failed to insert the event:\n%s" %event

    return res

#----------------------------------------------------------------------

def expireOldEvent(evCollHandle, oldEvent):
    ''' Kills the oldEvent, no longer being monitored in crowded. '''

    # Uses the document id to get the server process ID
    filter = {'objectId': oldEvent['objectId']}
    
    # Use the document id to get the PID for the connectionClient for this stream
    try:
        res = evCollHandle.find_one(filter, fields=['pid'])
        pid = res['pid']
    except:
        pid = None
        
    # Uses the process ID to kill the process
    if pid:
        process = subprocess.Popen(['kill', '-9', str(pid)], shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        removePidOut = process.communicate()
        
        # Remove the document from mongo
        try:
            evCollHandle.remove(filter)
            res = None 
        except Exception, e:
            print 'Exception: %s' %e
            res = "Failed to remove the old object, id: %s" %oldEvent['objectId']
    else:
        res = "Failed to get server PID for the old event:\n%s" %oldEvent
        
    return res

#----------------------------------------------------------------------

def main(configFile=None):
    ''' Coordinates the management functions
        Command line called, typically from a CRON.'''

    # Get the config file
    cwd = os.getcwd()
    parent = os.path.dirname(cwd)
    p = getConfigParameters(configFile)
    
    errorFile = os.path.join(p.errorPath, p.errorFile)
    ef = open(errorFile, 'a')
    
    # Streaming client
    p.streamClient = os.path.join(parent, 'src/connectionClient.py')

    # The mongo bits
    try:
        c, dbh = mdb.getHandle(host=p.dbHost, port=p.dbPort, db=p.db, user=p.dbUser, password=p.dbPassword)
        evCollHandle = dbh[p.eventsCollection]    
    except:
        ef.write("Failed to get mongo connection and Event Collection Handle.")
        sys.exit(1)
        
    # Get the current events from crowded
    crowdedEvents = getCrowdedEvents(p, ef)
    if not crowdedEvents:
        ef.write("Failed to get events list from crowded.")
        
    # Get the events currently stored by this app
    myEvents = getLocalEvents(p, evCollHandle)
    if not myEvents:
        ef.write("Failed to get events list from crowded.")

    # Compare the 2 sets of events: what's old and new?
    oldEvents, newEvents = checkEvents(crowdedEvents, myEvents)

    # Create new ones + setup conectionclient
    for newEvent in newEvents:
        pid = processNewEvent(p, newEvent)
        res = createLocalEvent(evCollHandle, newEvent, pid)
        if res: ef.write("Creating Local Event:\n%s" %res)
        
    # Expire old events from db + kill the connectionClient pid  
    for oldEvent in oldEvents:
        res = expireOldEvent(evCollHandle, oldEvent)
        if res: ef.write("Creating Local Event: %s" %res)

    mdb.close(c, dbh)
    ef.close()
    
    
if __name__ == "__main__":

    # Command Line arguments
    try:
        configFile = sys.argv[1]
    except:
        print; print "*"*68
        print 'Provide the full path to a config file as the sole argument. Exiting.'
        print "*"*68; print
        sys.exit(1)
    
    main(configFile)