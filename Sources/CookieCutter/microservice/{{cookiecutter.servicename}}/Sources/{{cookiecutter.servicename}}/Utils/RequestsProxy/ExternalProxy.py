from requests import Session
from requests.adapters import HTTPAdapter
from pkg_resources import resource_filename
from requests.packages.urllib3.util.retry import Retry
from json.decoder import JSONDecodeError

from Utils.Utils.JsonUtils import decode_dict_str
from Utils.Exception.ProxyException import ProxyException
from Utils.Errors.ProxyError import *
from Utils.Core.Singleton import Singleton
from Utils.Core.BaseObject import BaseObject


# noinspection PyUnresolvedReferences
class ExternalProxy(BaseObject, Singleton):
    # noinspection PyProtectedMember
    def __init__(self):
        BaseObject.__init__(self)

        config_file_path = resource_filename('Utils', 'Conf/Utils.conf')
        self._config_manager.load_config_file(config_file_path)

        self._retry_attempt = self._config_manager._settings_parser.getint('RequestsSettings', 'retry_attempt')
        self._backoff_factor = self._config_manager._settings_parser.getint('RequestsSettings', 'backoff_factor')
        self._pool_connections = self._config_manager._settings_parser.getint('RequestsSettings', 'pool_connections')
        self._max_connections = 0

        self.initialize_proxy()

        self._session = Session()

        if self._max_connections and type(self._max_connections) == int:
            retry = Retry(total=self._retry_attempt, backoff_factor=self._backoff_factor)
            # retry applies only for failed DNS lookups, socket connection and connection timeout
            # back_off is time delay between retries
            adapter = HTTPAdapter(pool_connections=self._pool_connections, pool_maxsize=self._max_connections,
                                  max_retries=retry)

            self._session.mount('http://', adapter)
            self._session.mount('https://', adapter)

    def initialize_proxy(self):
        pass

    def get(self, url, parameters=None, **kwargs):
        """
        Get Request with Retry Support
        Custom response in a structured way to have Error_Code, Message, and Data
        Args:
            url: Get request url
            parameters: params to be sent as part of get request
            kwargs: additional params/args
        Returns:
            Response data
        Raises:
            ProxyException
            Exception
        """

        try:
            response_data = self._session.get(url, params=parameters, **kwargs)
        except Exception as e:
            self._Logger.error(ProxyErrorMessages[PROXY_REQUESTS_GET_ERROR].format(url, parameters, str(e)))
            raise ProxyException(PROXY_REQUESTS_GET_ERROR, url, parameters, str(e))

        if (not (response_data is None)) and (response_data.status_code in [200, 500]):
            try:
                response_json_data = response_data.json(object_hook=decode_dict_str)

                response_json_data1 = {}
                if isinstance(response_json_data, dict):
                    if not response_json_data.get('ErrorCode'):
                        response_json_data1['ErrorCode'] = 0
                    if not response_json_data.get('ErrorCode'):
                        if 'jsonrpc' in response_json_data:
                            response_json_data1['Message'] = response_json_data.get('jsonrpc')
                        else:
                            response_json_data1['Message'] = None
                    if not response_json_data.get('Data'):
                        response_json_data1['Data'] = response_json_data
                    if not response_json_data.get('ErrorCode'):
                        response_json_data = response_json_data1
                elif isinstance(response_json_data, list):
                    response_json_data1['ErrorCode'] = 0
                    response_json_data1['Message'] = 'Success'
                    response_json_data1['Data'] = response_json_data
                    response_json_data = response_json_data1
            except JSONDecodeError:
                response_json_data = {}
                response_json_data['ErrorCode'] = 0
                response_json_data['Message'] = response_data.text
                response_json_data['Data'] = response_data.text
            except Exception as e:
                raise ProxyException(PROXY_DECODE_JSON_RESPONSE_ERROR, response_data, str(e))

            if not response_json_data:
                raise ProxyException(PROXY_EMPTY_JSON_RESPONSE_ERROR)

            if not ('ErrorCode' in response_json_data):
                raise ProxyException(PROXY_ERRORCODE_NOT_PRESENT_RESPONSE_ERROR, response_json_data)

            if not ('Message' in response_json_data):
                raise ProxyException(PROXY_MESSAGE_NOT_PRESENT_RESPONSE_ERROR, response_json_data)

            if not ('Data' in response_json_data):
                raise ProxyException(PROXY_DATA_NOT_PRESENT_RESPONSE_ERROR, response_json_data)

            if response_json_data.get('ErrorCode'):
                raise ProxyException(PROXY_ERROR_IN_RESPONSE_ERROR, response_json_data.get('Message'))

            return_value = response_json_data['Data']

        else:
            raise ProxyException(PROXY_INVALID_GET_RESPONSE_ERROR, url, parameters, response_data.content)

        return return_value

    def put(self, url, parameters=None, **kwargs):
        """
        Put Request with Retry Support
        Custom response in a structured way to have Error_Code, Message, and Data
        Args:
            url: Put request url
            parameters: params to be sent as part of Put request
            kwargs: additional params/args
        Returns:
            Response data
        Raises:
            ProxyException
            Exception
        """

        try:
            response_data = self._session.put(url, params=parameters, **kwargs)
        except Exception as e:
            self._Logger.error(ProxyErrorMessages[PROXY_REQUESTS_PUT_ERROR].format(url, parameters, str(e)))
            raise ProxyException(PROXY_REQUESTS_PUT_ERROR, url, parameters, str(e))

        if (not (response_data is None)) and (response_data.status_code in [200, 202, 500]):
            try:
                response_json_data = response_data.json(object_hook=decode_dict_str)

                response_json_data1 = {}
                if isinstance(response_json_data, dict):
                    if not response_json_data.get('ErrorCode'):
                        response_json_data1['ErrorCode'] = 0
                    if not response_json_data.get('ErrorCode'):
                        if 'jsonrpc' in response_json_data:
                            response_json_data1['Message'] = response_json_data.get('jsonrpc')
                        else:
                            response_json_data1['Message'] = None
                    if not response_json_data.get('Data'):
                        response_json_data1['Data'] = response_json_data
                    if not response_json_data.get('ErrorCode'):
                        response_json_data = response_json_data1
                elif isinstance(response_json_data, list):
                    response_json_data1['ErrorCode'] = 0
                    response_json_data1['Message'] = 'Success'
                    response_json_data1['Data'] = response_json_data
                    response_json_data = response_json_data1
            except JSONDecodeError:
                response_json_data = {}
                response_json_data['ErrorCode'] = 0
                response_json_data['Message'] = response_data.text
                response_json_data['Data'] = response_data.text
            except Exception as e:
                raise ProxyException(PROXY_DECODE_JSON_RESPONSE_ERROR, response_data, str(e))

            if not response_json_data:
                raise ProxyException(PROXY_EMPTY_JSON_RESPONSE_ERROR)

            if not ('ErrorCode' in response_json_data):
                raise ProxyException(PROXY_ERRORCODE_NOT_PRESENT_RESPONSE_ERROR, response_json_data)

            if not ('Message' in response_json_data):
                raise ProxyException(PROXY_MESSAGE_NOT_PRESENT_RESPONSE_ERROR, response_json_data)

            if not ('Data' in response_json_data):
                raise ProxyException(PROXY_DATA_NOT_PRESENT_RESPONSE_ERROR, response_json_data)

            if response_json_data.get('ErrorCode'):
                raise ProxyException(PROXY_ERROR_IN_RESPONSE_ERROR, response_json_data.get('Message'))

            return_value = response_json_data['Data']

        else:
            raise ProxyException(PROXY_INVALID_PUT_RESPONSE_ERROR, url, parameters, response_data.content)

        return return_value

    def post(self, url, data=None, json_data=None, **kwargs):
        """
        Post Request with Retry Support
        Custom response in a structured way to have Error_Code, Message, and Data
        Args:
            url: Post request url
            data: form Data  to be sent as part of Post request
            json_data: Json Data  to be sent as part of Post request
            kwargs: additional params/args
        Returns:
            Response data
        Raises:
            ProxyException
            Exception
        """

        try:
            response_data = self._session.post(url, data=data, json=json_data, **kwargs)
        except Exception as e:
            self._Logger.error(ProxyErrorMessages[PROXY_REQUESTS_POST_ERROR].format(url, data, json_data, str(e)))
            raise ProxyException(PROXY_REQUESTS_POST_ERROR, url, data, json_data, str(e))

        if (not (response_data is None)) and (response_data.status_code in [200, 202, 500]):
            try:
                response_json_data = response_data.json(object_hook=decode_dict_str)
                response_json_data1 = {}
                if isinstance(response_json_data, dict):
                    if not response_json_data.get('ErrorCode'):
                        response_json_data1['ErrorCode'] = 0
                    if not response_json_data.get('ErrorCode'):
                        if 'jsonrpc' in response_json_data:
                            response_json_data1['Message'] = response_json_data.get('jsonrpc')
                        else:
                            response_json_data1['Message'] = None
                    if not response_json_data.get('Data'):
                        response_json_data1['Data'] = response_json_data
                    if not response_json_data.get('ErrorCode'):
                        response_json_data = response_json_data1
                elif isinstance(response_json_data, list):
                    response_json_data1['ErrorCode'] = 0
                    response_json_data1['Message'] = 'Success'
                    response_json_data1['Data'] = response_json_data
                    response_json_data = response_json_data1
            except JSONDecodeError:
                response_json_data = {}
                response_json_data['ErrorCode'] = 0
                response_json_data['Message'] = response_data.text
                response_json_data['Data'] = response_data.text
            except Exception as e:
                raise ProxyException(PROXY_DECODE_JSON_RESPONSE_ERROR, response_data, str(e))

            if not response_json_data:
                raise ProxyException(PROXY_EMPTY_JSON_RESPONSE_ERROR)

            if not ('ErrorCode' in response_json_data):
                raise ProxyException(PROXY_ERRORCODE_NOT_PRESENT_RESPONSE_ERROR, response_json_data)

            if not ('Message' in response_json_data):
                raise ProxyException(PROXY_MESSAGE_NOT_PRESENT_RESPONSE_ERROR, response_json_data)

            if not ('Data' in response_json_data):
                raise ProxyException(PROXY_DATA_NOT_PRESENT_RESPONSE_ERROR, response_json_data)

            if response_json_data.get('ErrorCode'):
                raise ProxyException(PROXY_ERROR_IN_RESPONSE_ERROR, response_json_data.get('Message'))

            return_value = response_json_data['Data']

        else:
            raise ProxyException(PROXY_INVALID_POST_RESPONSE_ERROR_WITH_DETAILS, url, data, json_data,
                                 response_data.content)

        return return_value

    def delete(self, url, **kwargs):
        """
        Delete Request with Retry Support
        Custom response in a structured way to have Error_Code, Message, and Data
        Args:
            url: Delete request url
        Returns:
            Response data
        Raises:
            ProxyException
            Exception
        """

        try:
            response_data = self._session.delete(url, **kwargs)
        except Exception as e:
            self._Logger.error(ProxyErrorMessages[PROXY_REQUESTS_DELETE_ERROR].format(url, str(e)))
            raise ProxyException(PROXY_REQUESTS_DELETE_ERROR, url, str(e))

        if (not (response_data is None)) and (response_data.status_code in [200, 202, 500]):
            try:
                response_json_data = response_data.json(object_hook=_decode_dict)
                response_json_data1 = {}
                if isinstance(response_json_data, dict):
                    if not response_json_data.get('ErrorCode'):
                        response_json_data1['ErrorCode'] = 0
                    if not response_json_data.get('ErrorCode'):
                        if 'jsonrpc' in response_json_data:
                            response_json_data1['Message'] = response_json_data.get('jsonrpc')
                        else:
                            response_json_data1['Message'] = None
                    if not response_json_data.get('Data'):
                        response_json_data1['Data'] = response_json_data
                    if not response_json_data.get('ErrorCode'):
                        response_json_data = response_json_data1
                elif isinstance(response_json_data, list):
                    response_json_data1['ErrorCode'] = 0
                    response_json_data1['Message'] = 'Success'
                    response_json_data1['Data'] = response_json_data
                    response_json_data = response_json_data1
            except JSONDecodeError:
                response_json_data = {}
                response_json_data['ErrorCode'] = 0
                response_json_data['Message'] = response_data.text
                response_json_data['Data'] = response_data.text
            except Exception as e:
                raise ProxyException(PROXY_DECODE_JSON_RESPONSE_ERROR, response_data, str(e))

            if not response_json_data:
                raise ProxyException(PROXY_EMPTY_JSON_RESPONSE_ERROR)

            if not ('ErrorCode' in response_json_data):
                raise ProxyException(PROXY_ERRORCODE_NOT_PRESENT_RESPONSE_ERROR, response_json_data)

            if not ('Message' in response_json_data):
                raise ProxyException(PROXY_MESSAGE_NOT_PRESENT_RESPONSE_ERROR, response_json_data)

            if not ('Data' in response_json_data):
                raise ProxyException(PROXY_DATA_NOT_PRESENT_RESPONSE_ERROR, response_json_data)

            if response_json_data.get('ErrorCode'):
                raise ProxyException(PROXY_ERROR_IN_RESPONSE_ERROR, response_json_data.get('Message'))

            return_value = response_json_data['Data']

        else:
            raise ProxyException(PROXY_INVALID_DELETE_RESPONSE_ERROR, url, response_data.content)

        return return_value
