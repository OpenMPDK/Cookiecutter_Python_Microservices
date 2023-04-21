"""
Defines the error message and error code
"""
BASE_QUEUE_ERROR_NAME_READONLY = 3001
BASE_QUEUE_ERROR_LENGTH_READONLY = 3002

BaseQueueErrorMessages = {
    BASE_QUEUE_ERROR_NAME_READONLY: 'name is a read-only property',
    BASE_QUEUE_ERROR_LENGTH_READONLY: 'Length is a read-only property'
}
