import io
import os
import re
import xmlrpc.client
from configparser import ConfigParser

from Utils.Core.BaseObject import BaseObject
from Utils.Core.Singleton import Singleton
from Utils.Errors.ServiceManagerError import INVALID_SERVICE_CONFIGURATION_TEXT, \
    PARSING_SERVICE_CONFIGURATION_TEXT, NO_COMMAND_SPECIFIED_FOR_SERVICE, NO_SERVICE_NAME_SPECIFIED, \
    REREAD_UPDATE_SUPERVISOR_FAILED, INVALID_SERVICE_NAME_PROVIDED_FOR_DEREGISTERING, GET_ALL_PROCESS_INFO, \
    ERROR_WHILE_STOPPING_SERVICE
from Utils.Exception.ServiceManagerException import ServiceManagerException
from Utils.Utils.PathUtils import get_abs_path


class ServiceManager(BaseObject, Singleton):
    default_supervisor_xmlrpc_url = 'http://localhost:9001/RPC2'
    default_supervisor_config_dir = '~/services/conf.d'
    default_supervisor_logs_dir = '~/services/logs'

    service_config_cmd = 'command'

    service_config_program_name_patter = r'program:(?P<progname>\w+)'

    def __init__(self):
        """
        Constructor of this class
        """
        BaseObject.__init__(self)

        supervisor_xmlrpc_url = self._config_manager.get_setting_value('Supervisor', 'Supervisor_XML_RPC_URL')
        if not supervisor_xmlrpc_url:
            supervisor_xmlrpc_url = self.default_supervisor_xmlrpc_url

        supervisor_config_dir = self._config_manager.get_setting_value('Supervisor', 'Supervisor_Config_Dir_Path')
        if not supervisor_config_dir:
            supervisor_config_dir = self.default_supervisor_config_dir

        supervisor_logs_dir = self._config_manager.get_setting_value('Supervisor', 'Supervisor_Logs_Dir_Path')
        if not supervisor_logs_dir:
            supervisor_logs_dir = self.default_supervisor_logs_dir

        self._supervisor_xmlrpc_url = supervisor_xmlrpc_url
        self._supervisor_config_dir = get_abs_path(supervisor_config_dir)
        self._supervisor_logs_dir = get_abs_path(supervisor_logs_dir)

        if not os.path.exists(self._supervisor_config_dir):
            os.makedirs(self._supervisor_config_dir)

        if not os.path.exists(self._supervisor_logs_dir):
            os.makedirs(self._supervisor_logs_dir)

    def get_supervisor_service_config_path(self):
        """
        Get the supervisor config path location
        Returns:
            supervisor configuration path location
        """

        return self._supervisor_config_dir

    def get_supervisor_service_logs_path(self):
        """
        Get the supervisor logs path location
        Returns:
            supervisor logs path location
        """
        return self._supervisor_logs_dir

    def register_supervisor_service(self, service_config_text):
        """
        Register supervisor daemon service (Not support for windows platform)
        Returns:
            boolean true/false
        Raises:
            ServiceManagerException
        """
        if (service_config_text is None) or (not type(service_config_text) in [str, str]):
            raise ServiceManagerException(INVALID_SERVICE_CONFIGURATION_TEXT, service_config_text)
        buffer = io.StringIO(service_config_text)

        try:
            config_parser = ConfigParser()
            config_parser.optionxform = str
            config_parser.read_file(buffer)
        except Exception as e:
            self._Logger.error('Error while parsing service config text. Details : %s' % e)
            raise ServiceManagerException(PARSING_SERVICE_CONFIGURATION_TEXT, e)

        _sections = config_parser.sections()

        for _section in _sections:
            match = re.match(ServiceManager.service_config_program_name_patter, _section)
            _service_name = None
            if match:
                _service_name = match.group('progname')

            if _service_name:
                if config_parser.has_option(_section, ServiceManager.service_config_cmd):
                    config_file_path = os.path.join(self._supervisor_config_dir, ('%s.conf' % _service_name))
                    with open(config_file_path, 'w') as config_file_handler:
                        config_file_handler.write(service_config_text)
                else:
                    raise ServiceManagerException(NO_COMMAND_SPECIFIED_FOR_SERVICE, _service_name)
            else:
                raise ServiceManagerException(NO_SERVICE_NAME_SPECIFIED, _service_name)

        self._reread_update_supervisor_service()

        return True

    def _reread_update_supervisor_service(self):
        """
        Reread the configuration changes and updates the supervisor services
        Returns:
            boolean true/false
        Raises:
            ServiceManagerException
        """
        try:
            supervisor_proxy = xmlrpc.client.Server(self._supervisor_xmlrpc_url)

            new_configuration = supervisor_proxy.supervisor.reloadConfig()

            changed_configuration = new_configuration[0]

            if changed_configuration:
                added_groups = changed_configuration[0]
                modified_groups = changed_configuration[1]
                deleted_groups = changed_configuration[2]

                if added_groups:
                    for _group in added_groups:
                        supervisor_proxy.supervisor.addProcessGroup(_group)
                        supervisor_proxy.supervisor.startProcessGroup(_group)
                if modified_groups:
                    for _group in modified_groups:
                        supervisor_proxy.supervisor.addProcessGroup(_group)
                        supervisor_proxy.supervisor.startProcessGroup(_group)
                if deleted_groups:
                    for _group in deleted_groups:
                        supervisor_proxy.supervisor.stopProcessGroup(_group)
                        supervisor_proxy.supervisor.removeProcessGroup(_group)
        except Exception as e:
            raise ServiceManagerException(REREAD_UPDATE_SUPERVISOR_FAILED, e)

        return True

    def deregister_supervisor_service(self, service_name):
        """
        Deregisters a registered service by stopping/removing the service
        Returns:
            boolean true/false
        Raises:
            ServiceManagerException
        """
        if self.is_supervisor_service_registered(service_name):
            self.stop_supervisor_service(service_name)
            config_file_path = os.path.join(self._supervisor_config_dir, ('%s.conf' % service_name))
            if not os.path.exists(config_file_path):
                raise ServiceManagerException(INVALID_SERVICE_NAME_PROVIDED_FOR_DEREGISTERING, service_name)

            os.remove(config_file_path)

            self._reread_update_supervisor_service()

        return True

    def is_supervisor_service_registered(self, service_name):
        """
        Checks and returns if the supervisor service is registered or not
        Returns:
            boolean true/false
        Raises:
            ServiceManagerException
        """

        try:
            supervisor_proxy = xmlrpc.client.Server(self._supervisor_xmlrpc_url)
            current_processes = supervisor_proxy.supervisor.getAllProcessInfo()
        except Exception as e:
            raise ServiceManagerException(GET_ALL_PROCESS_INFO, e)

        bool_found = False
        if current_processes:
            bool_found = [True for _process in current_processes if _process['name'] == service_name]
            # for _process in current_processes:
            #     if _process['name'] == service_name:
            #         bool_found = True
            #         break
        return bool_found

    def is_supervisor_service_running(self, service_name):
        """
        Checks and returns if the supervisor service is running or not
        Returns:
            boolean true/false
        Raises:
            ServiceManagerException
        """

        try:
            supervisor_proxy = xmlrpc.client.Server(self._supervisor_xmlrpc_url)
            current_processes = supervisor_proxy.supervisor.getAllProcessInfo()
        except Exception as e:
            raise ServiceManagerException(GET_ALL_PROCESS_INFO, e)

        bool_running = False
        if current_processes:
            bool_running = [True for _process in current_processes if
                            (_process['name'] == service_name and _process['statename'] == 'RUNNING')]
            # for _process in current_processes:
            #     if (_process['name'] == service_name and _process['statename'] == 'RUNNING'):
            #         bool_running = True
            #         break
        return bool_running

    def start_supervisor_service(self, service_name, b_restart_if_already_running=False):
        """
        Starts supervisor service
        Returns:
            boolean true/false
        Raises:
            ServiceManagerException
        """

        try:
            supervisor_proxy = xmlrpc.client.Server(self._supervisor_xmlrpc_url)

            if self.is_supervisor_service_running(service_name):
                if b_restart_if_already_running:
                    supervisor_proxy.supervisor.stopProcess(service_name)

            supervisor_proxy.supervisor.startProcess(service_name)
        except Exception as e:
            raise ServiceManagerException(ERROR_WHILE_STOPPING_SERVICE, e)

        return True

    def stop_supervisor_service(self, service_name):
        """
        Stops supervisor service
        Returns:
            boolean true/false
        Raises:
            ServiceManagerException
        """

        try:
            supervisor_proxy = xmlrpc.client.Server(self._supervisor_xmlrpc_url)

            if self.is_supervisor_service_running(service_name):
                supervisor_proxy.supervisor.stopProcess(service_name)

        except Exception as e:
            raise ServiceManagerException(ERROR_WHILE_STOPPING_SERVICE, e)

        return True

    def get_supervisor_services(self, service_name_regex):
        """
        Gets all supervisor service
        Returns:
            list of all supervisor services
        Raises:
            ServiceManagerException
        """
        supervisor_services_list = list()

        try:
            supervisor_proxy = xmlrpc.client.Server(self._supervisor_xmlrpc_url)
            current_processes = supervisor_proxy.supervisor.getAllProcessInfo()
        except Exception as e:
            raise ServiceManagerException(GET_ALL_PROCESS_INFO, e)

        if current_processes:
            supervisor_services_list = [_process for _process in current_processes if
                                        (re.match(service_name_regex, _process['name']))]
            # for _process in current_processes:
            #     pName = _process['name']  
            #     if (re.match(service_name_regex, pName)):
            #         supervisor_services_list.append(pName)
        return supervisor_services_list
