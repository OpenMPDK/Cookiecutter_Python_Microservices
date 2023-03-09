import abc

from Utils.Errors.BaseAsyncDataStoreError import BASE_ASYNC_DATA_STORE_ERROR_NAME_READONLY
from Utils.Exception.BaseAsyncDataStoreException import BaseAsyncDataStoreException


class BaseAsyncDataStore(object, metaclass=abc.ABCMeta):
    def __init__(self, task_store_name):
        """
        Constructor of this class
        Args:
            task_store_name: string value containing name of the data store
        """
        self._task_store_name = task_store_name

    @abc.abstractmethod
    def create_job(self, task_spec):
        """
        Abstractmethod create job, will be implemented by the extended classes
        Args:
            task_spec: task specification details
        """
        pass

    @abc.abstractmethod
    def get_job(self, job_id):
        """
        Abstractmethod get job, will be implemented by the extended classes
        Args:
            job_id: information of the task or result which needs to be fetched
        """
        pass

    @abc.abstractmethod
    def set_result(self, task_id, result):
        """
        Abstractmethod set result, will be implemented by the extended classes
        Args:
            task_id: uuid of task, for which results need to be updated
            result: status output / actual response of the task
        """
        pass

    @abc.abstractmethod
    def set_task(self, task_id, task_spec):
        """
        Abstractmethod set task, will be implemented by the extended classes
        Args:
            task_id: uuid of task, for which results need to be updated
            task_spec: Specification of the task that needs to be performed

        Returns: None

        """
        pass

    @property
    def name(self):
        """
        Name Property used to get the data store name
        Returns: data store name

        """
        return self._task_store_name

    @name.setter
    def name(self, value):
        """
        Property for setting the value of data store name
        Args:
            value: data store value

        Returns:

        """
        raise BaseAsyncDataStoreException(BASE_ASYNC_DATA_STORE_ERROR_NAME_READONLY)
