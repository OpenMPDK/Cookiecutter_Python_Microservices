"""

"""
from Utils.Core.BaseObject import BaseObject
from Utils.Core.Singleton import Singleton
from Utils.Exception.AsyncWorkerManagerException import AsyncWorkerManagerException
from Utils.ServiceManagement.ServiceManager import ServiceManager
from Utils.Errors.AsyncWorkerManagerError import *
from Utils.Utils.SysUtils import get_logged_in_user


class AsyncWorkerManager(BaseObject, Singleton):

    def __init__(self):
        BaseObject.__init__(self)
        self._service_manager = ServiceManager.get_instance()

    def register_workers(self, worker_spec_name, worker_supervisor_conf_template):
        """
        Register the worker automatically based on the specification and configuration details
        @param worker_spec_name: worker spec name
        @param worker_supervisor_conf_template: worker spec configuration template
        """
        if not worker_spec_name or worker_spec_name not in self._config_manager.get_sections():
            raise AsyncWorkerManagerException(ASYNC_WORKER_MANAGER_ERROR_INVALID_WORKER_SPEC_NAME, worker_spec_name)

        if not worker_supervisor_conf_template:
            raise AsyncWorkerManagerException(ASYNC_WORKER_MANAGER_ERROR_INVALID_WORKER_SUPERVISOR_CONF_TEMPLATE,
                                              worker_supervisor_conf_template)

        workers_str = self._config_manager.get_setting_value(worker_spec_name, 'keys')
        workers = None

        if workers_str:
            workers = [x.strip() for x in workers_str.split(',')]

        if workers:
            for worker in workers:
                worker_settings = self._config_manager.get_settings(worker)

                name_format = worker_settings.get('NameFormat')
                number_of_workers = int(worker_settings.get('NumWorkers', '1'))
                worker_spec = worker_settings.get('WorkerSpec')
                worker_user_id = worker_settings.get('UserID', None)

                for count in range(0, number_of_workers):
                    worker_name = name_format.replace('${n}', str(count + 1))
                    self._setup_worker_service(worker_name, worker_spec, worker_supervisor_conf_template,
                                               worker_user_id)

    def deregister_workers(self, worker_spec_name):
        """
        Unregisters a worker which has been already created and registered
        @param worker_spec_name: name of the worker
        """
        if not worker_spec_name or worker_spec_name not in self._config_manager.get_sections():
            raise AsyncWorkerManagerException(ASYNC_WORKER_MANAGER_ERROR_INVALID_WORKER_SPEC_NAME, worker_spec_name)

        workers_str = self._config_manager.get_setting_value(worker_spec_name, 'keys')
        workers = None

        if workers_str:
            workers = [x.strip() for x in workers_str.split(',')]

        if workers:
            for worker in workers:
                worker_settings = self._config_manager.get_settings(worker)

                name_format = worker_settings.get('NameFormat')
                number_of_workers = int(worker_settings.get('NumWorkers', '1'))

                for count in range(0, number_of_workers):
                    worker_name = name_format.replace('${n}', str(count + 1))
                    service_name = '%s_%s' % (worker_name, get_logged_in_user())

                    if self._service_manager.is_supervisor_service_registered(service_name):
                        self._service_manager.deregister_supervisor_service(service_name)

    def _setup_worker_service(self, worker_name, worker_spec, worker_supervisor_conf_template, worker_user_id=None):
        """
        Sets up the worker as a daemon service using service manager
        @param worker_name: name of the worker
        @param worker_spec: specification of the worker
        @param worker_supervisor_conf_template: template details
        @param worker_user_id: username for which worker needs to be registered
        """
        service_name = '%s_%s' % (worker_name, get_logged_in_user())
        supervisor_conf_template = worker_supervisor_conf_template.replace('${progname}', service_name) \
            .replace('${workername}', worker_name) \
            .replace('${workerspec}', worker_spec) \
            .replace('${servicelogs}', self._service_manager.get_supervisor_service_logs_path())

        if worker_user_id:
            supervisor_conf_template = supervisor_conf_template.replace('${userID}', worker_user_id)

        if not self._service_manager.is_supervisor_service_registered(service_name):
            self._service_manager.register_supervisor_service(supervisor_conf_template)

    def stop_workers(self, worker_spec_name):
        """
        Stops the specified worker using service manager
        @param worker_spec_name:name of the worker
        """
        if not worker_spec_name or worker_spec_name not in self._config_manager.get_sections():
            raise AsyncWorkerManagerException(ASYNC_WORKER_MANAGER_ERROR_INVALID_WORKER_SPEC_NAME, worker_spec_name)

        workers_str = self._config_manager.get_setting_value(worker_spec_name, 'keys')
        workers = None

        if workers_str:
            workers = [x.strip() for x in workers_str.split(',')]

        if workers:
            for worker in workers:
                worker_settings = self._config_manager.get_settings(worker)

                name_format = worker_settings.get('NameFormat')
                number_of_workers = int(worker_settings.get('NumWorkers', '1'))

                for count in range(0, number_of_workers):
                    worker_name = name_format.replace('${n}', str(count + 1))
                    service_name = '%s_%s' % (worker_name, get_logged_in_user())

                    self._service_manager.stop_supervisor_service(service_name)

    def start_workers(self, worker_spec_name):
        """
        Starts the worker using service manager
        Args:
            worker_spec_name: name of the worker

        Returns:

        """
        if not worker_spec_name or worker_spec_name not in self._config_manager.get_sections():
            raise AsyncWorkerManagerException(ASYNC_WORKER_MANAGER_ERROR_INVALID_WORKER_SPEC_NAME, worker_spec_name)

        workers_str = self._config_manager.get_setting_value(worker_spec_name, 'keys')
        workers = None

        if workers_str:
            workers = [x.strip() for x in workers_str.split(',')]

        if workers:
            for worker in workers:
                worker_settings = self._config_manager.get_settings(worker)

                name_format = worker_settings.get('NameFormat')
                number_of_workers = int(worker_settings.get('NumWorkers', '1'))

                for count in range(0, number_of_workers):
                    worker_name = name_format.replace('${n}', str(count + 1))
                    service_name = '%s_%s' % (worker_name, get_logged_in_user())

                    self._service_manager.start_supervisor_service(service_name)


