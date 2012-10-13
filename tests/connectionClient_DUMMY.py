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
import connectionFunctions as cf
from baseUtils import getConfigParameters

def main(p, event, bbox=None, tag=None, people=None, mediaOnly=None):
    ''' Coordinates a new twitter stream connection'''

    if tag:
        tag = [tag]

    # Build an appropriate bounding box
    bbox = cf.buildBoundingBox(bbox)
    # track=tag, follow=people, 
    
    try:
        with tweetstream.FilterStream(p.sourceUser, p.sourcePassword, locations=bbox) as stream:
            for tweet in stream:
                
                # If we're only after those with media in
                if mediaOnly:
                    entities = tweet['entities']
                    
                    # If the tweet contains media
                    if entities.has_key('media'):
                        mediaOut = cf.processMedia(tweet)
                        mediaOut['objectId'] = event
                    else:
                        continue
                
                # Dump the tweet to a string for the jms
                try:
                    tweet = json.dumps(mediaOut, ensure_ascii=True)
                except Exception, e:
                    print 'FAILED to dump out'
                    print e
                    continue
            
                try:
                    success = cf.postTweet(tweet)
                except Exception, e:
                    print e
                    print success
            
    except tweetstream.ConnectionError, e:
        print "Disconnected from twitter. Reason:\n", e.reason
    

#------------------------------------------------------------------------------------------ 

if __name__ == '__main__':
    
    # Command Line Options
    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', dest='config',    help='The absolute path to the config file')
    parser.add_option('-o', '--event',    dest='eventId', help='The event that kicked off the interest.')
    
    parser.add_option('-t', '--tag',    dest='tag',    help='the tag to make up the stream filter.')
    parser.add_option('-n', '--north',  dest='n',  help='NORTH of the geographic bbox')
    parser.add_option('-s', '--south',  dest='s',  help='SOUTH of the geographic bbox')
    parser.add_option('-e', '--east',   dest='e',   help='EAST of the geographic bbox')
    parser.add_option('-w', '--west',   dest='w',   help='WEST of the geographic bbox')
    parser.add_option('-m', '--media_only', dest='media', action='store_true', help='true if only want media tweets.')
    (opts, args) = parser.parse_args()

    # Check for the config file
    if not opts.config or not opts.eventId:
        print "Must provide a config file location and an object id. \n"
        parser.print_help()
        exit(-1)
    
    # Check for the bbox
    if not opts.n and not opts.s and not opts.e and not opts.w and not opts.tag:
        print "Must provide either tag or -n & s & e & w \n"
        parser.print_help()
        exit(-1)    
    else:
        bbox = {'n':opts.n,'s':opts.s,'e':opts.e,'w':opts.w}

    #Config File Parameters
    logging.basicConfig()
    p = getConfigParameters(opts.config)
    
    x = True
    while x == True:
        pass
    
    #main(p, event=opts.eventId, tag=opts.tag, bbox=bbox, mediaOnly=opts.media)

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

