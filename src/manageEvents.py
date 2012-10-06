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

3. Build correctly formatted JSON for POST - returns JSON

4. Submit the post and check for good response ({data:[]}) = 0 or 1


  
'''

def getCrowdedEvents(p):
    ''' Retrieves the currently active events in crowded '''
    
    
    
    return events
    
#----------------------------------------------------------------------

def checkEvents(p, collHandle, events):
    ''' Retrieves the currently active events in crowded '''
    
    # Format the inEvents into list of objectIds - inEvents
    
    # Query mongo for all events and get objectIds into list - mnEvents
    
    # Get newEvents
    oldEventIds = list(set(mnEvents.keys()) - set(inEvents.keys()))
    oldEvents = [mnEvents[oe] for oe in oldEventIds]
    
    # Get newEvents
    newEventIds = list(set(inEvents.keys()) - set(mnEvents.keys()))
    newEvents = [inEvents[ne] for ne in newEventIds]

    
    return oldEvents, newEvents
    
#----------------------------------------------------------------------

def processNewEvent(p, collHandle, newEvent):
    ''' Establishes a new stream for this event. '''
    
    # Extract geo or tag info from the newEvent
    
    # Make a call to POpen passing in the filter param
    
    # Record and return the processId
    
    return processId
    
#----------------------------------------------------------------------

def updateEvents(p, collHandle, objectId, processId):
    ''' Updates the mongo document with the server process Id
        for later killing. '''
    
    # Uses the object Id to upsert the processId to the doc
    
    return success

#----------------------------------------------------------------------

def expireOldEvent(p, collHandle, oldEvent):
    ''' Kills the oldEvent, no longer being monitored in crowded. '''

    # Uses the document id to get the server process ID
    
    # Use the document id to remove the document from the collection
    
    # Uses the process ID to kill the process
    
    return success

#----------------------------------------------------------------------

if __name__ == '__main__':
    pass
    #main()