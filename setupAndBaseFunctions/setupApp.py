import os
import sys

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
            sys.path.append(directory)

#============================================================================================

import configureDatabase
import setupDatabase
import cleanupAllSubs

# Get the config file
configFile = sys.argv[1]

# Where this is being run - 
site = sys.argv[2]

# Clean the instagram subscriptions on their server
print '----> Cleaning all existing subscriptions on instagram.'
cleanupAllSubs.main(configFile)

# Configuring the dotcloud settings for mongodb
if site == 'dotcloud':
    print '----> Configuring the dotcloud settings for mongodb'
    configureDatabase.main(configFile)
elif site == 'local':
    print '***** Skipping all dotcloud configuration. '
    pass

# Setup the database
print '----> Setting up and populating database'
setupDatabase.main(configFile)
