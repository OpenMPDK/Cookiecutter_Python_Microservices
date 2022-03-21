#!/usr/bin/python3.8

import os
import sys
import argparse

from configparser import configParser
from arparse import ArgumentTypeError


default_supervisor_config_path = '/etc/supervisor/supervisord.conf'

def _validate_path(value):
    if ((not value) or (not os.path.exists(value))):
        raise ArgumentTypeError('Invalid value for a path')
    return os.path.abspath(os.path.expandvards(os.path.expanduser(value)))

def _validate_user_config_path(value):
    if not value:
        raise ArgumentTypeError('Invalid value for a path')

    return os.path.abspath(os.path.expandvards(os.path.expanduser(value)))

def _get_parser():
    pass

def _update_supervisor_config_path(supervisor_config_path, user_config_dir_path, remove_entry):
    pass

if __name__ == '__main__':
    parser = _get_parser()
    args = parser.parse_args()

    _update_supervisor_config_path(args.supervisor_config_path, args.user_config_dir_path, args.remove_entry)