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
import manageEvents as manEv
from baseUtils import getConfigParameters
import datetime

class Test(unittest.TestCase):
    
    
    """    
    def testGetCrowdedEvents(self):
        '''Tests successful retrieval of events.'''

        python = '/Library/Frameworks/Python.framework/Versions/2.6/bin/python'

        cwd = os.getcwd()
        parent = os.path.dirname(cwd)
        cfgs = os.path.join(parent, 'config/twitterCrowded.cfg')
        p = getConfigParameters(cfgs)

        # Standup a small bottle webserver which contains dummy function
        server = os.path.join(cwd, 'testWebServer.py')
        process = subprocess.Popen([python, server, '&'], shell=False, stdout=subprocess.PIPE)
        pid = process.pid
        print pid
        time.sleep(2)
        
        # Assign a localhost url
        p.crowdedEventsUrl = 'http://localhost:8991/events'
        
        # Test the function
        events = manEv.getCrowdedEvents(p)
        
        # Kill the process running the webserver once tested
        process = subprocess.Popen(['kill', '-9', str(pid)], shell=False, stdout=subprocess.PIPE)

        self.assertEquals(events[0]['objectId'], 'protest')
        self.assertEquals(events[1]['objectId'], 'spain')
    """
        
    def testCheckEvents_SAME(self):
        '''Tests checking of local to remote event lists.'''

        crowded = [{"start": "2012-10-07T13:41:07.734000", "objectId": "protest", "subType": "tag"},
                   {"start": "2012-10-07T13:44:42.044000", "objectId": "spain", "subType": "tag"}]

        local =   [{"start": "2012-10-07T13:41:07.734000", "objectId": "protest", "subType": "tag"},
                   {"start": "2012-10-07T13:44:42.044000", "objectId": "spain", "subType": "tag"}]

        old, new = manEv.checkEvents(crowded, local)
        self.assertEquals(old, [])
        self.assertEquals(new, [])
        
    def testCheckEvents_MORELOCAL(self):
        '''Tests checking of local to remote event lists.'''

        local = [{"loc": [-0.128723, 51.526896999999998], "objectId": "1509201", "subType": "geography", "start": "2012-10-07T17:59:19.205000", "radius": 0.022141293728782822, "bbox": [[-0.15086429372878282, 51.504755706271219], [-0.10658170627121719, 51.549038293728778]], "radius_m": 1999},
                 {"start": "2012-10-07T13:41:07.734000", "objectId": "protest", "subType": "tag"},
                 {"start": "2012-10-07T13:44:42.044000", "objectId": "spain", "subType": "tag"}]

        crowded = [{"start": "2012-10-07T13:41:07.734000", "objectId": "protest", "subType": "tag"},
                   {"start": "2012-10-07T13:44:42.044000", "objectId": "spain", "subType": "tag"}]

        old, new = manEv.checkEvents(crowded, local)
        self.assertEquals(old, [{"loc": [-0.128723, 51.526896999999998], "objectId": "1509201", "subType": "geography", "start": "2012-10-07T17:59:19.205000", "radius": 0.022141293728782822, "bbox": [[-0.15086429372878282, 51.504755706271219], [-0.10658170627121719, 51.549038293728778]], "radius_m": 1999}])
        self.assertEquals(new, [])
        

    def testCheckEvents_MORECROWDED(self):
        '''Tests checking of local to remote event lists.'''
        
        local = [{"loc": [-0.128723, 51.526896999999998], "objectId": "1509201", "subType": "geography", "start": "2012-10-07T17:59:19.205000", "radius": 0.022141293728782822, "bbox": [[-0.15086429372878282, 51.504755706271219], [-0.10658170627121719, 51.549038293728778]], "radius_m": 1999},
                 {"start": "2012-10-07T13:41:07.734000", "objectId": "protest", "subType": "tag"},
                 {"start": "2012-10-07T13:44:42.044000", "objectId": "spain", "subType": "tag"}]

        crowded = [{"loc": [-0.128723, 51.526896999999998], "objectId": "1509201", "subType": "geography", "start": "2012-10-07T17:59:19.205000", "radius": 0.022141293728782822, "bbox": [[-0.15086429372878282, 51.504755706271219], [-0.10658170627121719, 51.549038293728778]], "radius_m": 1999},
                   {"start": "2012-10-07T13:41:07.734000", "objectId": "salmo_trutta", "subType": "tag"},
                   {"start": "2012-10-07T13:41:07.734000", "objectId": "protest", "subType": "tag"},
                   {"start": "2012-10-07T13:44:42.044000", "objectId": "spain", "subType": "tag"}]

        old, new = manEv.checkEvents(crowded, local)
        self.assertEquals(old, [])
        self.assertEquals(new, [{"start": "2012-10-07T13:41:07.734000", "objectId": "salmo_trutta", "subType": "tag"}])


    def testFormatBBox(self):
        '''Tests correct extraction of bbox coords for command line'''

        bbox = [[-0.15086429372878282, 51.504755706271219], [-0.10658170627121719, 51.549038293728778]]
        n,s,e,w = manEv.formatBBox(bbox)
        self.assertAlmostEquals(n, 51.549038293728778)
        self.assertAlmostEquals(s, 51.504755706271219)
        self.assertAlmostEquals(e, -0.10658170627121719)
        self.assertAlmostEquals(w, -0.15086429372878282)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGetTopTags']
    unittest.main()