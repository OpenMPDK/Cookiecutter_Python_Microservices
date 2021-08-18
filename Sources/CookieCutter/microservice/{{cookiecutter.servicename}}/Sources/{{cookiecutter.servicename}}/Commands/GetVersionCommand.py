import logging
from CommonLibrary.Cliff.Command import Command

class GetVersionCommand(Command):
    'Get code version'
    
    def take_action(self, parsed_args):
        self.app.get_version()