import os
import requests

from urllib.parse import urlparse
import shutil

from Utils.Utils.ProcessUtils import execute_as_subprocess
from Utils.Utils.ProcessUtils import execute_as_subprocess_with_output


def touch_file(file_path, times=None):
    """
    Check if folder path exists, and create if not available
    Creates file in append mode

    Args:
        file_path:path of the file which needs to be created or updated
        times:timestamp to track file modification time
    Returns:
        None
    Raises:
        None
    """
    file_base_path = os.path.dirname(file_path)
    if not os.path.exists(file_base_path):
        os.makedirs(file_base_path)

    with open(file_path, 'a'):
        os.utime(file_path, times)


def download_file(url, verify=True, local_file_path=None):
    """
    Downloads file from the given URL
    
    Args:
        url: URL path from which file has to be downloaded
        verify: Certificate verification
        local_file_path: Local file path where the file has to be downloaded
    Returns:
        Downloaded file path as str
    Raises:
        None
    """
    if local_file_path is None:
        tmp_local_file_path = url.split('/')[-1]
    else:
        tmp_local_file_path = local_file_path

    req = requests.get(url, verify=verify, stream=True)
    req.raise_for_status()

    with open(tmp_local_file_path, 'wb') as fd:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                fd.write(chunk)
                fd.flush()

    return tmp_local_file_path


def fetch_files_from_url(url, destination_path, logger, timeout_in_secs=300):
    """
    Downloads files from the given URL
    
    Args:
        url: URL path from which file has to be downloaded
        destination_path: Local path where the file has to be downloaded
        logger: Logger instance to be used for logging
        timeout_in_secs: Maximum wait time for download to complete
    Returns:
        Wget commands response status
    Raises:
        None
    """
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)
    url_parts = urlparse(url)
    num_parts = len(url_parts.path.strip('/').strip('/'))
    command_line = 'wget -r --no-parent -nH --reject "index.html*" --cut-dirs=%s --timeout=%s %s' % (
        num_parts, timeout_in_secs, url)

    proc_status_code = execute_as_subprocess(command_line, destination_path, logger)

    return proc_status_code


def fetch_files_from_url_with_output(url, destination_path, logger, timeout_in_secs=300):
    """
    Downloads files from the given URL
    
    Args:
        url: URL path from which file has to be downloaded
        destination_path: Local path where the file has to be downloaded
        logger: Logger instance to be used for logging
        timeout_in_secs: Maximum wait time for download to complete
    Returns:
        (Command Return code, STDOUT, STDERR)
    Raises:
        None
    """
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)
    url_parts = urlparse(url)
    num_parts = len(url_parts.path.strip('/').strip('/'))
    command_line = 'wget -r --no-parent -nH --reject "index.html*" --cut-dirs=%s --timeout=%s ' \
                   '--no-check-certificate %s' % (num_parts, timeout_in_secs, url)

    proc_status_code = execute_as_subprocess_with_output(command_line, destination_path, logger)

    return proc_status_code


def copy_file_or_folder(source_path, destination_path):
    """
    Copies file(s) or folder(s) from Source to destination using SHUTIL
    
    Args:
        source_path: Source file/folder path
        destination_path: Destination file/folder path
    Returns:
        None
    Raises:
        None
    """
    if os.path.isdir(source_path):
        source_path_base_name = os.path.basename(source_path)
        tmp_destination_path = os.path.join(destination_path, source_path_base_name)
        shutil.copytree(source_path, tmp_destination_path)
    elif os.path.isfile(source_path):
        shutil.copy2(source_path, destination_path)
