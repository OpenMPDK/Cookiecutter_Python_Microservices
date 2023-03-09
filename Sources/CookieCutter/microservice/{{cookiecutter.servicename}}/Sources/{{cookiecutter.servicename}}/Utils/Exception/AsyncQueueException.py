"""
Created on Aug 1, 2021

@author: admin
"""
from Utils.Exception.BaseException import BaseException
from Utils.Errors.AsyncQueueError import AsyncQueueErrorMessages


class AsyncQueueException(BaseException):

    def __init__(self, err_code=None, *err_msg_params):
        """
        Constructor of AsyncQueueException
        Args:
            err_code: error code
            *err_msg_params: error message details
        """

        if (hasattr(self, self.USR_ERR_MSG_PROP_NAME)) and (getattr(self, self.USR_ERR_MSG_PROP_NAME)):
            self._AppErrorMessages.update(AsyncQueueErrorMessages)
        else:
            self._AppErrorMessages = AsyncQueueErrorMessages

        super(AsyncQueueException, self).__init__(err_code, *err_msg_params)
