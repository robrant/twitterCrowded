'''
Created on Sep 6, 2012

@author: brantinghamr
'''
import unittest
import os
import sys
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

#============================================================================================
import connectionFunctions as cf
from baseUtils import getConfigParameters
import datetime
from random import randint

class Test(unittest.TestCase):
    
    """
    def testGetDatetime(self):
        ''' Check the getDatetime function works.'''
        
        truthDatetime = '2012-10-06T19:38:50'
        testDatetime  = {'created_at':'Sat Oct 06 19:38:50 +0000 2012'}
        dt = cf.getDatetime(testDatetime)
        
        self.assertEquals(dt, truthDatetime)


    def testGetTags(self):
        ''' Check the getTags function works.'''
        
        truthTags = ['xfactor', 'dull']
        hashtags = [{u'indices': [0, 8], u'text': u'xfactor'},
                     {u'indices': [0, 8], u'text': u'dull'}]
        hashtags  = cf.getTags(hashtags)
        
        self.assertEquals(hashtags, truthTags)
        

    def testgetMedia(self):
        ''' Check the getMedia function.'''
        
        mediaDoc = [{"source_status_id_str": "254658040798773249",
                     "expanded_url": "http://twitter.com/HarrisonSmithDJ/status/254658040798773249/photo/1",
                     "display_url": "pic.twitter.com/ETcWJFLI",
                     "source_status_id": 254658040798773249,
                     "media_url_https": "https://p.twimg.com/A4i6I41CAAA0OFE.jpg",
                     "url": "http://t.co/ETcWJFLI",
                     "id_str": "254658040802967552",
                     "sizes": {"large": {"h": 640, "w": 960, "resize": "fit"},
                               "small": {"h": 227, "w": 340, "resize": "fit"},
                               "medium": {"h": 400, "w": 600, "resize": "fit"},
                               "thumb": {"h": 150, "w": 150, "resize": "crop"}},
                     "indices": [52, 72],
                     "type":"photo",
                     "id": 254658040802967552,
                     "media_url":"http://p.twimg.com/A4i6I41CAAA0OFE.jpg"}]
        
        thumbUrl, lowUrl, stdUrl = cf.getMedia(mediaDoc)
        self.assertEquals(thumbUrl, "http://p.twimg.com/A4i6I41CAAA0OFE.jpg:thumb")
        self.assertEquals(lowUrl,   "http://p.twimg.com/A4i6I41CAAA0OFE.jpg:small")
        self.assertEquals(stdUrl,   "http://p.twimg.com/A4i6I41CAAA0OFE.jpg:medium")
        

    def testbuildBoundingBox(self):
        ''' Check the ability build a bounding box function.'''
        
        truth = ['-12.0,49.0', '3.0,60.0']
        inCardinals = {'n':60.0,'s':49.0,'e':3.0,'w':-12.0}
        bb = cf.buildBoundingBox(inCardinals)
        self.assertEquals(bb, truth)
        
    def testprocessMedia(self):
        '''Full tweet test'''
        
        cwd = os.getcwd()
        sample = os.path.join(cwd, 'sampleTweet.json')
        data = open(sample, 'r')
        tweet = json.loads(data.read())
        mediaOut = cf.processMedia(tweet)
        
        self.assertEquals(mediaOut['data'][0]['caption'], 'Ah, lovely stuff - cocktails with @grainy47 http://t.co/lw4JSCHJ')
        self.assertEquals(mediaOut['data'][0]['dt'], '2012-10-06T19:38:44')
    """
        
    def testpostTweet(self):
        '''Tweet post test'''

        python = '/Library/Frameworks/Python.framework/Versions/2.6/bin/python'

        cwd = os.getcwd()
        parent = os.path.dirname(cwd)
        cfgs = os.path.join(parent, 'config/twitterCrowded.cfg')
        p = getConfigParameters(cfgs)

        server = os.path.join(cwd, 'testWebServer.py')
        process = subprocess.Popen([python, server, '&'], shell=False, stdout=subprocess.PIPE)
        pid = process.pid
        print pid
        time.sleep(2)
        
        # Change the POST url
        p.POSTurl = 'http://localhost:8991/contribute'
        
        data = {"data":[{"standard_resolution" : "http://distilleryimage3.s3.amazonaws.com/9b3dc7c00dcb11e2876222000a1fbcf1_7.jpg",
                        "low_resolution" : "http://distilleryimage3.s3.amazonaws.com/9b3dc7c00dcb11e2876222000a1fbcf1_6.jpg",
                        "source" : "instagram",
                        "dt" : "2012-10-04T19:06:04Z",
                        "caption" : "This actually worked as a POST",
                        "thumbnail" : "http://distilleryimage3.s3.amazonaws.com/9b3dc7c00dcb11e2876222000a1fbcf1_5.jpg",
                        "objectId" : "snorty",
                        "tags":["helloworld","foo","bar"]}]}
        
        response = cf.postTweet(p, data)
        outData = json.loads(response)
        self.assertEquals(outData, data['data'][0])
        
        process = subprocess.Popen(['kill', '-9', str(pid)], shell=False, stdout=subprocess.PIPE)
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGetTopTags']
    unittest.main()