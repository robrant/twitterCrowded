import os
import sys
import logging
import datetime
import json
import optparse

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
from redisQueue import RedisQueue
#from qr import Queue

import connectionFunctions as cf
from baseUtils import getConfigParameters
import mdb


#------------------------------------------------------------------------------------------

def main(p, mediaOnly=None):
    ''' Coordinates a new twitter stream connection'''
    
    # Logging config
    logFile = os.path.join(p.errorPath, p.connErrorFile)
    logging.basicConfig(filename=logFile, format='%(levelname)s:: %(asctime)s %(message)s', level=p.logLevel)

    # The mongo bits
    try:
        c, dbh = mdb.getHandle(host=p.dbHost, port=p.dbPort, db=p.db, user=p.dbUser, password=p.dbPassword)
        evCollHandle = dbh[p.eventsCollection]    
    except:
        logging.critical('Failed to connect to db and authenticate.', exc_info=True)
        sys.exit()

    # Here's the redis queue for managing the tweets as they come in
    try:
        q = RedisQueue(p.redisName, host=p.redisHost, password=p.redisPassword, port=p.redisPort, db=0)
    except:
        logging.critical("REDIS: Failed to connect in connectionClient.py. ", exc_info=True)
        sys.exit()

    # Connection placeholder in case the exception catches the drop out
    connection = True
    
    while connection==True:
            
        # Get the existing tags and add the current
        try:
            tags = cf.getCurrentTags(evCollHandle)
        except:
            tags = None
            logging.error('Failed to get current tags from db.', exc_info=True)
            
        # Build the building boxes
        try:
            bboxes = cf.getCurrentBBoxes(evCollHandle)
        except:
            bboxes = None
            logging.error('Failed to get current BBOXes from db.', exc_info=True)
       
        if not tags and not bboxes:
            logging.warning('Currently no tags or bboxes in the db.')
            sys.exit()
            
        try:
            print tags, bboxes
            with tweetstream.FilterStream(p.sourceUser, p.sourcePassword, track=tags, locations=bboxes) as stream:
                for tweet in stream:
                    if mediaOnly:       
                        try:
                            q.put(json.dumps(tweet))
                        except:
                            logging.critical("Failed to put tweet on redis. This tweet: \n%s" %(tweet), exc_info=True)
                        
        except tweetstream.ConnectionError:
            logging.critical("Disconnected from twitter", exc_info=True)
            
#------------------------------------------------------------------------------------------ 

if __name__ == '__main__':
    
    # Command Line Options
    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', dest='config',    help='The absolute path to the config file')
    parser.add_option('-m', '--media_only', dest='media', action='store_true', help='true if only want media tweets.')
    (opts, args) = parser.parse_args()

    # Check for the config file
    if not opts.config:
        print "Must provide a config file location. \n"
        parser.print_help()
        exit(-1)
    
    #Config File Parameters
    p = getConfigParameters(opts.config)
        
    main(p, mediaOnly=opts.media)
    