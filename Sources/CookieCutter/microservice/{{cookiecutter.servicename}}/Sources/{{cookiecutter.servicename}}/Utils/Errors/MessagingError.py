"""
Defines the error message and error code
"""
MESSAGING_BACKEND_SECTION_NOT_FOUND = 201
MESSAGING_BACKEND_SETTING_NOT_FOUND = 201

MessagingErrors = {
    MESSAGING_BACKEND_SECTION_NOT_FOUND: 'Messaging Backend Settings {0} not found',
    MESSAGING_BACKEND_SETTING_NOT_FOUND: 'Mandatory settings {0} not available in section {1}',
}
