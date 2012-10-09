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
import baseUtils
import datetime

class Test(unittest.TestCase):
    
    def testGetPython(self):
        '''Tests successful retrieval of the python executable.'''

        truth = '/usr/bin/python'
        python = baseUtils.getPython()
        self.assertEquals(python, truth)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGetTopTags']
    unittest.main()