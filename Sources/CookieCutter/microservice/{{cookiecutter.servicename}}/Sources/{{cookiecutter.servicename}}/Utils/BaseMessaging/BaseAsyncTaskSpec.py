import abc
import json

from Utils.Errors.BaseAsyncTaskSpecError import BASE_ASYNC_TASK_SPEC_ERROR_INVALID_TASK_TYPE, \
    BASE_ASYNC_TASK_SPEC_ERROR_TASK_TYPE_READONLY, \
    BASE_ASYNC_TASK_SPEC_ERROR_TASK_PARAMS_READONLY, \
    BASE_ASYNC_TASK_SPEC_ERROR_JSON_READONLY, \
    BASE_ASYNC_TASK_SPEC_ERROR_TASK_DICT_READONLY
from Utils.Exception.BaseAsyncTaskSpecException import BaseAsyncTaskSpecException


class BaseAsyncTaskSpec(object, metaclass=abc.ABCMeta):
    TASKSPEC_TYPE_NAME = 'tasktype'
    TASKSPEC_PARAM_NAME = 'taskparams'

    def __init__(self, task_type, task_params=None):
        """
        Constructor of this class
        Args:
            task_params : task parameters
            task_type: string value containing name of the data store
        """
        if task_type is None:
            raise BaseAsyncTaskSpecException(BASE_ASYNC_TASK_SPEC_ERROR_INVALID_TASK_TYPE)
        self._task_type = task_type
        self._task_params = task_params

    @property
    def task_type(self):
        """
        Property which gets the defined task_type
        Returns: task_type

        """
        return self._task_type

    @task_type.setter
    def task_type(self, value):
        """
        Restrict the user to set the value of task type
        Args:
            value:

        Returns:

        """
        raise BaseAsyncTaskSpecException(BASE_ASYNC_TASK_SPEC_ERROR_TASK_TYPE_READONLY)

    @property
    def task_params(self):
        """
        Property which gets the defined task_type
        Returns: task_params

        """
        return self._task_params

    @task_params.setter
    def task_params(self, value):
        """
        Restrict the user to set the value of task param
        Args:
            value:

        Returns:

        """
        raise BaseAsyncTaskSpecException(BASE_ASYNC_TASK_SPEC_ERROR_TASK_PARAMS_READONLY)

    @property
    def task_spec_json(self):
        """
        Property which gets the defined task_spec_json
        Returns: string value of task specification

        """
        return json.dumps(self.task_spec)

    @task_spec_json.setter
    def task_spec_json(self, value):
        """
        Restrict the user to set the value of task_spec_json
        Args:
            value:

        Returns:

        """
        raise BaseAsyncTaskSpecException(BASE_ASYNC_TASK_SPEC_ERROR_JSON_READONLY)

    @property
    def task_spec(self):
        """
        Gets the task specification by constructing the value from task type and task param
        Returns:

        """
        return_dict = dict()
        return_dict[self.TASKSPEC_TYPE_NAME] = self._task_type
        return_dict[self.TASKSPEC_PARAM_NAME] = self._task_params
        return return_dict

    @task_spec.setter
    def task_spec(self, value):
        """
        Restrict the user to set the value of task_spec
        Args:
            value:

        Returns:

        """
        raise BaseAsyncTaskSpecException(BASE_ASYNC_TASK_SPEC_ERROR_TASK_DICT_READONLY)
