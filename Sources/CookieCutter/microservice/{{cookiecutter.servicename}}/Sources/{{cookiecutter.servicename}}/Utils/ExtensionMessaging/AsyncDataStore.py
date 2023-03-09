"""
Created on Aug 1, 2021

@author: admin
"""
import json
import uuid

import redis

from Utils.BaseMessaging.BaseAsyncDataStore import BaseAsyncDataStore
from Utils.Core.BaseObject import BaseObject
from Utils.Errors.AsyncDataStoreError import ASYNC_DATA_STORE_ERROR_INVALID_DATASTORE_NAME, \
    ASYNC_DATA_STORE_ERROR_JOB_ID_NOT_AVAILABLE, \
    ASYNC_DATA_STORE_ERROR_INVALID_JOB_ID, ASYNC_DATA_STORE_ERROR_INVALID_TASK_SPEC, \
    ASYNC_DATA_STORE_ERROR_CANNOT_CONNECT_TO_DATASTORE
from Utils.Exception.AsyncDataStoreException import AsyncDataStoreException
from Utils.ExtensionMessaging.AsyncTaskSpec import AsyncTaskSpec
from Utils.ExtensionMessaging.MessagingBackend import MessagingBackend


class AsyncDataStore(BaseAsyncDataStore, BaseObject):
    DATASTORE_TASK_SPEC_KEY_NAME = 'taskspec'
    DATASTORE_RESULT_KEY_NAME = 'result'
    DATASTORE_ID_KEY_NAME = 'id'

    def __init__(self, data_store_name):
        """
        Constructor of this class

        Args:
            data_store_name: string representation of data store name
        """
        if not data_store_name:
            raise AsyncDataStoreException(ASYNC_DATA_STORE_ERROR_INVALID_DATASTORE_NAME, data_store_name)

        BaseObject.__init__(self)
        BaseAsyncDataStore.__init__(self, data_store_name)

        data_store_backend_name = self._config_manager.get_setting_value(data_store_name, 'DataStoreBackendName')

        if not data_store_backend_name:
            data_store_backend_name = self.name

        self._data_store_backend_name = data_store_backend_name
        self._job_data_store = None

        self._MessagingBackend = MessagingBackend.get_instance()

        self._load_backend_settings()

    def _load_backend_settings(self):
        """
        Loads the data store connection string from Messaging Backend class and tried to establish redis connection
        """

        job_data_store_connection_pool, job_data_store_settings = self._MessagingBackend. \
            get_datastore_backend_connection(self._data_store_backend_name)

        self._job_data_store = redis.StrictRedis(job_data_store_settings['Host'],
                                                 job_data_store_settings['Port'],
                                                 job_data_store_settings['DB'],
                                                 job_data_store_settings['Password'],
                                                 connection_pool=job_data_store_connection_pool)

        try:
            _ = self._job_data_store.info()

        except redis.ConnectionError as ex:
            raise AsyncDataStoreException(ASYNC_DATA_STORE_ERROR_CANNOT_CONNECT_TO_DATASTORE, str(ex))

    def create_job(self, task_spec):
        """
        Creates a job ID using UUID string and sets the value in redis datastore

        Args:
            task_spec: task specification
        """
        if (task_spec is None) or (not isinstance(task_spec, AsyncTaskSpec)):
            raise AsyncDataStoreException(ASYNC_DATA_STORE_ERROR_INVALID_TASK_SPEC, task_spec)

        job_id = str(uuid.uuid4())
        task_key = '%s:%s:%s' % (self.name, job_id, self.DATASTORE_TASK_SPEC_KEY_NAME)
        self._job_data_store.set(task_key, task_spec.task_spec_json)
        return job_id

    def get_job(self, job_id):
        """
        Gets the details of job_id from redis data store

        Args:
            job_id (object): unique identifier for the job or task
        """
        if job_id is None:
            raise AsyncDataStoreException(ASYNC_DATA_STORE_ERROR_INVALID_JOB_ID, job_id)
        job_task_key = '%s:%s:%s' % (self.name, job_id, self.DATASTORE_TASK_SPEC_KEY_NAME)
        job_task = self._job_data_store.get(job_task_key)

        if not job_task:
            raise AsyncDataStoreException(ASYNC_DATA_STORE_ERROR_JOB_ID_NOT_AVAILABLE, job_id)

        job_result_key = '%s:%s:%s' % (self.name, job_id, self.DATASTORE_RESULT_KEY_NAME)
        job_result = self._job_data_store.get(job_result_key)

        job = dict()

        job[self.DATASTORE_ID_KEY_NAME] = job_id
        if job_task:
            job[self.DATASTORE_TASK_SPEC_KEY_NAME] = job_task
        else:
            job[self.DATASTORE_TASK_SPEC_KEY_NAME] = None
        if job_result:
            job[self.DATASTORE_RESULT_KEY_NAME] = job_result
        else:
            job[self.DATASTORE_RESULT_KEY_NAME] = None

        return job

    def get_job_status(self, job_id):
        """
        Gets the status of job_id from redis data store

        Args:
            job_id (object): unique identifier for the job or task
        """
        if job_id is None:
            raise AsyncDataStoreException(ASYNC_DATA_STORE_ERROR_INVALID_JOB_ID, job_id)

        job_task_key = '%s:%s:%s' % (self.name, job_id, self.DATASTORE_TASK_SPEC_KEY_NAME)
        job_task = self._job_data_store.get(job_task_key)

        if not job_task:
            raise AsyncDataStoreException(ASYNC_DATA_STORE_ERROR_JOB_ID_NOT_AVAILABLE, job_id)

        job_result_key = '%s:%s:%s' % (self.name, job_id, self.DATASTORE_RESULT_KEY_NAME)
        job_result = self._job_data_store.get(job_result_key)

        if job_result:
            return_result = json.loads(job_result)
        else:
            return_result = None

        return return_result

    def set_result(self, job_id, result):
        """
        Updates the result for a given job id in redis datastore

        Args:
            result: output message that needs to be set for the specified task
            job_id (object): unique identifier for the job or task
        """

        if job_id is None:
            raise AsyncDataStoreException(ASYNC_DATA_STORE_ERROR_INVALID_JOB_ID, job_id)

        job_task_key = '%s:%s:%s' % (self.name, job_id, self.DATASTORE_TASK_SPEC_KEY_NAME)
        job_task = self._job_data_store.get(job_task_key)

        if not job_task:
            raise AsyncDataStoreException(ASYNC_DATA_STORE_ERROR_JOB_ID_NOT_AVAILABLE, job_id)

        job_result_key = '%s:%s:%s' % (self.name, job_id, self.DATASTORE_RESULT_KEY_NAME)

        self._job_data_store.set(job_result_key, json.dumps(result))

    def set_task(self, job_id, task_spec):
        """
        Updates the task_spec for a given job id in redis datastore

        Args:
            task_spec: task specification that needs to be processed
            job_id (object): unique identifier for the job or task
        """

        if job_id is None:
            raise AsyncDataStoreException(ASYNC_DATA_STORE_ERROR_INVALID_JOB_ID, job_id)

        job_task_key = '%s:%s:%s' % (self.name, job_id, self.DATASTORE_TASK_SPEC_KEY_NAME)
        job_task = self._job_data_store.get(job_task_key)

        if not job_task:
            raise AsyncDataStoreException(ASYNC_DATA_STORE_ERROR_JOB_ID_NOT_AVAILABLE, job_id)

        self._job_data_store.set(job_task_key, task_spec.task_spec_json)
