from Utils.Exception.BaseException import BaseException
from Utils.Errors.AsyncMessagingQueueError import AsyncMessagingQueueErrorMessages


class AsyncMessagingQueueException(BaseException):

    def __init__(self, err_code=None, *err_msg_params):
        """
        Constructor of AsyncMessagingQueueException
        Args:
            err_code: error code
            *err_msg_params: error message details
        """

        if (hasattr(self, self.USR_ERR_MSG_PROP_NAME)) and (getattr(self, self.USR_ERR_MSG_PROP_NAME)):
            self._AppErrorMessages.update(AsyncMessagingQueueErrorMessages)
        else:
            self._AppErrorMessages = AsyncMessagingQueueErrorMessages

        super(AsyncMessagingQueueException, self).__init__(err_code, *err_msg_params)
