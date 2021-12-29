#-------------------------------------------------------------------------------
# Name:         utilities Module
# Purpose:      A set of common functions to be used in scripts
# Author:       Esri Nederland: Mark Jagt / Maartje Holtslag
# Created:      20211228
# Status:       Production
# Copyright:    (c) Esri Nederland BV 2021
# Version:      20211229.01
#-------------------------------------------------------------------------------

import logging
import datetime
import requests
import arcgis
import sys

## Global variables, to be used in all functions
_logger = None
_logToArcGIS = False

def configureLogging(logFilePath, logToArcGIS=False, level="DEBUG"):
    """
    Configure the Logger object

    Input:
        logFilePath             (str)   - the full path to the logfile to be created, if None, no log file is created
        log2ArcGIS              (str)   - set to True to write log messages to the ArcGIS output
        level                   (str)   - minimum log level for messages to be visible (WARNING > INFO > DEBUG)
    """

    ## Set global variables, to be used in all functions
    global _logger
    global _logToArcGIS

    ## Set whether log messages should be written to ArcGIS or not
    _logToArcGIS = logToArcGIS
    
    ## Create Logger object
    _logger = logging.getLogger()

    ## Create format to display log messages
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%Y%m%d-%H:%M:%S')

    ## If a file path has been specified, add a FileHandler to the current Logger
    if logFilePath:
        logFilePath = logFilePath.replace("[date]",datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        fileHandler = logging.FileHandler(logFilePath)
        fileHandler.setFormatter(formatter)
        fileHandler.setLevel(level)
        _logger.addHandler(fileHandler)

    ## If logToArcGIS is False, add a StreamHandler to the current Logger
    if not _logToArcGIS:
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        streamHandler.setLevel(level)
        _logger.addHandler(streamHandler)

    ## Set the log level to the Logger object
    _logger.setLevel(level)

    logInfo("Logging Created, logfile: {}".format(logFilePath))
    logDebug("utilities::configureLogging::End")

def resetLogging():
    """
    Reset all current active Logger objects
    """
    logDebug("utilities::resetLogging::Start")

    ## Set global variable, to be used in all functions
    global _logger

    if _logger:
        ## Close all active Logger handlers
        while len(_logger.handlers)>0:
            handler = _logger.handlers[0]
            _logger.removeHandler(handler)
            handler.close()
        _logger = None

    logDebug("utilities::resetLogging::End")

def getLogger():
    """
    Get the current active Logger object, if not present, configure a new one
    """
    logDebug("utilities::getLogger::Start")

    ## If no Logger object is present, configure a new one
    if not _logger:
        configureLogging(None)
    
    logDebug("utilities::getLogger::End")
    return _logger

def logException(exception, message = ""):
    """
    Log an Exception message

    Input:
        exception               (Exception) - the Exception that occured
        message                 (str)       - the message to display
    """
    logDebug("utilities::logException::Start")

    ## Log an exception message
    getLogger().exception(message)
    logToArcGIS(message,"FATAL")
    logToArcGIS(exception,"FATAL")

    logDebug("utilities::logException::End")

def logError(message):
    """
    Log an Error message

    Input:
        message                 (str)       - the message to display
    """
    logDebug("utilities::logError::Start")

    ## If the Logger is enabled for Error messages, log the message
    if getLogger().isEnabledFor(logging.ERROR):
        getLogger().error(message)
        logToArcGIS(message,"ERROR")

    logDebug("utilities::logError::End")
    
def logWarning(message):
    """
    Log a Warning message

    Input:
        message                 (str)       - the message to display
    """
    logDebug("utilities::logWarning::Start")

    ## If the Logger is enabled for Warning messages, log the message
    if getLogger().isEnabledFor(logging.WARN):
        getLogger().warning(message)
        logToArcGIS(message,"WARN")

    logDebug("utilities::logWarning::End")

def logInfo(message):
    """
    Log an Info message

    Input:
        message                 (str)       - the message to display
    """
    logDebug("utilities::logInfo::Start")

    ## If the Logger is enabled for Info messages, log the message
    if getLogger().isEnabledFor(logging.INFO):
        getLogger().info(message)
        logToArcGIS(message,"INFO")
    
    logDebug("utilities::logInfo::End")

def logDebug(message):
    """
    Log a Debug message

    Input:
        message                 (str)       - the message to display
    """
    logDebug("utilities::logDebug::Start")

    ## If the Logger is enabled for Debug messages, log the message
    if getLogger().isEnabledFor(logging.DEBUG):
        getLogger().debug(message)
        logToArcGIS(message,"DEBUG")
    
    logDebug("utilities::logDebug::End")

def logToArcGIS(message, level):
    """
    Log the message to the ArcGIS output window, if logging to ArcGIS is enabled

    Input:
        message                 (str)       - the message to display
        level                   (str)       - the level of the log message
    """

    ## Check if logging to ArcGIS is enabled
    if _logToArcGIS:
        logDebug("utilities::logToArcGIS::Start")

        ## Check if the arcpy module has already been imported
        if not checkModuleImport("arcpy"):
            import arcpy

        ## Set formatting for the messages in the ArcGIS output window
        fullMessage ="{} - {} - {}".format(datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S'), level, message)

        ## Add message to ArcGIS based on the log level
        if level == "ERROR" or level == "FATAL":
            arcpy.AddError(fullMessage)
        elif level =="WARN":
            arcpy.AddWarning(fullMessage)
        else:
            arcpy.AddMessage(fullMessage)
    
        logDebug("utilities::logToArcGIS::End")

def checkModuleImport(moduleName):
    """
    Check if the module is already imported

    Input:
        moduleName              (str)   - the name of the module to check
    Output: 
        moduleImported          (bool)  - True if module is imported, False if not
    """
    logDebug("utilities::checkModuleImport::Start::{}".format(moduleName))

    ## Boolean to indicate if module is imported or not
    moduleImported = False

    ## Check if the module is in the system modules and in the current Python directory
    if (moduleName in sys.modules) and (moduleName in dir()):
        moduleImported = True
    
    logDebug("utilities::checkModuleImport::End::{}".format(moduleName))
    return moduleImported

def sendRequest(url, type="POST", params=None, headers=None):
    """
    Send a request to a URL

    Input:
        url                     (str)   - the url to send the request to
        type                    (str)   - the type of request (GET or POST)
        params                  (dict)  - parameters to be sent with the request
        headers                 (dict)  - headers to be sent with the request
    Output:
        response                (dict)  - the JSON response of the request
    """
    logDebug("utilities::sendRequest::Start")

    ## Perform a GET request
    if type == "GET":
        rawResponse = requests.get(url, params=params, headers=headers)
    ## Perform a POST request
    else:
        rawResponse = requests.post(url, params=params, headers=headers)

    ## Convert the response to a json object, if possible
    if hasattr(rawResponse, "json"):
        response = rawResponse.json()
    ## Otherwise, get the text response
    else:
        response = rawResponse.text

    logDebug("utilities::sendRequest::End")
    return response

def sendGISRequest(gis, url, type="POST", params=None, headers=None):
    """
    Send a request to a URL, using the GIS object for authentication

    Input:
        gis                     (GIS)   - the Python API GIS object
        url                     (str)   - the url to send the request to
        type                    (str)   - the type of request (GET or POST)
        params                  (dict)  - parameters to be sent with the request
        headers                 (dict)  - headers to be sent with the request
    Output:
        response                (dict)  - the JSON response of the request
    """
    logDebug("utilities::sendGISRequest::Start")

    ## Perform a GET request
    if type == "GET":
        response = gis._con.get(url, params=params, headers=headers)
    ## Perform a POST request
    else:
        response = gis._con.post(url, params=params, headers=headers)

    ## Check if the reponse returned an error
    if "error" in response:
        logError("Error in response: {}".format(response["error"]))

    logDebug("utilities::sendGISRequest::End")
    return response

def getGIS(portalUsername=None, portalUrl=None):
    """
    Get a GIS object, either using a profile or the current active user in ArcGIS Pro

    Input:
        portalUsername          (str)   - username from the user to sign in with, if None, the the current active user in ArcGIS Pro will be used
        portalUrl               (str)   - URL to the ArcGIS Portal, if not ArcGIS Online
    Output:
        gis                     (GIS)   - the GIS object
    """
    logDebug("utilities::getGIS::Start")

    try:
        ## Sign in using a profile
        if portalUsername:
            logInfo("Signing in using profile, for user {}".format(portalUsername))

            ## Create a profile name
            profileName = "arcgis_{}".format(portalUsername)

            ## Create a ProfileManager object to check if the current profile exists
            profileManager = arcgis.gis._impl._profile.ProfileManager()
            if profileName not in profileManager.list():
                ## If a profile with the given name does not exist, ask the user to give the corresponding password
                import getpass
                portalPassword = getpass.getpass()

                ## Create a new profile
                profileManager.create(profileName, portalUrl, portalUsername, portalPassword)
                logInfo("Created new profile for user: {}".format(portalUsername))
            
            ## Create a GIS object, using the profile name
            gis = arcgis.GIS(portalUrl, profile=profileName)
        
        ## Sign in using the current active user in ArcGIS Pro
        else:
            logInfo("Signing in using ArcGIS Pro")

            ## Create a GIS object using ArcGIS Pro
            gis = arcgis.GIS("Pro")

        logInfo("Successfully signed in to '{}' with the '{}' user".format(gis.properties.portalHostname,gis.properties.user.username))

    except Exception as ex:
        logException(ex, "The GIS object could not be created. You either need to be signed in with ArcGIS Pro or provide a portal username")

        ## Return None if the GIS object could not be created
        gis = None

    logDebug("utilities::getGIS::End")
    return gis

def dateStringToTimestamp(dateString, formatting="%Y/%m/%d", returnInMilliseconds=True):
    """
    Convert a date string of the given format to a timestamp

    Input:
        dateString              (str)   - the date to be converted
        formatting              (str)   - formatting of the dateString, see: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        returnInMilliseconds    (bool)  - set whether timestamp should be in milliseconds
    Output:
        timestamp               (int)   - the created timestamp
    """
    logDebug("utilities::dateStringToTimestamp::Start")

    ## Convert the dateString to a datetime object
    element = datetime.datetime.strptime(dateString, formatting)

    ## Convert the datetime object to a timestamp
    timestamp = datetime.datetime.timestamp(element)

    ## If the timestamp should be in milliseconds, multiply by 1000
    if returnInMilliseconds:
        timestamp *= 1000
    
    logDebug("utilities::dateStringToTimestamp::End")
    return round(timestamp)

def timestampToDateString(timestamp, formatting="%Y/%m/%d"):
    """
    Convert a timestamp to a date string in the given format

    Input:
        timestamp               (int)   - the timestamp to be converted
        formatting              (str)   - formatting of the dateString result, see: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    Output:
        datestring              (str)   - the created date string
    """
    logDebug("utilities::timestampToDateString::Start")

    ## If the given timestamp is in milliseconds, divide by 1000
    if len(f"{timestamp}") > 10:
        timestamp /= 1000
    
    ## Convert the timestamp to a datetime object
    element = datetime.datetime.fromtimestamp(timestamp)

    ## Convert the datetime object to a date string in the given format
    dateString = datetime.datetime.strftime(element, formatting)

    logDebug("utilities::timestampToDateString::End")
    return dateString
