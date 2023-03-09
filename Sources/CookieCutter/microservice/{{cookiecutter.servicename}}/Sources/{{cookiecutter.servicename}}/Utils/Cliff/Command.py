from cliff.command import Command
from Utils.Exception.BaseException import BaseException

from logging import getLogger


# noinspection PyRedeclaration
class Command(Command):
    def take_action(self, parsed_args):
        """
        Function that processed the command
        Args:
            parsed_args:
        """
        pass

    def run(self, parsed_args):
        """
        Runs the command and captures the log information
        Args:
            parsed_args: command arguments

        Returns: command output

        """
        try:
            return_value = self.take_action(parsed_args)
        except BaseException as e:
            _log = None

            if hasattr(self, 'LOG'):
                _log = self.LOG
            else:
                _log = getLogger(__name__)

            _log.error(str(e))
            return_value = e.get_error_code()

        return return_value
