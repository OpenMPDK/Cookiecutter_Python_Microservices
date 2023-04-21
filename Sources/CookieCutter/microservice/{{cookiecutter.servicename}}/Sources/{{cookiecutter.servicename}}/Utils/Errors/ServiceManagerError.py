"""
Defines the error message and error code
"""
INVALID_SERVICE_CONFIGURATION_TEXT = 20
PARSING_SERVICE_CONFIGURATION_TEXT = 21
NO_COMMAND_SPECIFIED_FOR_SERVICE = 22
NO_SERVICE_NAME_SPECIFIED = 23
REREAD_UPDATE_SUPERVISOR_FAILED = 24
INVALID_SERVICE_NAME_PROVIDED_FOR_DEREGISTERING = 25
GET_ALL_PROCESS_INFO = 26
ERROR_WHILE_STOPPING_SERVICE = 27

ServiceManagerErrorMessages = {
    INVALID_SERVICE_CONFIGURATION_TEXT: 'Invalid service configuration text : {0}',
    PARSING_SERVICE_CONFIGURATION_TEXT: 'Error while parsing service configuration text : {0}',
    NO_COMMAND_SPECIFIED_FOR_SERVICE: 'Program has no command specified : {0}',
    NO_SERVICE_NAME_SPECIFIED: 'Service specification does not have a service name specified : {0}',
    REREAD_UPDATE_SUPERVISOR_FAILED: 'Reread amd update of supervisord failed with Error : {0}',
    INVALID_SERVICE_NAME_PROVIDED_FOR_DEREGISTERING: 'Invalid service name requested for de-registration : {0}',
    GET_ALL_PROCESS_INFO: 'Error while querying all process info from supervisor. Details : {0}',
    ERROR_WHILE_STOPPING_SERVICE: 'Error while stopping service : {0}. Details : {1}',
}
