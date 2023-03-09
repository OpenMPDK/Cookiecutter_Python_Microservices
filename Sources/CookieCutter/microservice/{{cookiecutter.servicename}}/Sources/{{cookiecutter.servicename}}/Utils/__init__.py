import os
import logging
from logging import getLogger

from pkg_resources import resource_filename

logging.basicConfig(level=logging.ERROR)

version_file = resource_filename('Utils', 'version.txt')
_LOG = getLogger()
version = None

if not os.path.exists(version_file):
    _LOG.error('%s does not exists. Considering version as 0.0.0.0' % version_file)
    version = '0.0.0'
else:
    try:
        with open(version_file, 'rt') as file_handler:
            version = file_handler.read().strip()
    except Exception as e:
        version = '0.0.0'
        _LOG.error('Exception %s while opening file %s. Considering version as 0.0.0.0' % (str(e), version_file))

__version__ = version
__description__ = 'Helper library for python microservice projects'
