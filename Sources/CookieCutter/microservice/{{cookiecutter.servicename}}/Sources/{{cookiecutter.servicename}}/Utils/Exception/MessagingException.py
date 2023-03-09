from Utils.Exception.BaseException import BaseException
from Utils.Errors.MessagingError import MessagingErrors


class MessagingException(BaseException):

    def __init__(self, err_code=None, *err_msg_params):
        """
        Constructor of MessagingException
        Args:
            err_code: error code
            *err_msg_params: error message details
        """

        if (hasattr(self, self.USR_ERR_MSG_PROP_NAME)) and (getattr(self, self.USR_ERR_MSG_PROP_NAME)):
            self._AppErrorMessages.update(MessagingErrors)
        else:
            self._AppErrorMessages = MessagingErrors

        super(MessagingException, self).__init__(err_code, *err_msg_params)
