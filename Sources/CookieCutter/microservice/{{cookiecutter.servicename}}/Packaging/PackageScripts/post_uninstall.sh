#!/bin/bash

venv=/opt/{{cookiecutter.venvname}}
user={{cookiecutter.user}}
supervisors_group_name=supervisors

action="remove"

if [ "$1" = "${action}" ]; then
    echo "removing virtual env"
    rm -rf ${venv}

    echo "Deregistering user from ${supervisors_group_name} group"
    deluser ${user} ${supervisors_group_name}
    
    echo "Deleting user ${user}"
    deluser ${user}
    
    echo "Removing user ${user} directories"
    rm -rf /home/${user}
fi

exit 0