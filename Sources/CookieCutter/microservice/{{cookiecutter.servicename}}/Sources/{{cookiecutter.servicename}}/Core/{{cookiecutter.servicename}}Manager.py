from pkg_resources import resource_filename

from Utils.Core.BaseObject import BaseObject
from Utils.Core.Singleton import Singleton

from {{cookiecutter.servicename}}.Exception.{{cookiecutter.servicename}}Exception import {{cookiecutter.servicename}}Exception
from {{cookiecutter.servicename}} import __version__,__description__

class {{cookiecutter.servicename}}Manager(BaseObject, Singleton):
    def __init__(self):
        BaseObject.__init__(self)

    def get_version(self):
        self._Logger.info('Getting version information from %s-%s' %('{{cookiecutter.servicename}}', __version__))
        return '{{cookiecutter.servicename}}:'+__version__