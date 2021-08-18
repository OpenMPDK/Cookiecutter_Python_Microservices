import os
import requests
import socket
import webbrowser

from pkg_resources import resource_filename
from time import sleep
from flask import Flask
from flask import Blueprint
#from flask_autoindex import AutoIndexBluePrint
#from flask_restful_swagger-3 import Api
from flask_restful import Api
from flask_restful_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from gevent.pywsgi import WSGIServer

from CommonLibrary.Core.BaseObject import BaseObject
from CommonLibrary.Core.Singleton import Singleton
from CommonLibrary.Utils.FileUtils import touch_file
from CommonLibrary.Utils.SysUtils import get_logged_in_user
from CommonLibrary.ServiceManagement.ServiceManager import ServiceManager

from {{cookiecutter.servicename}}.Exception.{{cookiecutter.servicename}}Exception import {{cookiecutter.servicename}}Exception
from {{cookiecutter.servicename}}.Errors.ErrorCodes import *
from {{cookiecutter.servicename}}.RestResource.ShutdownServer import ShutdownServer

#Sample Rest resource
from {{cookiecutter.servicename}}.RestResource.GetVersion import GetVersion

class RestServer(BaseObject, Singleton):
    """
    Rest Server Main imlplementation
    """
    default_hostname = '0.0.0'
    default_port = '3586'
    default_rest_server_shutdown_timeout_in_secs = '120'

    rest_server_supervisor_conf_program_name = '{{cookiecutter.servicename}}_REST_SERVER_%s'
    rest_server_state_file_name = '.restserverstate'

    url_shutdown_rest_server = '/v1/shutdownserver'
    url_rest_api_spec = '/v1/spec'
    url_swagger_docs = '/docs'

    url_service_logs = '/servicelogs'

    def __init__(self, rest_server_working_folder_path = None):
        BaseObject.__init__(self)
        self._rest_server_working_folder_path = None
        if rest_server_working_folder_path is None:
            self._rest_server_working_folder_path = os.getcwd()
        else:
            self._rest_server_working_folder_path = rest_server_working_folder_path

        if not os.path.exists(self._rest_server_working_folder_path):
            try:
                os.makedirs(self._rest_server_working_folder_path)
            except Exception as ex:
                self._Logger.error('Cannot Create working folder path for rest server. Details :%s' % str(ex))
                raise {{cookiecutter.servicename}}Exception(REST_SERVER_WORKING_FOLDER_CREATE_FAILURE, str(ex)) 

        self._rest_server_state_file_path = os.path.join(self._rest_server_working_folder_path, RestServer.rest_server_state_file_name)

        self._rest_app = None
        self._rest_api_v1 = None

        shutdowntimeout = self._config_manager.get_setting_value('Rest_Server','Shutdown_Timeout_In_Secs')
        if not shutdowntimeout:
            shutdowntimeout = RestServer.default_rest_server_shutdown_timeout_in_secs

        self._rest_server_shutdown_timeout_in_secs = int(shutdowntimeout)

        self._rest_server_url_prefix = self._config_manager.get_setting_value('Rest_Server', 'URL_Prefix')

        self._ServiceManager = ServiceManager.get_instance()

        rest_server_supervisor_conf_template = resource_filename('{{cookiecutter.servicename}}',
            'Conf/{{cookiecutter.servicename}}_Rest_Server_Supervisor.conf'
        )
        self._rest_server_supervisor_conf_template = None
        with open(rest_server_supervisor_conf_template) as file_handler:
            self._rest_server_supervisor_conf_template = file_handler.read().replace('${servicelogs}', self._ServiceManager.get_supervisor_service_logs_path()) \
                                                                            .replace('${progname}',self.rest_server_supervisor_conf_program_name %get_logged_in_user())

        self._server_object = None


    def _check_rest_server_status(self):
        """
        Checks if the rest service is running or not
        """
        return os.path.exists(self._rest_server_state_file_path)

    def _create_rest_server_state_file(self):
        """
        Creates a file to show rest server status
        """
        touch_file(self._rest_server_state_file_path)

    def _delete_rest_server_state_file(self):
        """
        Deletes a file to show rest server status (i.e rest server is not running)
        """
        if os.path.exists(self._rest_server_state_file_path):
            self._Logger.info('Removing Rest Server State File Path')
            os.remove(self._rest_server_state_file_path)
            self._Logger.info('Removed Rest Server State File Path')

    def get_rest_server_wsgi_app(self):
        """
        Returngs WSGI app instance, if the instance is not available, it will create the instance
        """
        if not self._rest_app:
            self._prepare_rest_server()

        return self._rest_app


    def _prepare_rest_server(self):
        """
        Prepares the Flask / WSGI App instance
        """
        self._rest_app = Flask(__name__)

        if self._rest_server_url_prefix:
            self._rest_app.config['APPLICATION_ROOT'] = self._rest_server_url_prefix
            self._rest_app.wsgi_app = DispatcherMiddleware(
                Flask('DummyRootApp'), 
                {self._rest_server_url_prefix: self._rest_app.wsgi_app}
            )

        '''
        For Enhaced Swagger
        servers = [
            {'url' : 'http://{0}:{1}{2}'.format(self._get_local_ip(), self.get_rest_server_port(), self._rest_server_url_prefix)},
            {'url' : 'http://{0}:{1}{2}'.format(self.get_rest_server_host(), self.get_rest_server_port(), self._rest_server_url_prefix)},
        ]

        
        #Attaching swagger docs
        self._rest_api_v1 = Api(
            self._rest_app,
            version='0.1',
            api_spec_url=self.url_rest_api_spec,
            servers=servers,
            description='{{cookiecutter.description}}',
            title='{{cookiecutter.servicename}}'
        )
        '''
        self._Logger.info("Attaching swagger doc support")
        self._rest_api_v1 = swagger.docs(Api(self._rest_app), apiVersion='0.1', api_spec_url=self.url_rest_api_spec)

        self._Logger.info("Providing support for Cross Origin Resource Sharing")
        CORS(self._rest_app)

        #Adding Rest resources to Flask
        self._register_resources_v1()

        '''
        For Enhaced Swagger

        swagger_ui_blue_print = get_swaggerui_blueprint(
            self._rest_server_url_prefix+self.url_swagger_docs,
            self._rest_server_url_prefix+self.url_rest_api_spec+".json",
            config={
                'app_name':'{{cookiecutter.servicename}}'
            }            
        )
        self._rest_app.register_blueprint(swagger_ui_blue_print, url_prefix=self.url_swagger_docs)
        '''


    def start_rest_server(self, debug_mode = False, force_start = False, **server_options):
        """
        Starts the rest server
        """
        self._prepare_rest_server()

        rest_server_host = self.get_rest_server_host()
        rest_server_port = self.get_rest_server_port()

        if self._check_rest_server_status():
            raise {{cookiecutter.servicename}}Exception(REST_SERVER_ALREADY_RUNNING)

        self._create_rest_server_state_file()

        self._Logger.info('Launching {{cookiecutter.servicename}} Rest Server. Details :')
        self._Logger.info('     Host : %s' % rest_server_host)
        self._Logger.info('     Port : %s' % rest_server_port)
        self._Logger.info('     Debug Mode : %s' % debug_mode)
        self._Logger.info('     Server Options : %s' % server_options)

        try:
            self._server_object =  WSGIServer((rest_server_host, rest_server_port), self._rest_app)
            {% if cookiecutter.server_mode == 'wsgi' %}
            self._server_object.serve_forever()
            {% elif cookiecutter.server_mode == 'flask' %}
            self._rest_app.run(rest_server_host, rest_server_port)
            {% endif %}
            self._Logger.info('Server shutdown')
            self._delete_rest_server_state_file()
        except Exception as ex:
            self._Logger.debug('Error while starting rest server. Details : %s'% str(ex))
            self._delete_rest_server_state_file()
            raise {{cookiecutter.servicename}}Exception(ERROR_WHILE_STARTING_REST_SERVER, str(ex))

    def _get_rest_server_url(self):
        """
        Gets the Rest server URL
        """
        host = self.get_rest_server_host()
        port = self.get_rest_server_port()

        if host == self.default_hostname:
            host = '127.0.0.1'

        return 'http://%s:%s' % (host, port)

    def get_rest_server_host(self):
        """
        Gets the Rest server host
        """
        host_from_config = self._config_manager.get_setting_value('Rest_Server','Host')
        if not host_from_config:
            host_from_config = self.default_hostname

        return host_from_config

    def get_rest_server_port(self):
        """
        Gets the Rest server port
        """
        port_from_config = self._config_manager.get_setting_value('Rest_Server','Port')
        if not port_from_config:
            port_from_config = self.default_port

        return int(port_from_config)

    def set_rest_server_host(self, host_name):
        """
        Sets the Rest server host
        """
        if ((not host_name) or (type(host_name) != str)):
            raise {{cookiecutter.servicename}}Exception(INVALID_REST_SERVER_HOST, str(ex)) 
        
        self._config_manager.set_setting_value('Rest_server', 'Host', host_name)

    def set_rest_server_port(self, port_no):
        """
        Sets the Rest server port
        """
        if ((not port_no) or (not port_no.isdigit()) or ((int(port_no) < 1024) or (int(port_no)> 65535))):
            raise {{cookiecutter.servicename}}Exception(INVALID_REST_SERVER_PORT, str(ex)) 
        
        self._config_manager.set_setting_value('Rest_server', 'Port', port_no)

    def _get_local_ip(self):
        """
        Get Local IP Address using socket
        """
        try:
            ip_address = [(s.connection(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
        except Exception as ex:
            ip_address = self.get_rest_server_host()
        return ip_address

    def stop_rest_server(self, ignore_stop_failure):
        """
        Stops the ruunning Rest Server
        """
        if not self._check_rest_server_status():
            if not ignore_stop_failure:
                raise {{cookiecutter.servicename}}Exception(REST_SERVER_NOT_RUNNING, str(ex))  
            else:
                return
        rest_server_url = self._get_rest_server_url()
        timeout = False

        if self._server_object:
            self._server_object.stop()
            self._delete_rest_server_state_file()
        else:
            shutdown_url = '%s%s' % (rest_server_url, self.url_shutdown_rest_server)
            try:
                requests.post(shutdown_url)
                self._Logger.info('Posted a shutdown request')
            except Exception as ex:
                if not ignore_stop_failure:
                    self._Logger.info('Error while posting shutdown request. Details: %s' % str(ex))
                    raise {{cookiecutter.servicename}}Exception(REST_SERVER_SHUTDOWN_REQUEST_FAILED, str(ex))  
                else:
                    self._Logger.warning('Ignoring failure to stop Rest Server')
                    self._delete_rest_server_state_file()
                    return
            self._Logger.debug('Proceeding to wait for requst to be completed for %s minutes' % self._rest_server_shutdown_timeout_in_secs)
            time_waited  = 0
            while (os.path.exists(self._rest_server_state_file_path)):
                sleep(1)
                time_waited += 1
                if time_waited > self._rest_server_shutdown_timeout_in_secs:
                    timeout = True
                    break

            if not timeout:
                self._Logger.info('Rest server shutdown complete')
            else:
                if not ignore_stop_failure:
                    raise {{cookiecutter.servicename}}Exception(REST_SERVER_SHUTDOWN_REQUEST_TIMEDOUT, str(ex))   
                else:
                    self._Logging.warning('Ignoring failure to stop Rest Server')
                    self._delete_rest_server_state_file()
            return

    def _register_shutdown_rest_resource(self):
        """
        Registers shutdown api as part of Rest server available API
        """
        self._rest_api_v1.add_resource(ShutdownServer,self.url_shutdown_rest_server, resource_class_kwargs={'serverObj':self._server_object})

    def register_as_supervisor_service(self):
        """
        Registers Rest server as a supervisor servie
        """
        self._ServiceManager.regiser_supervisor_service(self._rest_server_supervisor_conf_template)

    def deregister_as_supervisor_service(self):
        """
        Registers Rest server as a supervisor servie
        """
        self._ServiceManager.deregister_supervisor_service(self.rest_server_supervisor_conf_program_name % get_logged_in_user())

    def show_api_spec(self):
        """
        Shows API Specification in browser
        """
        if self._check_rest_server_status():
            api_spec_url = self._get_rest_server_url() + RestServer.url_rest_api_spec + '.html'
            webbrowser.open_new_tab(api_spec_url)
        else:
            raise {{cookiecutter.servicename}}Exception(REST_SERVER_NOT_RUNNING)  

    def _register_resources_v1(self):
        #Shutdown Rest Resource
        self._register_shutdown_rest_resource()
        #SampleRestResource
        self._rest_api_v1.add_resource(GetVersion,'/v1/get_version')
        #Expose your rest resources here