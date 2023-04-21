from Utils.Exception.BaseException import BaseException
from Utils.Errors.ServiceManagerError import ServiceManagerErrorMessages


class ServiceManagerException(BaseException):
    def __init__(self, err_code=None, *err_msg_params):
        """
        Constructor of ServiceManagerException
        Args:
            err_code: error code
            *err_msg_params: error message details
        """
        self._AppErrorMessages = ServiceManagerErrorMessages

        BaseException.__init__(self, err_code, *err_msg_params)
