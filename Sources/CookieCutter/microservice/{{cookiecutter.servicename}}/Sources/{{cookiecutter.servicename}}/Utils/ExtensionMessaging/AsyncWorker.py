from inspect import ismodule, isclass
from threading import Event, Lock
from time import sleep

from Utils.BaseMessaging.BaseAsyncWorker import BaseAsyncWorker
from Utils.Core.BaseObject import BaseObject
from Utils.Errors.AsyncWorkerError import *
from Utils.Exception.AsyncWorkerException import AsyncWorkerException
from Utils.ExtensionMessaging.AsyncQueue import AsyncQueue
from Utils.ExtensionMessaging.MessagingBackend import MessagingBackend


class AsyncWorker(BaseAsyncWorker, BaseObject):
    async_worker_control_event_check_frequency_in_secs = 1
    max_wait_time_for_worker_to_stop_in_secs = 120

    def __init__(self, name, worker_spec):
        """
        Constructor of this class
        @param name: Worker name
        @param worker_spec: worker specification
        """
        BaseObject.__init__(self)
        BaseAsyncWorker.__init__(self, name)

        if name is None:
            raise AsyncWorkerException(ASYNC_WORKER_ERROR_INVALID_VALUE_FOR_NAME, name)

        if worker_spec is None:
            raise AsyncWorkerException(ASYNC_WORKER_ERROR_INVALID_WORKER_SPEC_PROPERTY, worker_spec,
                                       'WorkerSpecName: None')

        if worker_spec not in self._config_manager.get_sections():
            raise AsyncWorkerException(ASYNC_WORKER_ERROR_INVALID_WORKER_SPEC_PROPERTY, worker_spec,
                                       'Section not present')

        self._messaging_backend = MessagingBackend.get_instance()

        self._worker_spec_name = worker_spec
        self._control_event = Event()

        self._control_event_check_frequency_in_secs = self.async_worker_control_event_check_frequency_in_secs

        self._task_handlers = None
        self._task_handlers_lock = Lock()

        self._task_queues_lock = Lock()

        self.load_task_queues()

        self._worker_stopped = False

    def _get_object(self, class_name, *args, **kwargs):
        """

        @param class_name:
        @param args:
        @param kwargs:
        @return:
        """
        self._Logger.debug('_get_object function')
        return_object = None
        class_ = None
        if class_name in globals():
            type_ = globals()[class_name]
            if ismodule(type_):
                class_ = getattr(type_, class_name)
            elif isclass(type_):
                class_ = type_
            return_object = class_(*args, **kwargs)
        return return_object

    def load_task_queues(self):
        """

        """
        worker_spec_details = self._config_manager.get_settings(self._worker_spec_name)
        task_queue_str = worker_spec_details.get('TaskQueues')
        if not task_queue_str:
            raise AsyncWorkerException(ASYNC_WORKER_ERROR_INVALID_WORKER_SPEC_PROPERTY, self._worker_spec_name,
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
        Gets the resolved task queues
        @return: list of AsyncQueue objects
        """
        with self._task_queues_lock:
            task_queues = self._task_queues
        return task_queues

    @task_queues.setter
    def task_queues(self, value):
        raise AsyncWorkerException(ASYNC_WORKER_ERROR_CANNOT_SET_TASK_QUEUES_PROPERTY)

    @property
    def task_handlers(self):
        """
        Gets the resolved task handlers
        @return: list of TaskProcessor objects
        """
        with self._task_handlers_lock:
            task_handlers = self._task_handlers
        return task_handlers

    @task_handlers.setter
    def task_handlers(self, value):
        if not value or not isinstance(value, dict):
            raise AsyncWorkerException(ASYNC_WORKER_ERROR_INVALID_VALUE_ASSIGNED_FOR_TASK_HANDLERS, value)
        with self._task_handlers_lock:
            self._task_handlers = value

    def start(self):
        """
        Starts the worker
        Returns:

        """
        if self._task_queues is None:
            raise AsyncWorkerException(ASYNC_WORKER_ERROR_TASK_QUEUES_NOT_SET)

        if not self._task_handlers:
            raise AsyncWorkerException(ASYNC_WORKER_ERROR_TASK_PROCESSOR_NOT_SET)

        try:
            self.before_work_start()
        except Exception as ex:
            self._Logger.error('Error before starting work : %s' % str(ex))
            raise AsyncWorkerException(ASYNC_WORKER_ERROR_BEFORE_START, str(ex))

        self._worker_stopped = False
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
                self._Logger.info('De-queued empty task object from task queue - %s' % task_queue)  # Change to debug
                continue

            self._Logger.info(
                'De-queued task object - %s - from task queue - %s' % (task_object, task_queue))  # Change to debug

            try:
                before_task_process = self.before_task_process(task_queue, task_object)
            except Exception as ex:
                self._Logger.error('Error while executing before_task_process with task object %s, and task queue - '
                                   '%s. Details %s' % (task_queue, task_object, str(ex)))
                before_task_process = False

            if not before_task_process:
                continue

            task_id = task_object.get('jobid')
            task_spec = task_object.get('taskspec')

            self._Logger.info('taskspec - %s' % task_spec)  # Change to debug

            if not task_spec or not task_spec.get('tasktype') or not task_spec.get('taskparams'):
                self._Logger.error('Invalid task spec received')
                continue

            task_type = task_spec.get('tasktype')
            task_params = task_spec.get('taskparams')

            task_handler = self.task_handlers

            if not task_handler.get(task_type):
                self._Logger.error('No task handler found for tasktype - %s' % task_type)
                continue

            try:
                process_object = task_handler[task_type]
                result = process_object.Process(task_params, task_id)
            except Exception as ex:
                self._Logger.error('Error while processing task type - %s with task params - %s . Details - %s'
                                   % (task_type, task_params, str(ex)))
                result = 'Error while processing task type - %s with task params - %s . Details - %s' \
                         % (task_type, task_params, str(ex))
                process_object = None

            if task_id:
                task_queue.set_result(task_id, result)

            try:
                self.after_task_process(process_object, task_id, task_spec, result)
            except Exception as ex:
                self._Logger.error('Error while processing task object - %s, result - %s. Details - %s' %
                                   (task_object, result, str(ex)))

    def before_work_start(self):
        pass

    def stop(self):
        """
        Stops the current running worker
        Returns:

        """
        self._control_event.set()
        time_waited = 0
        while True:
            if self._worker_stopped or time_waited > self.max_wait_time_for_worker_to_stop_in_secs:
                self._Logger.info('Worker Stopped')
                break
            else:
                sleep(2)
                time_waited = time_waited + 2

    def before_task_fetch_from_queue(self):
        return True

    def before_task_process(self, task_queue, task_object):
        return True

    def after_task_process(self, process_object, task_queue, task_object, result):
        return True
