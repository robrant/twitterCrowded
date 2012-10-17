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
import logging
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


def getCrowdedEvents(p):
    ''' Retrieves the currently active events in crowded '''
    
    try:
        print p.crowdedEventsUrl
        req = urllib2.Request(p.crowdedEventsUrl)
        response = urllib2.urlopen(req).read()
    except:
        response = None
        logging.error("Failed to retrieve Crowded events list from url: %s" %(p.crowdedEventsUrl), exc_info=True)

    
    try:
        events = json.loads(response)
    except:
        logging.error("Failed to load events", exc_info=True)
        events = None
        
    if events.has_key('data'):
        events = events['data']
        
    return events

#----------------------------------------------------------------------

def getLocalEvents(p, evCollHandle):
    ''' Retrieves the active events stored by this app. '''
    
    # The query into mongo that should only return 1 doc
    res = evCollHandle.find()
    if res:
        try:
            docs = [d for d in res]
        except:
            logging.warning("Failed to get local events.", exc_info=True)
            docs = None
    else:
        docs = None
        
    return docs
    
#----------------------------------------------------------------------

def checkEvents(crowded, local):
    ''' Compares crowded and my events. '''
    
    # Format the crowded events into list of objectIds - inEvents
    crowdedEvents = {}
    try:
        for ev in crowded:
            crowdedEvents[ev['objectId']] = ev 
    except:
        pass
    # Format my events into list of objectIds - inEvents
    localEvents = {}
    try:
        for ev in local:
            localEvents[ev['objectId']] = ev 
    except:
        pass    

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
    
def killOldProcess(pid):
    ''' Kill off the old process'''

    # Build the command and arguments    
    command = ['kill', '-9', str(pid)]
    # Make a call to POpen passing in the filter param
    process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE)
    
    return process.pid
    
#----------------------------------------------------------------------

def processNewEvent(p):
    ''' Establishes a new stream for this event. '''
    
    # Build the command and arguments    
    command = [p.python, p.streamClient, '-c', p.configFile, '-m', '&']
    
    # Make a call to POpen passing in the filter param
    process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE)
    
    # Get the linux process id (pid) 
    return process.pid
        
#----------------------------------------------------------------------

def createLocalEvent(evCollHandle, event):
    ''' Initial insert of the document '''
    
    try:
        res = evCollHandle.insert(event)
    except:
        logging.warning("Failed to insert the event:\n%s" %event, exc_info=True)
        res = None 

    return res
#----------------------------------------------------------------------

def getPid(mgmtCollHandle):
    ''' Gets the PID from the mongo management collection. '''

    # Add the process id to the existing document
    query = {'function':'twitterClientPid'}
    fields = ['pid']
    try:
        doc = mgmtCollHandle.find_one(query, fields)
        pid = doc['pid']
        
    except:
        logging.warning("Failed to UPDATE the PID for twitter Client", exc_info=True)
        pid = None
        
    return pid

#----------------------------------------------------------------------

def setInitialPid(mgmtCollHandle):
    ''' Set the initial PID'''
    
    logging.debug('Setting the initial PID')

    # Add the process id to the existing document
    query = {'function':'twitterClientPid'}
    try:
        res = mgmtCollHandle.find_one(query)
    except:
        res = None
    
    if not res or len(res) == 0:
        query['pid'] = None
        insRes = mgmtCollHandle.insert(query)
        logging.debug('Creating a placeholder PID document.')

    else:
        insRes = None
        
    return insRes    

#----------------------------------------------------------------------

def storePid(mgmtCollHandle, processId):
    ''' Updates the mongo document with server process Id for later kill. '''

    # Add the process id to the existing document
    query = {'function':'twitterClientPid'}
    update = {'$set':{'pid':processId}}
    try:
        res = mgmtCollHandle.update(query, update, upsert=True)
        logging.debug('Successfully updated the PID in mgmt collection.')
        res = processId
    except:
        logging.warning('Failed to update the PID in mgmt collection', exc_info=True)
        res = None
        
    return res


#----------------------------------------------------------------------

def expireOldEvent(evCollHandle, oldEvent):
    ''' Kills the oldEvent, no longer being monitored in crowded. '''

    # Uses the document id to get the server process ID
    filter = {'objectId': oldEvent['objectId']}
    
    # Remove the document from mongo
    try:
        evCollHandle.remove(filter)
        res = None 
    except:
        logging.warning("Failed to remove the old object, id: %s" %oldEvent['objectId'])
        
    return res

#----------------------------------------------------------------------

def killCurrentProcess(mgmtCollHandle, pid):

    # Use the document id to get the PID for the connectionClient for this stream
    try:
        res = mgmtCollHandle.find_one(filter, fields=['pid'])
        pid = res['pid']
    except:
        logging.warning("Failed to get the current PID from mgmt collection.", exc_info=True)
        pid = None
        
    # Uses the process ID to kill the process
    if pid:
        process = subprocess.Popen(['kill', '-9', str(pid)], shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        removePidOut = process.communicate()

#---------------------------------------------------------------------- 

def main(configFile=None):
    ''' Coordinates the management functions
        Command line called, typically from a CRON.'''

    # Get the config file
    p = getConfigParameters(configFile)
    
    # Logging config
    logFile = os.path.join(p.errorPath, p.errorFile)
    logging.basicConfig(filename=logFile, format='%(levelname)s:: \t%(asctime)s %(message)s', level=p.logLevel)

    # Streaming client
    connClientPath = os.path.dirname(p.errorPath)
    p.streamClient = os.path.join(connClientPath, 'src/connectionClient.py')

    # The mongo bits
    try:
        c, dbh = mdb.getHandle(host=p.dbHost, port=p.dbPort, db=p.db, user=p.dbUser, password=p.dbPassword)
        evCollHandle = dbh[p.eventsCollection]  
        mgmtCollHandle = dbh[p.mgmtCollection]
        logging.debug("Connected and authenticated on the db.")
    except:
        logging.critical('Failed to connect to db and authenticate.', exc_info=True)
        sys.exit()
            
    # Create a new management document if needed
    initialOID = setInitialPid(mgmtCollHandle)
    
    # Get the current events from crowded
    crowdedEvents = getCrowdedEvents(p)
        
    # Get the events currently stored by this app
    myEvents = getLocalEvents(p, evCollHandle)

    # Compare the 2 sets of events: what's old and new?
    oldEvents, newEvents = checkEvents(crowdedEvents, myEvents)
    
    # Expire old events from db, so that the new stream reflects the correct interest  
    for oldEvent in oldEvents:
        print oldEvent
        logging.debug('Expiring Old Event in DB: %s' %(oldEvent))
        res = expireOldEvent(evCollHandle, oldEvent)
        
    # Create new item in the db
    for newEvent in newEvents:
        logging.debug('Creating New Event in DB: %s' %(newEvent))
        res = createLocalEvent(evCollHandle, newEvent)
    
    # Get the old process ID and kill it off
    pid = getPid(mgmtCollHandle)
    logging.debug('Current PID: %s' %(pid))

    # Only continue if there is a change in the events    
    if len(oldEvents) > 0 or len(newEvents) > 0:
        
        if pid:
            logging.debug('Killing old process with ID: %s' %(pid))
            res = killOldProcess(pid)
    
        # Now create the new one
        newPid = processNewEvent(p)
        logging.debug('Creating a new process with PID: %s' %(newPid))
        
        # Update the current process id in mongo
        res = storePid(mgmtCollHandle, newPid)
        logging.debug('Stored the new PID: %s' %(res))
        
    mdb.close(c, dbh)
    logging.shutdown()
    
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