from Utils.Exception.BaseException import BaseException
from Utils.Errors.ProxyError import ProxyErrorMessages


class ProxyException(BaseException):
    def __init__(self, err_code=None, *err_msg_params):
        """
        Constructor of ProxyException
        Args:
            err_code: error code
            *err_msg_params: error message details
        """
        self._AppErrorMessages = ProxyErrorMessages

        BaseException.__init__(self, err_code, *err_msg_params)
