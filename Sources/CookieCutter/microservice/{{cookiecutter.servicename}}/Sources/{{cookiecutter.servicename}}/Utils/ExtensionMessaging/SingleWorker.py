from threading import Event, Lock

from Utils.BaseMessaging.BaseAsyncWorker import BaseAsyncWorker
from Utils.Core.BaseObject import BaseObject
from Utils.Errors.SingleWorkerError import *
from Utils.Exception.SingleWorkerException import SingleWorkerException
from Utils.ExtensionMessaging.AsyncQueue import AsyncQueue
from Utils.ExtensionMessaging.MessagingBackend import MessagingBackend


class SingleWorker(BaseAsyncWorker, BaseObject):

    simple_worker_control_event_check_frequency_in_secs = 1

    def __init__(self, name, worker_spec):
        """

        @param name:
        @param worker_spec:
        """
        BaseObject.__init__(self)
        BaseAsyncWorker.__init__(self, name)

        if name is None:
            raise SingleWorkerException(SINGLE_WORKER_ERROR_INVALID_VALUE_FOR_NAME, name)

        if worker_spec is None:
            raise SingleWorkerException(SINGLE_WORKER_ERROR_INVALID_WORKER_SPEC_PROPERTY, worker_spec,
                                        'WorkerSpecName: None')

        if worker_spec not in self._config_manager.get_sections():
            raise SingleWorkerException(SINGLE_WORKER_ERROR_INVALID_WORKER_SPEC_PROPERTY, worker_spec,
                                        'Section not present')

        self._messaging_backend = MessagingBackend.get_instance()

        self._worker_spec_name = worker_spec
        self._control_event = Event()

        self._control_event_check_frequency_in_secs = self.simple_worker_control_event_check_frequency_in_secs

        self._task_handlers = None
        self._task_handlers_lock = Lock()

        self._task_queues_lock = Lock()

        self.load_task_queues()

    def load_task_queues(self):
        """
        Loads all the task queues object based on the definition available in the TaskQueue settings in
        configuration file
        """
        worker_spec_details = self._config_manager.get_settings(self._worker_spec_name)
        task_queue_str = worker_spec_details.get('TaskQueues')
        if not task_queue_str:
            raise SingleWorkerException(SINGLE_WORKER_ERROR_INVALID_WORKER_SPEC_PROPERTY, self._worker_spec_name,
                                        'TaskQueues not present')

        task_queue_names = [x.strip() for x in task_queue_str.split(',')]
        task_queue_list = list()
        for task_queue_name in task_queue_names:
            task_queue_object = AsyncQueue(task_queue_name)
            task_queue_list.append(task_queue_object)

        with self._task_queues_lock:
            self._task_queues = task_queue_list

    @property
    def task_queues(self):
        """
        Gets the task queue objects
        @return: task queue object
        """
        with self._task_queues_lock:
            task_queues = self._task_queues
        return task_queues

    @task_queues.setter
    def task_queues(self, value):
        raise SingleWorkerException(SINGLE_WORKER_ERROR_CANNOT_SET_TASK_QUEUES_PROPERTY)

    @property
    def task_handlers(self):
        """
        Gets the task handler objects
        @return: object of task handler
        """
        with self._task_handlers_lock:
            task_handlers = self._task_handlers
        return task_handlers

    @task_handlers.setter
    def task_handlers(self, value):
        """
        sets the task handler objects
        @param value:
        """
        if not value or not isinstance(value, dict):
            raise SingleWorkerException(SINGLE_WORKER_ERROR_INVALID_VALUE_ASSIGNED_FOR_TASK_HANDLERS, value)
        with self._task_handlers_lock:
            self._task_handlers = value

    def start(self):
        """
        Starts the worker
        """
        if self._task_queues is None:
            raise SingleWorkerException(SINGLE_WORKER_ERROR_TASK_QUEUES_NOT_SET)

        if not self._task_handlers:
            raise SingleWorkerException(SINGLE_WORKER_ERROR_TASK_PROCESSOR_NOT_SET)

        try:
            self.before_work_start()
        except Exception as ex:
            self._Logger.error('Error before starting work : %s' % str(ex))
            raise SingleWorkerException(SINGLE_WORKER_ERROR_BEFORE_START, str(ex))

        while not self._control_event.wait(self._control_event_check_frequency_in_secs):
            try:
                before_task_fetch = self.before_task_fetch_from_queue()
            except Exception as ex:
                self._Logger.error('Error while executing before_task_fetch_from_queue : %s' % str(ex))
                before_task_fetch = False

            if not before_task_fetch:
                continue

            task_queue = None
            task_object = None

            task_queues = self.task_queues
            self._Logger.info('Number of task queues configured %s' % len(task_queues))
            for queue in task_queues:
                self._Logger.info('Checking queue - %s ' % queue.name)  # Change to debug
                task_queue = queue
                task_object = task_queue.dequeue()
                if task_object:
                    self._Logger.info('task object - %s' % task_object)
                    break

            if not task_object:
                self._Logger.info('De-queued empty task object from task queue - %s' % task_queue)
                # Change to debug
                continue

            self._Logger.info('De-queued task object - %s - from task queue - %s' % (task_object, task_queue))
            # Change to debug

            try:
                before_task_process = self.before_task_process(task_queue, task_object)
            except Exception as ex:
                self._Logger.error('Error while executing before_task_process with task object %s, and task queue - '
                                   '%s. Details %s' % (task_queue, task_object, str(ex)))
                before_task_process = False

            if not before_task_process:
                continue

            task_handler_name = list(self.task_handlers.keys())[0]
            task_handler = self.task_handlers[task_handler_name]

            try:
                result = task_handler.Process(task_object)
            except Exception as ex:
                self._Logger.error('Error while processing task object - %s. Details - %s' % (task_object, str(ex)))
                result = 'Error while processing task object - %s. Details - %s' % (task_object, str(ex))

            try:
                self.after_task_process(task_handler, task_queue, task_object, result)
            except Exception as ex:
                self._Logger.error('Error while processing task object - %s, result - %s. Details - %s' %
                                   (task_object, result, str(ex)))

    def before_work_start(self):
        pass

    def stop(self):
        """
        Stops the worker
        """
        self._control_event.set()

    def before_task_fetch_from_queue(self):
        return True

    def before_task_process(self, task_queue, task_object):
        return True

    def after_task_process(self, process_obj, task_queue, task_object, result):
        return True
