"""
Defines the error message and error code
"""
ASYNC_QUEUE_ERROR_PEEK_NOT_SUPPORTED = 4013
ASYNC_QUEUE_ERROR_INVALID_ITEM_ENQUEUED = 4014
ASYNC_QUEUE_ERROR_SET_RESULT_INVOKED_WITH_INVALID_JOB_ID = 4015
ASYNC_QUEUE_ERROR_SET_RESULT_NOT_SUPPORTED = 4016
ASYNC_QUEUE_ERROR_WHILE_SETTING_UP_BACKEND = 4017

AsyncQueueErrorMessages = {
    ASYNC_QUEUE_ERROR_PEEK_NOT_SUPPORTED: 'Peek operation is not supported on this queue',
    ASYNC_QUEUE_ERROR_INVALID_ITEM_ENQUEUED: 'AsyncQueue can accept items of type AsyncTaskSpec ',
    ASYNC_QUEUE_ERROR_SET_RESULT_INVOKED_WITH_INVALID_JOB_ID: 'Set result invoked with an invalid job  : {0}',
    ASYNC_QUEUE_ERROR_SET_RESULT_NOT_SUPPORTED: 'Set result not supported on queue : {0}',
    ASYNC_QUEUE_ERROR_WHILE_SETTING_UP_BACKEND: 'Error while setting up backend. Details : {0}',
}
