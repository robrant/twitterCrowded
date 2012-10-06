import os
import sys
import logging
import datetime

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


import tweetstream
# Custom libs
import mdb
from parameterUtils import getConfigParameters
import json
import time
from datetime import datetime

#------------------------------------------------------------------------------------------ 

def setup(params):

    # Instantiate the mongo connection for this client
    c, dbh = mdb.getHandle(params.dbHost, params.dbPort, params.db)
    collHandle = dbh[params.collection]

    # Authentication
    try:
        auth = dbh.authenticate(params.dbUser, params.dbPassword)
    except Exception, e:
        print "Failed to authenticate with mongo db."
        print e

    return c, dbh, collHandle

#------------------------------------------------------------------------------------------ 

def tweetStream(params):
    ''' Handles the streaming feed '''
    
    x = 0

    # A variable that switches if connection is down for > x seconds
    recentlyConnected = True
    
    try:
        with tweetstream.FilterStream(params.sourceUser, params.sourcePassword, locations=params.bbox) as stream:
    
            for tweetIn in stream:
                
                # stream.connected == True while in the iter()
                
                # Dump the tweet to a string for the jms
                try:
                    tweet = json.dumps(tweetIn, ensure_ascii=True)
                except:
                    print 'FAILED'
                    print tweetIn
                    continue
                            
                jms.sendData(params.jmsDest, tweet, x)        
    
    except tweetstream.ConnectionError, e:
        print "Disconnected from twitter. Reason:\n", e.reason

#------------------------------------------------------------------------------------------ 
       
# we initialise the logger to log to the console
logging.basicConfig()

# first argument is the config file path
configFile = sys.argv[1]
#configFile = "/Users/brantinghamr/Documents/Code/eclipseWorkspace/getTwitter/config/consumeTweets.cfg"
    
# Get the config information into a single object
p = getConfigParameters(configFile)

# Select between 
#if p.backend == 'mongo':
#    c, dbh, collHandle = setup(p)

    #*** THIS ALL NEEDS CHECKING, BECAUSE THE AMQPHANDLER CLASS HASNT BEEN WRITTEN YET. ***

# Handle the tweets
tweetStream(p)

