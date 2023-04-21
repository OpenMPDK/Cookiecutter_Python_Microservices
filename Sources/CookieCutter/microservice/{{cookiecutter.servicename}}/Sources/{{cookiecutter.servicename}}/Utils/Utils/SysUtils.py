# import grp, pwd
import getpass


def get_logged_in_user():
    """
    Gets the current logged-in user in which the service is running
    Returns: username

    """
    return getpass.getuser()
