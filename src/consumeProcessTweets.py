import os
import sys
import json

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

#============================================================================================
from redisQueue import RedisQueue

import connectionFunctions as cf
from baseUtils import getConfigParameters
import mdb


def dispatchTweet(p, tweet, objectId):
    ''' Takes the tweet from the options in main and dispatches it'''
    
    try:
        entities = tweet['entities']
    except:
        return None
    
    # If the tweet contains media
    if entities.has_key('media') == True:
        mediaOut = cf.processMedia(objectId, tweet)
    
        # Dump the tweet to a string for the jms
        try:
            tweet = json.dumps(mediaOut, ensure_ascii=True)
            success = 1
            #tFile.write("4. Media Event Making it Through"+"\n")
        except Exception, e:
            success = None 
    
        try:
            success = cf.postTweet(p, tweet)
            success = 1
            #tFile.write("5. Media Event Being Posted: %s\n" %success)
        except Exception, e:
            print e
            success = None
            #tFile.write("5. Media Failed POST\n")
    else:
        success = -1
        
    return success

#------------------------------------------------------------------------------------------

def main(p):

    # The mongo bits
    try:
        c, dbh = mdb.getHandle(host=p.dbHost, port=p.dbPort, db=p.db, user=p.dbUser, password=p.dbPassword)
        evCollHandle = dbh[p.eventsCollection]    
    except:
        print "Failed to connect to mongo."
        sys.exit(1)

    # Get the current tags 
    tags = cf.getCurrentTags(evCollHandle)
    # Get the current bounding boxes
    queryBBoxes = cf.getQueryBBox(evCollHandle)
    
    x = 1
    while x == 1:
        
        # Here's the redis queue for managing the tweets as they come in
        try:
            q = RedisQueue(p.redisName, host=p.redisHost, password=p.redisPassword, port=p.redisPort, db=0)
        except:
            print "REDIS: Failed to connect in connectionClient.py. "
            sys.exit()
        
        # This call is blocking, so expect it to hang on this point
        tweetStr = q.get()
        tweet = json.loads(tweetStr)
        
        # Work out which object/event this tweet is associated with
        if tags:
            tweetTags = cf.whichTags(tags, tweet)
            for tweetTag in tweetTags:
                success = dispatchTweet(p, tweet, tweetTag)
                print 'tag success:', success
        if queryBBoxes:
            tweetGeos = cf.matchesCurrentGeos(queryBBoxes, tweet)
            for tweetGeo in tweetGeos:
                success = dispatchTweet(p, tweet, tweetGeo)
                print 'geo success:', success
#--------------------------------------------------------------------------------

if __name__ == "__main__":
    
    configFile = sys.argv[1]
    
    # first argument is the config file path
    if not configFile:
        print 'no Config file provided. Exiting.'
        sys.exit()
    else:
        # Get the config information into a single object
        p = getConfigParameters(configFile)
    
    main(p)
