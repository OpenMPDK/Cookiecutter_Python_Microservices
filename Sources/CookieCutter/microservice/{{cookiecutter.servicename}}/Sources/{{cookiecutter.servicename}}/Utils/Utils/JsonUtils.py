import json


def json_loads(input_value):
    """
    Method to be used to parse a valid JSON string and convert it into Python dictionary
    Args:
        input_value: string representation of the json

    Returns: dictionary object

    """
    return json.loads(input_value, object_hook=_decode_dict)


def json_load(file_pointer):
    """
    Method to be used to parse a file object and convert it into Python dictionary
    Args:
        file_pointer: file pointer object

    Returns: python dictionary

    """
    return json.load(file_pointer, object_hook=_decode_dict)


def decode_dict_str(data):
    """
    This is a test method to check the implementation
    Args:
        data: dictionary

    Returns: constructed output in dictionary object

    """
    return _decode_dict(data)


def _decode_dict(data):
    """
    Iterate through the dictionary's key,value pairs and Encode the string with UTF-8
    Args:
        data: dictionary that needs to be processed

    Returns: processed data

    """
    return_value = {}
    for key, value in data.items():
        # if isinstance(key, str):
        #     # key = key.encode('utf-8')
        #     key = key  # str(key, 'utf-8')
        # if isinstance(value, str):
        #     # value = value.encode('utf-8')
        #     value = value  # str(value, 'utf-8')
        # el
        if isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        return_value[key] = value

    return return_value


def _decode_list(items):
    """
    Iterate through the list item and Encode the string with UTF-8
    Args:
        items: nested data list of dictionary values

    Returns: processed data

    """
    return_value = []
    for item in items:
        # if isinstance(item, str):
        #     # item = item.encode('utf-8')
        #     item = item  # str(item, 'utf-8')
        # el
        if isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        return_value.append(item)
    return return_value


def _decode_string(item):
    """
    Encode string value with UTF-8
    Args:
        item: string to be encoded to utf-8

    Returns: utf-8 encoded string

    """
    return_value = item
    if isinstance(item, str):
        return_value = item  # str(item, 'utf-8')
    return return_value
