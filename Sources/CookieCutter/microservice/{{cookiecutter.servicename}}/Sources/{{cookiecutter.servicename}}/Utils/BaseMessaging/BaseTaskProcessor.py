import abc

from Utils.Core.BaseObject import BaseObject
from Utils.Errors.BaseTaskProcessorError import BASE_TASK_PROCESSOR_ERROR_TASK_TYPE_READONLY
from Utils.Exception.BaseTaskProcessorException import BaseTaskProcessorException


class BaseTaskProcessor(BaseObject, metaclass=abc.ABCMeta):

    @property
    def task_type(self):
        """
        Gets the defined task type
        Returns:

        """
        return self._get_task_type()

    @task_type.setter
    def task_type(self, value):
        raise BaseTaskProcessorException(BASE_TASK_PROCESSOR_ERROR_TASK_TYPE_READONLY)

    @abc.abstractmethod
    def _get_task_type(self):
        """
        Abstract method definition of get task type
        Returns:

        """
        pass

    @abc.abstractmethod
    def process(self, process_params, job_id=None):
        """
        Abstract method definition of process the task
        Args:
            process_params: message to be processed
            job_id: job id or token id to tract the processing
        """
        pass
