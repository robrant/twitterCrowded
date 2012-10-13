import os
import mdb
import ConfigParser
import json
import subprocess

# Get the directory in which this was executed (current working dir)
cwd = os.getcwd()
wsDir = os.path.dirname(cwd)

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
        except Exception, e:
            print "Failed to read the config file for twitter connection client."
            print e
        
        # Keep the location of the config file in the config file for mods on the fly
        self.configFile = filePath
        
        self.source = config.get("default", "dataSource")
        
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
        self.verbose   = config.getboolean("error", "verbose")
        self.writeOut  = config.getboolean("error", "write_out") 
        errorPath      = config.get("error", "err_path")   
        self.errorPath = os.path.join(wsDir, errorPath)
        self.errorFile = config.get("error", "err_file")

        self.python = getPython() 

        
#----------------------------------------------------------------------------------------

def getMongoHandles(p):
    ''' Gets the mongo connection handle, authentication and the collection handle.  '''

    # Handles the mongo connections
    c, dbh = mdb.getHandle(db=p.db, host=p.dbHost, port=p.dbPort)

    # Authentication
    try:
        auth = dbh.authenticate(p.dbUser, p.dbPassword)
    except Exception, e:
        print "Failed to authenticate with mongo db."
        print e

    collHandle = dbh[p.slangCollection]
    emoCollHandle = dbh[p.emoCollection]
    
    return c, dbh, collHandle, emoCollHandle

#-------------------------------------------------------------------------------------

def handleErrors(p, error):
    ''' Handles the printing (or other) of errors. '''

    # Report out the parsing errors if verbose is set
    if p.verbose == True:
        print "-"*10+"Error"+"-"*10
        print error

    if p.writeOut == True:
        f = open(os.path.join(p.errorPath, p.errorFile), 'a')
        f.write(str(error)+'\n')
        f.close()
#----------------------------------------------------------------------------------------

def decodeEncode(token, encoding='latin-1'):
    ''' Decoding and encoding the sting '''
    
    token = token.decode(encoding)
    token = token.encode('utf8')
    
    return token    
#-------------------------------------------------------------------------------------

