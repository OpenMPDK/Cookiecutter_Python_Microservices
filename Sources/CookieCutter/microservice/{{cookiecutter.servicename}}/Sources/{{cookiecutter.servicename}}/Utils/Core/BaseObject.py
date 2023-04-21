from logging import getLogger

from Utils.Core.ConfigManager import ConfigManager


class BaseObject(object):
    def __init__(self):
        """
        Constructor of Base Object
        This class provides access to Logger and Config manager instances which can be used for
        logging and reading/changing configuration values in conf file.
        """
        super(BaseObject, self).__init__()
        self._Logger = getLogger(type(self).__module__)
        self._config_manager = ConfigManager.get_instance()
