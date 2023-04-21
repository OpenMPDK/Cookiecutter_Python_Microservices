"""
Defines the error message and error code
"""
ASYNC_WORKER_ERROR_INVALID_VALUE_FOR_NAME = 5007
ASYNC_WORKER_ERROR_INVALID_VALUE_FOR_TASK_QUEUE = 5008
ASYNC_WORKER_ERROR_TASK_QUEUES_NOT_SET = 5009
ASYNC_WORKER_ERROR_TASK_PROCESSOR_NOT_SET = 5010
ASYNC_WORKER_ERROR_TASK_PROCESSOR_NOT_FOUND = 5011
ASYNC_WORKER_ERROR_INVALID_TASK_DEQUEUED = 5012
ASYNC_WORKER_ERROR_BEFORE_START = 5013
ASYNC_WORKER_ERROR_INVALID_WORKER_SPEC_PROPERTY = 5014
ASYNC_WORKER_ERROR_INVALID_VALUE_ASSIGNED_FOR_TASK_HANDLERS = 5015
ASYNC_WORKER_ERROR_CANNOT_SET_TASK_QUEUES_PROPERTY = 5016

AsyncWorkerErrorMessages = {
    ASYNC_WORKER_ERROR_INVALID_VALUE_FOR_NAME: 'Invalid value provided for name : {0}',
    ASYNC_WORKER_ERROR_INVALID_VALUE_FOR_TASK_QUEUE:  'Invalid value provided for task queue : {0}. Should be list of '
                                                      'AsyncQueue Objects',
    ASYNC_WORKER_ERROR_TASK_QUEUES_NOT_SET: 'Cannot start worker, task queue is not set/assigned',
    ASYNC_WORKER_ERROR_TASK_PROCESSOR_NOT_SET: 'Cannot start worker, no task processor(s) are assigned',
    ASYNC_WORKER_ERROR_TASK_PROCESSOR_NOT_FOUND: 'No task processor(s) found for task type : {0}',
    ASYNC_WORKER_ERROR_INVALID_TASK_DEQUEUED: 'Invalid task dequeued',
    ASYNC_WORKER_ERROR_BEFORE_START: 'Error before starting worker, Details : {0}',
    ASYNC_WORKER_ERROR_INVALID_WORKER_SPEC_PROPERTY: 'Invalid value {0} provided for worker spec. Details : {1}',
    ASYNC_WORKER_ERROR_INVALID_VALUE_ASSIGNED_FOR_TASK_HANDLERS: 'Invalid value assigned for task handlers',
    ASYNC_WORKER_ERROR_CANNOT_SET_TASK_QUEUES_PROPERTY: 'task_queues property is not settable'
}
