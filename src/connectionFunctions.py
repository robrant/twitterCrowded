import os
import sys
import datetime
import json
import urllib2
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
#FOSS Lib
import tweetstream
# Custom libs
from baseUtils import getConfigParameters, decodeEncode

#------------------------------------------------------------------------------------------ 

def getDatetime(tweet):
    '''Get the datetime information out '''
    
    try:
        timeStamp = tweet['created_at']
        ts = datetime.datetime.strptime(timeStamp, '%a %b %d %H:%M:%S +0000 %Y')
    except Exception, e:
        print "Failed to parse 'created_at' into datetime object."
        print e
        ts = datetime.datetime.utcnow()

    if ts:
        ts = ts.isoformat()
        
    return ts
    
#------------------------------------------------------------------------------------------ 
    
def getTags(hashtags):
    ''' Gets all of the hashtags out into a list'''
    
    tags = [ht['text'] for ht in hashtags]
    
    return tags

#------------------------------------------------------------------------------------------ 

def getMedia(mediaDoc):
    ''' Gets the media urls. Only taking the first image. '''
    
    # Get the base URL
    baseUrl = mediaDoc[0]['media_url']
    
    # Get the various sizes
    thumb    = "%s:thumb" %baseUrl
    low      = "%s:small" %baseUrl
    standard = "%s:medium" %baseUrl
    
    return thumb, low, standard
    
    
#------------------------------------------------------------------------------------------ 

def buildBoundingBox(cardinals):
    ''' Builds the bounding box for the twitter format.'''

    sw = "%s,%s" %(cardinals['w'],cardinals['s'])
    ne = "%s,%s" %(cardinals['e'],cardinals['n'])
    bbox = [sw, ne]
    return bbox

#------------------------------------------------------------------------------------------ 

def processMedia(objectId, tweet):
    '''Handles the formatting of the tweet media to be compatible with crowded.'''
    
    try:
        entities = tweet['entities']
    except:
        return None
    
    #Get the media
    thumbUrl, lowUrl, stdUrl = getMedia(entities['media'])
    
    # Get the tags
    if entities.has_key('hashtags'):
        hashtags = getTags(entities['hashtags'])
    
    # Get the tweet
    try:
        caption = decodeEncode(tweet['text'])
    except:
        caption = '***caption not parsed***'
    
    # Get the datetime out as ISO
    dt = getDatetime(tweet)
        
    # Kludge them together
    mediaTweet = {'standard_resolution' : stdUrl,
                  'low_resolution'      : lowUrl,
                  'thumbnail'           : thumbUrl,
                  'dt'                  : dt,
                  'source'              : 'twitter',
                  'caption'             : caption,
                  'tags'                : hashtags, 
                  'objectId'            : str(objectId)}
    
    tweetOut = {'data':[mediaTweet]}

    return tweetOut

#------------------------------------------------------------------------------------------ 

def postTweet(p, mediaTweet):
    ''' POST the media json object to the URL.'''
    
    errors = []

    try:
        req = urllib2.Request(p.POSTurl, mediaTweet, {'Content-Type': 'application/json'})
        f = urllib2.urlopen(req)
        response = f.read()
    except:
        errors.append('Failed to POST json content to URL.')

    if len(errors) > 1:
        return errors
    else:
        return response
