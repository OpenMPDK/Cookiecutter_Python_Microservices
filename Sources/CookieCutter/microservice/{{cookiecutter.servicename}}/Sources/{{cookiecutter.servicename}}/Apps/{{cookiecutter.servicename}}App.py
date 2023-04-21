import os
import sys
import logging.config

from datetime import datetime
from pkg_resources import resource_filename
from cliff.app import App
from cliff.commandmanager import CommandManager

from Utils.Core.ConfigManager import ConfigManager
from Utils.Utils.PathUtils import get_abs_path
from Utils.Utils.SysUtils import get_logged_in_user
from Utils.Cliff.InteractiveApp import InteractiveApp

from {{cookiecutter.servicename}} import __description__, __version__

from {{cookiecutter.servicename}}.Core.RestServer import RestServer
from {{cookiecutter.servicename}}.Core.{{cookiecutter.servicename}}Manager import {{cookiecutter.servicename}}Manager

class {{cookiecutter.servicename}}App(App):
    user_config_file_path = os.path.normpath('~/.{{cookiecutter.servicename}}/{{cookiecutter.servicename}}.conf')
    logs_folder_path = os.path.normpath('~/.{{cookiecutter.servicename}}/Logs')
    logs_file_name = '{{cookiecutter.servicename}}.log'
    rest_server_working_folder_name = 'RestServer'
    working_folder_path = os.getcwd()
    supervisor_config_dir_path = '/opt/supervisor/conf.d'
    supervisor_logs_dir_path = '~/services/logs/{{cookiecutter.servicename}}Logs'
    rest_server_supervisor_conf_program_name='{{cookiecutter.servicename}}_REST_SERVER'

    def __init__(self):
        #self._rest_server_working_folder_path
        super({{cookiecutter.servicename}}App, self).__init__(
            description=__description__,
            version=__version__,
            command_manager=CommandManager('{{cookiecutter.servicename}}.commands'),
            interactive_app_factory=InteractiveApp,
            deferred_help=True
        )
        self._config_manager = None

        config_file_path = resource_filename('{{cookiecutter.servicename}}', 'Conf/{{cookiecutter.servicename}}.conf')

        self._config_manager = ConfigManager.get_instance()
        self._config_manager.load_config_file(config_file_path)

        self.load_custom_settings()
        
        #Working folder Path setup
        working_folder_path = self._derive_working_folder_path()
        self._working_folder_path = get_abs_path(working_folder_path)

        self._config_manager.set_setting_value('General', 'Working_Folder_Path', self._working_folder_path)

        if not os.path.exists(self._working_folder_path):
            os.makedirs(self._working_folder_path)
        
        #Rest Server Setup
        _rest_server_working_folder_Name = self._config_manager.get_setting_value('General', 'Rest_Server_Working_Folder_Name')
        if not _rest_server_working_folder_Name:
            _rest_server_working_folder_Name = {{cookiecutter.servicename}}App.rest_server_working_folder_name

        self._rest_server_working_folder_path = os.path.join(self._working_folder_path, _rest_server_working_folder_Name)

        if not os.path.exists(self._rest_server_working_folder_path):
            os.makedirs(self._rest_server_working_folder_path)

        self._rest_server = None
        self._{{cookiecutter.servicename}}Manager = {{cookiecutter.servicename}}Manager.get_instance()


    def load_custom_settings(self):
        """
        Loads user configuration if available
        """
        user_config_file_path_from_config = self._config_manager.get_setting_value('General', 'User_Config_File_Path')
        if not user_config_file_path_from_config:
            user_config_file_path_from_config = self.user_config_file_path
        
        _user_config_file_path = get_abs_path(user_config_file_path_from_config)
        self._config_manager.load_user_config_file(_user_config_file_path)

    def _derive_working_folder_path(self):
        """
        Derives the working folder path for {{cookiecutter.servicename}}
        """
        _working_folder_path = None
        working_folder_path_from_config = self._config_manager.get_setting_value('General', 'Working_Folder_Path')
        if os.path.exists(working_folder_path_from_config):
            is_working_folder_path_modified = self._config_manager.is_setting_modified_by_user('General', 'Working_Folder_Path')
        else:
            is_working_folder_path_modified = False

        if is_working_folder_path_modified:
            _working_folder_path = working_folder_path_from_config
            return _working_folder_path
        
        working_folder_name_from_config = self._config_manager.get_setting_value('General', 'Working_Folder_Name')
        if not working_folder_name_from_config:
            return os.path.join({{cookiecutter.servicename}}App.working_folder_path, get_logged_in_user(), working_folder_name_from_config)
        else:
            return working_folder_path_from_config

    def initialize_app(self, argv):
        """
        Initializes the Main {{cookiecutter.servicename}}app
        """
        if ( ('-h' in argv) or ('help' in argv) or ('--help' in argv)):
            return

        self.LOG.info('Initializing App')
        self.LOG.info('Initializing Rest Server')
        self._rest_server = RestServer.get_instance(self._rest_server_working_folder_path)
        self.LOG.info('Initialized Rest Server')

    def configure_logging(self):
        """
        Configure logging logic for the app based on the logging configuration file
        """
        log_config_file_path = resource_filename('{{cookiecutter.servicename}}', 'Conf/{{cookiecutter.servicename}}_Log.conf')

        log_file_path = None
        if ((hasattr(self, 'options')) and (hasattr(self.options, 'log_file')) and self.options.log_file):
            log_file_path = get_abs_path(self.options.log_file)
        else:
            logs_folder_path_from_config = self._config_manager.get_setting_value('Logging', 'Logs_Folder_Path')
            if not logs_folder_path_from_config:
                logs_folder_path_from_config = {{cookiecutter.servicename}}App.logs_folder_path

            logs_folder_path = get_abs_path(logs_folder_path_from_config)

            if not os.path.exists(logs_folder_path):
                os.makedirs(logs_folder_path)
            
            log_file_name_from_config = self._config_manager.get_setting_value('Logging', 'Log_File_Name')

            if not log_file_name_from_config:
                log_file_name_from_config = {{cookiecutter.servicename}}App.logs_file_name

            log_file_path = os.path.join(logs_folder_path,log_file_name_from_config)

        logging.config.fileConfig(log_config_file_path, {'log_file_path' : ("%r" % log_file_path)}, False)
        

    def shutdown_app(self, argv, returnCode):
        """
        Shut downs the rest server app
        """
        if ((returnCode == -1) and (argv) and (argv[0] == 'restserver') and (argv[1] == 'start')):
            self.stop_rest_server(True)

    def start_rest_server(self, force_start = False):
        """
        Starts the rest server
        """
        if not self._rest_server:
            self.LOG.info('Initializing Rest Server')
            self._rest_server = RestServer.get_instance(self._rest_server_working_folder_path)
            self.LOG.info('Initialized Rest Server')
        self.LOG.info('Starting rest server')
        self._rest_server.start_rest_server(force_start = force_start)

    def stop_rest_server(self, ignore_stop_failure = False):
        """
        Stops the rest server
        """
        self.LOG.info('Stopping rest server')
        if self._rest_server:
            try:
                self._rest_server.stop_rest_server(ignore_stop_failure)
            except Exception as e:
                self.LOG.error('Cannot shutdown Rest Server. Details -- %s' % str(e))
                if not ignore_stop_failure:
                    raise e

    def get_rest_server_network_config(self):
        """
        Gets the rest server network configuration and returns (host, port) as a tuple
        """
        network_host = self._rest_server.get_rest_server_host()
        network_port = self._rest_server.get_rest_server_port()
        return (network_host, network_port)

    def set_rest_server_network_config(self, host, port):
        """
        Sets the rest server network configuration with specified host and port
        """
        self._rest_server.set_rest_server_host(host)
        self._rest_server.set_rest_server_port(port)

    def show_rest_api_spec(self):
        """
        Shows the API spec in a browser
        """
        self._rest_server.show_rest_api_spec()

    def set_rest_url_prefix(self, url_prefix) :
        """
        Set the rest server's url prefix details as per the argument
        """
        return self._config_manager.set_setting_value('Rest_Server', 'URL_Prefix', url_prefix)

    def get_rest_url_prefix(self):
        """
        Get the rest server's url prefix details
        """
        return self._config_manager.get_setting_value('Rest_Server', 'URL_Prefix')

    def get_rest_server_wsgi_app(self):
        """
        Get the rest server's wsgi app instance
        """
        return self._rest_server.get_rest_server_wsgi_app()

    def register_rest_server_as_service(self):
        """
        Rregister the rest server service
        """
        self.LOG.info('Registering {{cookiecutter.servicename}} rest server from supervisor service')
        if self._rest_server:
            self._rest_server.register_as_service()

    def deregister_rest_server_as_service(self):
        """
        Deregister the rest server service
        """
        self.LOG.info('Deregistering {{cookiecutter.servicename}} rest server from supervisor service')
        if self._rest_server:
            self._rest_server.deregister_as_service()

    #Sample Command
    def get_version(self):
        value = self._{{cookiecutter.servicename}}Manager.get_version()
        self.LOG.info('Version of {{cookiecutter.servicename}}  : %s' % value)
        return value



def main():
    argv = sys.argv[1:]
    datetime.strptime('2021-06-28', '%Y-%m-%d')
    {{cookiecutter.servicename|lower}}app = {{cookiecutter.servicename}}App()

    try:
        returnCode = {{cookiecutter.servicename|lower}}app.run(argv)
        {{cookiecutter.servicename|lower}}app.shutdown_app(argv, returnCode)
        return returnCode
    except (KeyboardInterrupt, SystemExit):
        returnCode = -1
        {{cookiecutter.servicename|lower}}app.shutdown_app(argv, returnCode)
        return 0

if __name__ == '__main__':
    returnCode = main()
    exit(returnCode)