"""
Created on Aug 1, 2021

@author: admin
"""
from Utils.Exception.BaseException import BaseException
from Utils.Errors.BaseQueueError import BaseQueueErrorMessages


class BaseQueueException(BaseException):

    def __init__(self, err_code=None, *err_msg_params):
        """
        Constructor of BaseQueueException
        Args:
            err_code: error code
            *err_msg_params: error message details
        """

        if (hasattr(self, self.USR_ERR_MSG_PROP_NAME)) and (getattr(self, self.USR_ERR_MSG_PROP_NAME)):
            self._AppErrorMessages.update(BaseQueueErrorMessages)
        else:
            self._AppErrorMessages = BaseQueueErrorMessages

        super(BaseQueueException, self).__init__(err_code, *err_msg_params)
