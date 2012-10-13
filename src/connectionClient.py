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

import connectionFunctions as cf
from baseUtils import getConfigParameters
import mdb


#------------------------------------------------------------------------------------------

def main(p, mediaOnly=None):
    ''' Coordinates a new twitter stream connection'''
    
    # Connection placeholder in case the exception catches the drop out
    connection = True
    
    while connection==True:
    
        # The mongo bits
        try:
            c, dbh = mdb.getHandle(host=p.dbHost, port=p.dbPort, db=p.db, user=p.dbUser, password=p.dbPassword)
            evCollHandle = dbh[p.eventsCollection]    
        except:
            print "Failed to connect to mongo."
            sys.exit(1)
            
        # Get the existing tags and add the current
        tags = cf.getCurrentTags(evCollHandle)
    
        # Build the building boxes
        bboxes = cf.getCurrentBBoxes(evCollHandle)
        # track=tag, follow=people, 
        
        if not tags and not bboxes:
            sys.exit()
            
        # Here's the redis queue for managing the tweets as they come in
        try:
            q = RedisQueue(p.redisName, host=p.redisHost, password=p.redisPassword, port=p.redisPort, db=0)
        except:
            print "REDIS: Failed to connect in connectionClient.py. "
            sys.exit()
            
        try:
            print tags, bboxes
            with tweetstream.FilterStream(p.sourceUser, p.sourcePassword, track=tags, locations=bboxes) as stream:
                for tweet in stream:
                    #print '********************'   
                    #print tweet
                    #print '********************'   
                    # If we're only after those with media in
                    if mediaOnly:
                        
                        try:
                            q.put(json.dumps(tweet))
                        except:
                            print "Failed to put tweet on redis. This tweet:"
                            print tweet
                        
        except tweetstream.ConnectionError, e:
            print "Disconnected from twitter. Reason:\n", e.reason

#------------------------------------------------------------------------------------------ 

if __name__ == '__main__':
    
    # Command Line Options
    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', dest='config',    help='The absolute path to the config file')
    #parser.add_option('-o', '--event',    dest='eventId', help='The event that kicked off the interest.')
    
    #parser.add_option('-t', '--tag',    dest='tag',    help='the tag to make up the stream filter.')
    #parser.add_option('-g', '--geo',    dest='bbox',   action='store_true', help='the geographic bbox - see https://bitbucket.org/runeh/tweetstream/src')
    parser.add_option('-m', '--media_only', dest='media', action='store_true', help='true if only want media tweets.')
    (opts, args) = parser.parse_args()

    # Check for the config file
    if not opts.config:
        print "Must provide a config file location. \n"
        parser.print_help()
        exit(-1)
    
    # Check for the bbox
    """
    if not opts.bbox and not opts.tag:
        print "Must provide either tag or geospatial bounding box(es) \n"
        parser.print_help()
        exit(-1)
    elif opts.bbox:
        bbox = opts.bbox
        tag = None
    elif opts.tag:
        tag = opts.tag
        bbox = None
    """
    
    #Config File Parameters
    logging.basicConfig()
    p = getConfigParameters(opts.config)
        
    main(p, mediaOnly=opts.media)


"""
{"data":[{"standard_resolution" : "http://distilleryimage1.s3.amazonaws.com/8b74d2ee0e5611e2adc122000a1de653_7.jpg",
          "low_resolution" : "http://distilleryimage1.s3.amazonaws.com/8b74d2ee0e5611e2adc122000a1de653_6.jpg",
           "source" : "instagram",
           "dt" : "2012-10-04T19:06:04Z",
           "caption" : "This actually worked as a POST",
           "thumbnail" : "http://distilleryimage1.s3.amazonaws.com/8b74d2ee0e5611e2adc122000a1de653_5.jpg",
           "objectId" : "snorty",
           "tags" : ["hello world", "foo", "bar"]}]}
"""

