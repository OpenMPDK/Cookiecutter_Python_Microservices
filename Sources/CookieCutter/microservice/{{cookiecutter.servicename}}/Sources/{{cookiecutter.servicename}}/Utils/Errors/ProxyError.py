"""
Defines the error message and error code
"""
PROXY_NO_ERROR = 0
PROXY_GENERIC_ERROR = -1

PROXY_REQUESTS_GET_ERROR = 101
PROXY_REQUESTS_PUT_ERROR = 102
PROXY_REQUESTS_POST_ERROR = 103
PROXY_REQUESTS_DELETE_ERROR = 104

PROXY_INVALID_GET_RESPONSE_ERROR = 105
PROXY_INVALID_PUT_RESPONSE_ERROR = 106
PROXY_INVALID_POST_RESPONSE_ERROR = 107
PROXY_INVALID_DELETE_RESPONSE_ERROR = 108

PROXY_DECODE_JSON_RESPONSE_ERROR = 109
PROXY_EMPTY_JSON_RESPONSE_ERROR = 110

PROXY_ERRORCODE_NOT_PRESENT_RESPONSE_ERROR = 111
PROXY_MESSAGE_NOT_PRESENT_RESPONSE_ERROR = 112
PROXY_DATA_NOT_PRESENT_RESPONSE_ERROR = 113
PROXY_ERROR_IN_RESPONSE_ERROR = 114
PROXY_INVALID_POST_RESPONSE_ERROR_WITH_DETAILS = 115

ProxyErrorMessages = {
    PROXY_REQUESTS_GET_ERROR: 'Error while invoking GET request on URL {0} with params: {1}. Details: {2}',
    PROXY_REQUESTS_PUT_ERROR: 'Error while invoking PUT request on URL {0} with params: {1}. Details: {2}',
    PROXY_REQUESTS_POST_ERROR: 'Error while invoking POST request on URL {0} with params: {1}. Details: {2}',
    PROXY_REQUESTS_DELETE_ERROR: 'Error while invoking DELETE request on URL {0} with params: {1}. Details: {2}',

    PROXY_INVALID_GET_RESPONSE_ERROR: 'Invalid response received while invoking GET request on URL {0} with params: {'
                                      '1}. Details: {2}',
    PROXY_INVALID_PUT_RESPONSE_ERROR: 'Invalid response received while invoking PUT request on URL {0} with params: {'
                                      '1}. Details: {2}',
    PROXY_INVALID_POST_RESPONSE_ERROR: 'Invalid response received while invoking POST request on URL {0} with params: '
                                       '{1}. Details: {2}',
    PROXY_INVALID_POST_RESPONSE_ERROR_WITH_DETAILS: 'Invalid response received while invoking POST request on URL '
                                                    '{0} with params: {1}. Details: {2}. '
                                                    'Response Code : {3}. Response Message: {4}',
    PROXY_INVALID_DELETE_RESPONSE_ERROR: 'Invalid response received while invoking DELETE request on URL {0} with '
                                         'params: {1}. Details: {2}',

    PROXY_DECODE_JSON_RESPONSE_ERROR: 'Error while decoding JSON from response object {0}, Error Details: {1}',
    PROXY_EMPTY_JSON_RESPONSE_ERROR: 'Empty JSON received',

    PROXY_ERRORCODE_NOT_PRESENT_RESPONSE_ERROR: 'Filed ErrorCode not present in response. Response object {0}',
    PROXY_MESSAGE_NOT_PRESENT_RESPONSE_ERROR: 'Filed Message not present in response. Response object {0}',
    PROXY_DATA_NOT_PRESENT_RESPONSE_ERROR: 'Filed Data not present in response. Response object {0}',
    PROXY_ERROR_IN_RESPONSE_ERROR: '{0}',
}
