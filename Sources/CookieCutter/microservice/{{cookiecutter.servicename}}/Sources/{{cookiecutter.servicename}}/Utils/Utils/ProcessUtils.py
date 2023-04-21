import os
import subprocess
from logging import getLogger, Logger
from time import sleep


def execute_as_subprocess_without_output(command_line, working_folder_path, logger):
    """
    Executes a given command line as subprocess using subprocess.Popen

    Args:
        command_line:Command to be executed
        working_folder_path:Current directory on which the command needs to be executed
        logger: Logger instance to be used for logging
    Returns:
        None
    Raises:
        Custom Exception
    """
    if (logger is None) or (not (type(logger) is Logger)):
        _log = getLogger()
    else:
        _log = logger

    if not command_line:
        _log.error('Invalid command line')
        return False

    if (working_folder_path is None) or (not os.path.exists(working_folder_path)):
        _log.error('Invalid working folder path : %s' % working_folder_path)
        return False

    try:
        _ = subprocess.Popen(command_line, cwd=working_folder_path, shell=True)
        return True
    except Exception as ex:
        _log.error('Exception while executing command line %s. Details: %s' % (command_line, str(ex)))


def execute_as_subprocess(command_line, working_folder_path, logger):
    """
    Executes a given command line as subprocess using subprocess.Popen
    STDOUT and STDERR are logged as info and error respectively

    Args:
        command_line:Command to be executed
        working_folder_path:Current directory on which the command needs to be executed
        logger: Logger instance to be used for logging
    Returns:
        Return code of process, where None indicates no error.
    Raises:
        Custom Exception
    """
    if (logger is None) or (not (type(logger) is Logger)):
        _log = getLogger()
    else:
        _log = logger

    if not command_line:
        _log.error('Invalid command line')
        return None

    if (working_folder_path is None) or (not os.path.exists(working_folder_path)):
        _log.error('Invalid working folder path : %s' % working_folder_path)
        return None

    try:
        command_process = subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           cwd=working_folder_path, shell=True)

        with command_process.stdout:
            for line in iter(command_process.stdout.readline, b''):
                strip_line = line.strip()
                if strip_line:
                    _log.info(strip_line)

        with command_process.stderr:
            for line in iter(command_process.stderr.readline, b''):
                strip_line = line.strip()
                if strip_line:
                    _log.error(strip_line)

        command_process.wait()

        return command_process.returncode
    except Exception as ex:
        _log.error('Exception while executing command line %s. Details: %s' % (command_line, str(ex)))


def execute_as_subprocess_with_output(command_line, working_folder_path, logger):
    """
    Executes a given command line as subprocess using subprocess.Popen
    STDOUT and STDERR are logged as info and error respectively

    Args:
        command_line:Command to be executed
        working_folder_path:Current directory on which the command needs to be executed
        logger: Logger instance to be used for logging
    Returns:
        A tuple containing 'Return code of process, where None indicates no error.', STDOUT, STDERR
    Raises:
        Custom Exception
    """
    if (logger is None) or (not (type(logger) is Logger)):
        _log = getLogger()
    else:
        _log = logger

    if not command_line:
        _log.error('Invalid command line')
        return None

    if (working_folder_path is None) or (not os.path.exists(working_folder_path)):
        _log.error('Invalid working folder path : %s' % working_folder_path)
        return None

    try:
        command_process = subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           cwd=working_folder_path, shell=True)

        # command_process.wait() // is a blocking call. It may hang the application sometimes, so instead using
        # communicate method and a timer to control it

        stdout, stderr = command_process.communicate()

        time_waited = 0
        while True:
            return_value = command_process.poll()
            if return_value is None:
                sleep(2)
                time_waited = time_waited + 2
                if time_waited < 10:
                    continue
                else:
                    break
            else:
                break

        return command_process.returncode, stdout, stderr
    except Exception as ex:
        _log.error('Exception while executing command line %s. Details: %s' % (command_line, str(ex)))
