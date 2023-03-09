import os


def get_abs_path(path):
    """
    Gets the absolute path
    Args:
        path: relative path

    Returns: absolute file path string

    """
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))
