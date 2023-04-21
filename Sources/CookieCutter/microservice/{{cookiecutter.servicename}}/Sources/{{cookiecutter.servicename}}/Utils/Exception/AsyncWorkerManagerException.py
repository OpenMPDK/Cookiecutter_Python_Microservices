"""
Created on Aug 1, 2021

@author: admin
"""
from Utils.Exception.BaseException import BaseException
from Utils.Errors.AsyncWorkerManagerError import AsyncWorkerManagerErrorMessages


class AsyncWorkerManagerException(BaseException):

    def __init__(self, err_code=None, *err_msg_params):
        """
        Constructor of AsyncWorkerManagerException
        Args:
            err_code: error code
            *err_msg_params: error message details
        """

        if (hasattr(self, self.USR_ERR_MSG_PROP_NAME)) and (getattr(self, self.USR_ERR_MSG_PROP_NAME)):
            self._AppErrorMessages.update(AsyncWorkerManagerErrorMessages)
        else:
            self._AppErrorMessages = AsyncWorkerManagerErrorMessages

        super(AsyncWorkerManagerException, self).__init__(err_code, *err_msg_params)
