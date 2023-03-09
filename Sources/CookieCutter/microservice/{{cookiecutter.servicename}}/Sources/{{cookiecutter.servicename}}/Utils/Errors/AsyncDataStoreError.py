"""
Defines the error message and error code
"""
ASYNC_DATA_STORE_ERROR_CANNOT_CONNECT_TO_DATASTORE = 4007
ASYNC_DATA_STORE_ERROR_INVALID_TASK_SPEC = 4008
ASYNC_DATA_STORE_ERROR_INVALID_JOB_ID = 4009
ASYNC_DATA_STORE_ERROR_JOB_ID_NOT_AVAILABLE = 4010
ASYNC_DATA_STORE_ERROR_INVALID_DATASTORE_NAME = 4011
ASYNC_DATA_STORE_ERROR_INALID_DATASTORE_SETTINGS = 4012

AsyncDataStoreErrorMessages = {
    ASYNC_DATA_STORE_ERROR_CANNOT_CONNECT_TO_DATASTORE: 'Invalid name {0} specified for job store',
    ASYNC_DATA_STORE_ERROR_INVALID_TASK_SPEC: 'Cannot connect to job datastore. Details : {0}',
    ASYNC_DATA_STORE_ERROR_INVALID_JOB_ID: 'Invalid task spec {0} provided',
    ASYNC_DATA_STORE_ERROR_JOB_ID_NOT_AVAILABLE: 'Invalid job id {0} provided',
    ASYNC_DATA_STORE_ERROR_INVALID_DATASTORE_NAME: 'Data store name {0} not available',
    ASYNC_DATA_STORE_ERROR_INALID_DATASTORE_SETTINGS: 'Invalid data store settings {0} provided for jobstore {1}'
}
