"""
Implements Asynchronous queue for Kafka / Kombu backend
"""
import json

from Utils.BaseMessaging.BaseQueue import BaseQueue
from Utils.Core.BaseObject import BaseObject
from Utils.Errors.AsyncQueueError import *
from Utils.Exception.AsyncQueueException import AsyncQueueException
from Utils.ExtensionMessaging.AsyncDataStore import AsyncDataStore
from Utils.ExtensionMessaging.AsyncTaskSpec import AsyncTaskSpec
from Utils.ExtensionMessaging.MessagingBackend import MessagingBackend


class AsyncQueue(BaseQueue, BaseObject):
    default_queue_backend_url = 'redis://127.0.0.1:6379'
    default_dequeue_timeout_in_secs = 1
    default_result_task_type = 'SetJobResult'

    def __init__(self, async_queue_name):
        """
        Constructor of this class
        Args:
            async_queue_name: string rep of the queue name
        """
        BaseObject.__init__(self)
        BaseQueue.__init__(self, async_queue_name)

        queue_details = self._config_manager.get_settings(async_queue_name)

        self._backend_manager = MessagingBackend.get_instance()

        job_data_store_name = queue_details.get('AsyncDataStore')

        self._results_queue_name = queue_details.get('ResultQueueName')
        self._results_task_type = queue_details.get('ResultTaskType', self.default_result_task_type)

        if job_data_store_name:
            self._job_data_store = AsyncDataStore(job_data_store_name)

    def enqueue(self, async_task):
        """
        Produces / Enqueues / Puts the message into the queue
        Args:
            async_task: async task object

        Returns: uuid value associated to this task

        """
        if async_task is None or not isinstance(async_task, AsyncTaskSpec):
            raise AsyncQueueException(ASYNC_QUEUE_ERROR_INVALID_ITEM_ENQUEUED)

        job_id = None

        item = dict()
        item['taskspec'] = async_task.task_spec

        if self._results_queue_name:
            job_id = self._job_data_store.create_job(async_task)
            item['jobid'] = job_id

        topics, queue_object, _, _ = self._backend_manager.get_queue(self.name)

        if topics is None:
            queue_object.put(item, serializer='json', compression='zlib', retry=True, retry_policy={'max_retries': 5})
        else:
            queue_object.produce(topics, json.dumps(item))
            queue_object.poll(0.1)
            queue_object.flush()

        return job_id

    # @staticmethod
    def acknowledge(self, err, msg):
        """
        Acknowledge call back function used in case of Kafka backend
        Args:
            err: any error when polling
            msg: message received from the queue

        Returns:

        """
        self._Logger.debug("acknowledge")
        if err is not None:
            print("Failed to deliver message: {0}:{1}"
                  .format(msg.value(), err.str()))
        else:
            print("Message produced:{0}".format(msg.value()))

    def dequeue(self):
        """
        Consumes / Dequeues / polls messages from the Queue
        Returns: message that was pulled from the queue

        """
        item = None
        topics, queue_object, consumer_object, _ = self._backend_manager.get_queue(self.name)
        try:
            if topics is None:
                queue_item = queue_object.get(block=False, timeout=self.default_dequeue_timeout_in_secs)
            else:
                # queue_item = consumer_object.consume(timeout=10)
                queue_item = consumer_object.poll(timeout=10)
        except Exception as ex:
            self._Logger.debug('Error while getting an item from Queue / Topic. Queue Probably empty : %s' % str(ex))
            queue_item = None

        if queue_item:
            item = queue_item.payload if topics is None else json.loads(queue_item.value())
            queue_item.ack() if topics is None else consumer_object.commit()

        return item

    def peek(self):
        """
        Looks into the queue to check if any messages are yet to be processed
        This works the same way as dequeue, except in dequeue message will be ACK
        Returns: first message available in queue without consuming it

        """
        item = None
        topics, queue_object, _, _ = self._backend_manager.get_queue(self.name)
        try:
            if topics is None:
                queue_item = queue_object.get(block=False, timeout=self.default_dequeue_timeout_in_secs)
            else:
                queue_item = queue_object.consume(num_messages=1, timeout=self.default_dequeue_timeout_in_secs)
        except Exception as ex:
            self._Logger.warn('Error while getting an item from Queue / Topic. Queue Probably empty : %s' % str(ex))
            queue_item = None

        if queue_item:
            item = queue_item.payload if topics is None else queue_item.value()

        return item

    def empty(self):
        """
        Clears the message in the Queue or Topic
        """
        topics, queue_object, exchange, connection = self._backend_manager.get_queue(self.name)
        if topics is None:
            # channel = connection.channel()
            # channel.queue_purge(queue_object)
            queue_object.clear()
        else:
            queue_object.poll(timeout=self.default_dequeue_timeout_in_secs)

    def get_length(self):
        """
        Gets the count of messages available in the queue
        Returns: count of messages in queue

        """
        topics, queue_object, _, _ = self._backend_manager.get_queue(self.name)
        try:
            queue_length = len(queue_object)
        except Exception as ex:
            self._Logger.error('Error while getting the length queue object: %s' % str(ex))
            queue_length = None

        return queue_length

    def set_result(self, job_id, result):
        """
        Sets the results for the given job id
        Args:
            job_id: uuid produced from enqueue
            result: result / output message that needs to be updated
        """
        if job_id is None:
            raise AsyncQueueException(ASYNC_QUEUE_ERROR_SET_RESULT_INVOKED_WITH_INVALID_JOB_ID, job_id)

        if not self._results_queue_name:
            raise AsyncQueueException(ASYNC_QUEUE_ERROR_SET_RESULT_NOT_SUPPORTED, self.name)

        update_result_task = AsyncTaskSpec(self._results_task_type, {'jobid': job_id, 'result': result})
        results_queue = AsyncQueue(self._results_queue_name)
        results_queue.enqueue(update_result_task)

    def get_job_data_store(self):
        """
        Gets the current data store object
        Returns: AsyncDataStore object

        """
        return self._job_data_store
