from CommonLibrary.Exception.BaseException import BaseException
from {{cookiecutter.servicename}}.Errors.ErrorCodes import ErrorMessages

class {{cookiecutter.servicename}}Exception(BaseException):
    def __init__(self, errCode = None, *errMsgParams):
        self._AppErrorMessages = ProxyErrorMessages

        BaseException.__init__(self, errCode, *errMsgParams)