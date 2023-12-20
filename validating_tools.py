# Victor Flucus Last Edit: 19DEC23
# Edited from workfron's example files: https://github.com/Workfront/workfront-api-examples-python
# Class "SteamClient"
#   Input: url for a given workfront project.
#       I've been testing with the one for Buffer Run-Cell Sim (https://lonza.my.workfront.com/project/655438a4002709a80b2dd4f915205123/tasks)
#   Output: Nested dictionary of tasks and subtasks within the project
#
# Class "XMLtoJSON"
#   Input: File location of DeltaV XML file (use Mike Ecker's tool to create)
#   Output: All the data in the xml file converted to a JSON

# Imports
import certifi;
import json
import ssl;
import urllib
from urllib.request import urlopen
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import xmltodict
# try:
#     from urllib import urlencode
#     from urllib.request import urlopen
#     from urllib.parse import urlparse
# except ImportError:
#     from urllib.parse import urlencode



#CLASSES

#StreamClient is for interacting with Adobe Workfront's API, supporting classes follow
class StreamClient(object):

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'

    PATH_LOGIN = "/login"
    PATH_LOGOUT = "/logout"

    API_KEY = '&apiKey=jblyc291yz2t7s6r3y79rjrcgmb2c528'
    BASE_URL = 'https://lonza.my.workfront.com/attask/api/v15.0'

    # Create unverified context in xml (needed to get past [SSL: CERTIFICATE_VERIFY_FAILED] error)
    # https://support.chainstack.com/hc/en-us/articles/9117198436249-Common-SSL-Issues-on-Python-and-How-to-Fix-it
    CONTEXT = ssl._create_unverified_context()
    
    def __init__(self,url):
        #Parses url into compenents
        self.entered_url = url if not url.endswith('/') else url[:-1]
        parsed_url = urlparse(url)
        self.scheme = parsed_url.scheme
        self.netloc = parsed_url.netloc
        self.path = parsed_url.path
        self.path_components = self.path.split("/")[1:]
        self.handle = None


    def get_project_tasks(self):
        """
        Returns nested dictionary of all project tasks under instantiated project
        """
        # Find 'project' or 'proj' in path_components
        project_index = next((i for i, component in enumerate(self.path_components) if component == 'project' or 'proj' in component), None)

        # Check if 'project' or 'proj' was found, and get the subsequent value
        if project_index is not None and project_index + 1 < len(self.path_components):
            subsequent_value = self.path_components[project_index + 1]
            endpoint = "/project/search?id=%s&fields=tasks" % subsequent_value
            print(endpoint)
        else:
            error_msg = "No 'project' or 'proj' found in path_components or no subsequent value."
            return error_msg
        # Build path to API
        path = f'{StreamClient.BASE_URL}{endpoint}{StreamClient.API_KEY}'
        print(path)

        #Send GET request
        with urlopen(path, context=StreamClient.CONTEXT) as response:
            body = response.read()
        #return data to user
        # print(json.loads(body)) (THIS IS FOR DEBUGGING)
        return json.loads(body)

    def get(self,objcode,objid,fields=None):
        """
        Lookup an object by id
        objcode -- object type ie. ObjCode.PROJECT
        objid -- id to lookup
        [fields] -- list of field names to return for each object
        """
        path = '/%s/%s' % (objcode, objid)
        return self.request(path,None,StreamClient.GET,fields)

    def search(self,objcode,params,fields=None):
        """
        Search for objects
        objcode -- object type ie. ObjCode.PROJECT
        params -- name value keys to search for
        [fields] -- fields to return for each search result
        """
        path = '/%s/%s' % (objcode, 'search')
        return self.request(path,params,StreamClient.GET,fields)

    
class StreamAPIException(Exception):
    "Raised when a request fails"


class StreamClientNotSet(Exception):
    """Raised when calling an api method on an object without an
    attached StreamClient object
    """


# Supported object codes
class ObjCode:
    PROJECT = 'proj'
    TASK = 'task'
    ISSUE = 'optask'
    TEAM = 'team'
    HOUR = 'hour'
    TIMESHEET = 'tshet'
    USER = 'user'
    ASSIGNMENT = 'assgn'
    USER_PREF = 'userpf'
    CATEGORY = 'ctgy'
    CATEGORY_PARAMETER = 'ctgypa'
    PARAMETER = 'param'
    PARAMETER_GROUP = 'pgrp'
    PARAMETER_OPTION = 'popt'
    PARAMETER_VALUE = 'pval'
    ROLE = 'role'
    GROUP = 'group'
    NOTE = 'note'
    DOCUMENT = 'docu'
    DOCUMENT_VERSION = 'docv'
    EXPENSE = 'expns'
    CUSTOM_ENUM = 'custem'
    

#XMLtoJSON 

class XMLtoJSON:

    def __init__(self, file_loc):
        self.file_loc = file_loc
        self.tree = ET.parse('%s' % self.file_loc)
        self.xml_data = self.tree.getroot()
        #Change encoding type 
        self.xml_as_string = ET.tostring(self.xml_data, encoding='utf-8', method='xml')

    def convert(self):
        data_dict = xmltodict.parse(self.xml_as_string)

        json_data = json.dumps(data_dict)
        return json_data
