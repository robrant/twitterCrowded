import os
import mdb
import ConfigParser
import json
import subprocess
import logging

#----------------------------------------------------------------------------------------

def getPython():
    ''' Gets the currently installed python for this machine. '''
    
    process = subprocess.Popen(['which', 'python'], shell=False, stdout=subprocess.PIPE)
    response = process.communicate()
    python = response[0].rstrip('\n')
    return python

#----------------------------------------------------------------------------------------

class getConfigParameters():
    ''' Gets the configuration parameters into an object '''
    
    def __init__(self, filePath):
        
        config = ConfigParser.ConfigParser()
        try:
            config.read(filePath)
        except:
            logging.warning('Failed to read config file.')
        
        # Keep the location of the config file in the config file for mods on the fly
        self.configFile = filePath
        cwd = os.path.dirname(filePath)
        parent = os.path.dirname(cwd)
        
        self.source = config.get("default", "dataSource")
        self.python = config.get("default", "python")

        # Mongo parameters
        self.dbHost     = config.get("backend", "host")
        self.dbPort     = config.getint("backend", "port")
        self.db         = config.get("backend", "db")
        self.dbUser      = config.get("backend", "user")
        self.dbPassword  = config.get("backend", "password")
        self.dropCollection = config.getboolean("backend", "drop_collection")
        
        # Redis tweet staging 
        self.redisHost = config.get("stage", "redisHost")
        self.redisPort = config.getint("stage", "redisPort")
        self.redisPassword = config.get("stage", "redisPassword")
        self.redisName = config.get("stage", "redisName")
        
        # Collections and indexes
        self.collections      = json.loads(config.get("backend", "collections"))
        self.eventsCollection = self.collections[0]['collection']
        self.mgmtCollection   = self.collections[1]['collection']

        # Parameters for the instagram API
        self.sourceUser     = config.get("source", "user")
        self.sourcePassword = config.get("source", "password")
        self.warning        = config.get("source", "warning")
        
        # URLs that get used
        self.helpUrl        = config.get("web", "helpUrl")
        self.webStaticRoute = config.get("web", "webStaticRoute")
        self.POSTurl        = config.get("web", "target")
        self.crowdedEventsUrl = config.get("web", "eventList")
        
        # Error Logging
        self.logLevel  = self.checkLogLevel(config.get("error", "loglevel"))
        errorPath      = config.get("error", "err_path")   
        self.errorPath = os.path.join(parent, errorPath)
        self.errorFile = config.get("error", "err_file")
        self.connErrorFile = config.get("error", "conn_err_file")
        self.redisConsumerLog = config.get("error", "redis_err_file")

        #self.python = getPython()


    def checkLogLevel(self, logLevel):
        ''' Checks that the log level is correct or defaults to DEBUG.'''
        
        logLevel = logLevel.upper()
        if logLevel in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            level = getattr(logging, logLevel)
        else:
            level = 10
        return level
    
#----------------------------------------------------------------------------------------

def getMongoHandles(p):
    ''' Gets the mongo connection handle, authentication and the collection handle.  '''

    # Handles the mongo connections
    c, dbh = mdb.getHandle(db=p.db, host=p.dbHost, port=p.dbPort)

    # Authentication
    try:
        auth = dbh.authenticate(p.dbUser, p.dbPassword)
    except:
        logging.warning("Failed to authenticate with mongo db.")

    collHandle = dbh[p.slangCollection]
    emoCollHandle = dbh[p.emoCollection]
    
    return c, dbh, collHandle, emoCollHandle

#----------------------------------------------------------------------------------------

def decodeEncode(token, encoding='latin-1'):
    ''' Decoding and encoding the sting '''
    
    token = token.decode(encoding)
    token = token.encode('utf8')
    
    return token    
#-------------------------------------------------------------------------------------

