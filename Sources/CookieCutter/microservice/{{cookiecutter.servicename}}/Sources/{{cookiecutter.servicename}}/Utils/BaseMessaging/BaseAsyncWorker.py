import abc

from Utils.Errors.BaseAsyncWorkerError import *
from Utils.Exception.BaseAsyncWorkerException import BaseAsyncWorkerException


class BaseAsyncWorker(object, metaclass=abc.ABCMeta):
    def __init__(self, name):
        """
        Constructor of this class
        Args:
            name : name of the async worker
        """
        self._name = name
        self._task_queues = None
        self._task_handlers = None

    @property
    def task_queues(self):
        """
        Gets the value of task queue
        Returns: task_queue

        """
        return self._task_queues

    @task_queues.setter
    def task_queues(self, value):
        """
        Restricting value to be set for task queue
        Args:
            value:
        """
        self._task_queues = value

    @property
    def name(self):
        """
        Gets the name of the Async worker
        Returns: string representation of async worker name

        """
        return self._name

    @name.setter
    def name(self, value):
        """
        Restricting value to be set for async worker name
        Args:
            value:
        """
        raise BaseAsyncWorkerException(BASE_ASYNC_WORKER_ERROR_NAME_READONLY)

    @property
    def task_handlers(self):
        """
        Gets the task handlers
        Returns: task handlers

        """
        return self._task_handlers

    @task_handlers.setter
    def task_handlers(self, value):
        """
        Sets value to the task handler
        Args:
            value:

        Returns: None

        """
        self._task_handlers = value

    @abc.abstractmethod
    def start(self):
        """
        Starts the async worker process
        """
        pass

    @abc.abstractmethod
    def stop(self):
        """
        Stop the async worker
        """
        pass

    @abc.abstractmethod
    def before_work_start(self):
        """
        Pre setup before actually starting the async worker start method
        """
        pass

    @abc.abstractmethod
    def before_task_fetch_from_queue(self):
        """
        Pre setup before actually picking the messages from the queue
        """
        pass

    @abc.abstractmethod
    def before_task_process(self, task_queue, task_object):
        """
        Pre setup before processing the task
        Args:
            task_queue: task queue detail
            task_object: task handler object
        """
        pass

    @abc.abstractmethod
    def after_task_process(self, process_object, task_queue, task_object, result):
        """
        Post-processing once the task execution is completed
        Args:
            process_object: object of the task processor
            task_queue: task queue detail
            task_object: task handler object details
            result: results to be posted back
        """
        pass
