import os
# from configParser import configparser
from configparser import ConfigParser

# import fcntl                           #No support for windows
import portalocker  # Cross-platform support for File locking and unlocking.

from Utils.Core.Singleton import Singleton
from Utils.Utils.FileUtils import touch_file
from Utils.Utils.PathUtils import get_abs_path


class ConfigManager(Singleton):
    """
    ConfigManager module
    """

    def __init__(self, config_file_path=None):
        """
        Constructor of Config Manager class
        Args:
            config_file_path: configuration file that needs to be read.
        """
        self._user_settings_file_lock_path = None
        self._user_settings_file_path = None
        self._service_registry_settings_file_lock_path = None
        self._service_registry_settings_file_path = None
        self._settings_file_path = config_file_path
        self._settings_parser = ConfigParser()
        self._settings_parser.optionxform = str
        self._config_loaded = False
        self._override_settings_file_path = None

        if config_file_path:
            self._load_config_settings()

    def load_config_file(self, config_file_path):
        """
        Loads the specified configuration file
        """
        self._settings_file_path = config_file_path
        self._load_config_settings()

    def _load_config_settings(self):
        """
        Loads the config settings based on the following priority order
            if user settings file available - Priority : 1
            if service registry settings file available - Priority : 2
        """
        self._settings_parser.read(self._settings_file_path)

        if self._user_settings_file_path and (os.path.exists(self._user_settings_file_path)):
            file_descriptor = self._lock_user_settings_file()
            self._settings_parser.read(self._user_settings_file_path)
            self._unlock_settings_file(file_descriptor)

        if self._service_registry_settings_file_path and (os.path.exists(self._service_registry_settings_file_path)):
            file_descriptor = self._lock_service_registry_settings_file()
            self._settings_parser.read(self._service_registry_settings_file_path)
            self._unlock_settings_file(file_descriptor)

        self.override_settings_from_file()

        self._config_loaded = True

    def load_user_config_file(self, user_config_file_path):
        self._user_settings_file_path = get_abs_path(user_config_file_path)
        self._user_settings_file_lock_path = self._user_settings_file_path + ".lock"

        if not os.path.exists(self._user_settings_file_lock_path):
            touch_file(self._user_settings_file_lock_path)

        self._service_registry_settings_file_path = self._user_settings_file_path + '.srconf'
        self._service_registry_settings_file_lock_path = self._service_registry_settings_file_path + '.lock'

        self._load_config_settings()

    def _lock_user_settings_file(self):
        """
        Blocks the User settings file to avoid untracked changes  
        """
        file_descriptor = None
        if self._user_settings_file_lock_path:
            if not os.path.exists(self._user_settings_file_lock_path):
                touch_file(self._user_settings_file_lock_path)
            file_descriptor = open(self._user_settings_file_lock_path, 'w')
            # fcntl.flock(file_descriptor, fcntl.LOCK_EX)
            portalocker.lock(file_descriptor, portalocker.LOCK_EX)
        return file_descriptor

    def _lock_service_registry_settings_file(self):
        """
        Blocks the Service registry settings file to avoid untracked changes 
        """
        file_descriptor = None
        if self._service_registry_settings_file_lock_path:
            if not os.path.exists(self._service_registry_settings_file_lock_path):
                touch_file(self._service_registry_settings_file_lock_path)
            file_descriptor = open(self._service_registry_settings_file_lock_path, 'w')
            # fcntl.flock(file_descriptor, fcntl.LOCK_EX)
            portalocker.lock(file_descriptor, portalocker.LOCK_EX)
        return file_descriptor

    def _unlock_settings_file(self, file_descriptor):
        """
        Unblocks the settings file
        """
        self._test = "Unlock settings file"
        if file_descriptor:
            # fcntl.flock(file_descriptor, fcntl.LOCK_UN)
            portalocker.unlock(file_descriptor)
            file_descriptor.close()

    def initialize_override_file(self, override_file_path):
        """
        Update the override file with new file
        """
        if override_file_path:
            self._override_settings_file_path = override_file_path

    def override_settings_from_file(self):
        """
        Overrides the settings parser with correct configuration 
        """
        if not self._override_settings_file_path:
            return None

        service_registry_config_file_path = self._override_settings_file_path + '.srconf'

        if self._override_settings_file_path and (os.path.exists(self._override_settings_file_path)):
            self._settings_parser.read(self._override_settings_file_path)

        if service_registry_config_file_path and (os.path.exists(service_registry_config_file_path)):
            self._settings_parser.read(service_registry_config_file_path)

    def get_sections(self):
        """
        Reads the configuration file and returns all available sections in it
        """
        return self._settings_parser.sections()

    def get_user_sections(self):
        """
        Reads the User's configuration file and returns all available sections in it
        since the default self._settings_parser holds value based on availability of different files, 
        for getting user section, we need to read the file again
        """
        lcl_config_parser = ConfigParser()
        lcl_config_parser.read(self._user_settings_file_path)
        return lcl_config_parser.sections()

    def get_settings(self, section_name):
        """
        Gets available setting key/name, value from the given section name
        Args:
            section_name : Name of the section for which setting key / value need to be retrieved
        Returns:
            A dictionary object with all settings key, value in the section_name
        """
        return_value = None
        settings_list = self._settings_parser.items(section_name)
        if settings_list:
            return_value = dict()
            for setting_name, setting_value in settings_list:
                return_value[setting_name] = setting_value

        return return_value

    def get_setting_value(self, section_name, setting_name):
        """
        Gets the value of the setting of  given section details
        Args:
            section_name : Name of the section for which setting value need to be retrieved
            setting_name : Name of the setting for which value need to be retrieved
        Returns:
            string value of the settings
        """
        return self._settings_parser.get(section_name, setting_name)

    def set_setting_value(self, section_name, setting_name, setting_value):
        """
        Sets the value of setting for respective setting name in a section
        If the settings file is not available, it will create and update the file
        Args:
            section_name : Name of the section for which setting value need to be retrieved
            setting_name : Name of the setting for which value need to be retrieved
            setting_value : Value to be updated in the section -> setting
        Returns:
            string value of the settings
        """
        lcl_config_parser = ConfigParser()
        lcl_config_parser.optionxform = str

        if os.path.exists(self._user_settings_file_path):
            file_descriptor = self._lock_user_settings_file()
            lcl_config_parser.read(self._user_settings_file_path)
            self._unlock_settings_file(file_descriptor)

            if not lcl_config_parser.has_section(section_name):
                lcl_config_parser.add_section(section_name)

            lcl_config_parser.set(section_name, setting_name, setting_value)
        else:
            touch_file(self._user_settings_file_path)

            lcl_config_parser.add_section(section_name)
            lcl_config_parser.set(section_name, setting_name, setting_value)

        file_descriptor = self._lock_user_settings_file()
        with open(self._user_settings_file_path, 'w') as _file:
            lcl_config_parser.write(_file)
        self._unlock_settings_file(file_descriptor)
        self._load_config_settings()

        return True

    def remove_user_section(self, section_name):
        """
        Modify the User configuration file by removing a section
        Args:
            section_name: Name of the section that needs to be removed
        Returns:
            Removal status True / False
        """
        lcl_config_parser = ConfigParser()
        lcl_config_parser.optionxform = str
        remove_section_status = False
        if os.path.exists(self._user_settings_file_path):
            file_descriptor = self._lock_user_settings_file()
            lcl_config_parser.read(self._user_settings_file_path)
            self._unlock_settings_file(file_descriptor)

            if lcl_config_parser.has_section(section_name):
                remove_section_status = lcl_config_parser.remove_section(section_name)

            file_descriptor = self._lock_user_settings_file()
            with open(self._user_settings_file_path, 'w') as _file:
                lcl_config_parser.write(_file)

            self._unlock_settings_file(file_descriptor)
            self._load_config_settings()

        return remove_section_status

    def remove_user_setting(self, section_name, setting_name):
        """
        Modify the User configuration file by removing a settings in a section
        Args:
            section_name: Name of the section that needs to be removed
            setting_name: Name of the setting that needs to be removed
        Returns:
            Removal status True / False
        """
        lcl_config_parser = ConfigParser()
        lcl_config_parser.optionxform = str
        remove_setting_status = False
        if os.path.exists(self._user_settings_file_path):
            file_descriptor = self._lock_user_settings_file()
            lcl_config_parser.read(self._user_settings_file_path)
            self._unlock_settings_file(file_descriptor)

            if lcl_config_parser.has_section(section_name):
                remove_setting_status = lcl_config_parser.remove_option(section_name, setting_name)

            file_descriptor = self._lock_user_settings_file()
            with open(self._user_settings_file_path, 'w') as _file:
                lcl_config_parser.write(_file)

            self._unlock_settings_file(file_descriptor)
            self._load_config_settings()

        return remove_setting_status

    def is_setting_modified_by_user(self, section_name, setting_name):
        """
        Check if the settings are modified by users
        Args:
            section_name: Name of the section that needs to be checked
            setting_name: Name of the settings that needs to be checked
        Returns:
            Removal status True / False
        """
        return_value = None
        if section_name and setting_name:

            if self._user_settings_file_path and (os.path.exists(self._user_settings_file_path)):
                user_setting_parser = ConfigParser()
                file_descriptor = self._lock_user_settings_file()
                user_setting_parser.read(self._user_settings_file_path)
                self._unlock_settings_file(file_descriptor)

                try:
                    user_setting_value = user_setting_parser.get(section_name, setting_name)
                    if user_setting_value:
                        return_value = True
                except KeyError:
                    return_value = False
        return return_value
