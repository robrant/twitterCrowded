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

#------------------------------------------------------------------------------------------

def main(p, event, bbox=None, tag=None, people=None, mediaOnly=None):
    ''' Coordinates a new twitter stream connection'''

    cwd = os.getcwd()
    parent = os.path.dirname(cwd)
    logFile = os.path.join(parent, 'tweets_id_%s.out' %(event))
    tFile = open(logFile, 'a')

    if tag:
        tag = [tag]

    # Build an appropriate bounding box
    elif bbox:
        bbox = cf.buildBoundingBox(bbox)
    # track=tag, follow=people, 
    
    tFile.write("Media Only %s" %mediaOnly)
    
    try:
        with tweetstream.FilterStream(p.sourceUser, p.sourcePassword, track=tag, locations=bbox) as stream:
            for tweet in stream:
                
                tFile.write("*"*80+"\n")
                txt = "1. %s  :  %s \n" %(tweet['created_at'], tweet['text'])
                tFile.write(json.dumps(txt, ensure_ascii=True))
                try:
                    txt = "2. %s  \n" %(tweet['entities'])
                    tFile.write(json.dumps(txt, ensure_ascii=True))
                except:
                    continue

                # If we're only after those with media in
                if mediaOnly:
                    try:
                        entities = tweet['entities']
                    except:
                        continue
                    # If the tweet contains media
                    if entities.has_key('media') == True:
                        mediaOut = cf.processMedia(event, tweet)

                        # Dump the tweet to a string for the jms
                        try:
                            tweet = json.dumps(mediaOut, ensure_ascii=True)
                            #tFile.write("4. Media Event Making it Through"+"\n")
                        except Exception, e:
                            continue
                    
                        try:
                            success = cf.postTweet(p, tweet)
                            tFile.write("5. Media Event Being Posted: %s\n" %success)
                        except Exception, e:
                            tFile.write("5. Media Failed POST\n")
                    else:
                        continue
                    
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
    elif opts.n and opts.s and opts.e and opts.w:
        bbox = {'n':opts.n,'s':opts.s,'e':opts.e,'w':opts.w}
        tag = None
    elif opts.tag:
        tag = opts.tag
        bbox = None

    #Config File Parameters
    logging.basicConfig()
    p = getConfigParameters(opts.config)
        
    main(p, event=opts.eventId, tag=tag, bbox=bbox, mediaOnly=opts.media)

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

