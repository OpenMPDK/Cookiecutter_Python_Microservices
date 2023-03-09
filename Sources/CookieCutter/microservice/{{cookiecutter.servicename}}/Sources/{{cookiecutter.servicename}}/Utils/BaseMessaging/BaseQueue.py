import abc

from Utils.Errors.BaseQueueError import BASE_QUEUE_ERROR_LENGTH_READONLY, BASE_QUEUE_ERROR_NAME_READONLY
from Utils.Exception.BaseQueueException import BaseQueueException


class BaseQueue(object):
    def __init__(self, queue_name):
        """
        Constructor of Base Queue class
        Args:
            queue_name: queue name detail
        """
        self._queue_name = queue_name

    @abc.abstractmethod
    def enqueue(self, item):
        """
        Abstract method definition of enqueue
        Args:
            item: item to be enqueued

        Returns:

        """
        pass

    @abc.abstractmethod
    def dequeue(self):
        """
        Abstract method definition of dequeue

        Returns:

        """
        pass

    @abc.abstractmethod
    def peek(self):
        """
        Abstract method definition of peek

        Returns:

        """
        pass

    @abc.abstractmethod
    def empty(self):
        """
        Abstract method definition of empty

        Returns:

        """
        pass

    @abc.abstractmethod
    def get_length(self):
        """
        Abstract method definition of get length

        Returns:

        """
        pass

    @property
    def length(self):
        """
        Property to get the length of queue items

        Returns: queue item length

        """
        return self.get_length()

    @length.setter
    def length(self, value):
        raise BaseQueueException(BASE_QUEUE_ERROR_LENGTH_READONLY)

    @property
    def name(self):
        """
        Gets the queue name
        Returns: string representation of queue name

        """
        return self._queue_name

    @name.setter
    def name(self, value):
        raise BaseQueueException(BASE_QUEUE_ERROR_NAME_READONLY)
