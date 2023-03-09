"""
Defines the error message and error code
"""
ASYNC_WORKER_MANAGER_ERROR_INVALID_WORKER_SPEC_NAME = 4018
ASYNC_WORKER_MANAGER_ERROR_INVALID_WORKER_SUPERVISOR_CONF_TEMPLATE = 4019

AsyncWorkerManagerErrorMessages = {
    ASYNC_WORKER_MANAGER_ERROR_INVALID_WORKER_SPEC_NAME: 'Invalid worker spec name: {0}',
    ASYNC_WORKER_MANAGER_ERROR_INVALID_WORKER_SUPERVISOR_CONF_TEMPLATE: 'Invalid worker supervisor configuration '
                                                                        'template {0} '
}
