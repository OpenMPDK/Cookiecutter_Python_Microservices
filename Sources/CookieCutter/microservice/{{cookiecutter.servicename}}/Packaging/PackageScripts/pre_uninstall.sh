#!/bin/bash

venv=/opt/{{cookiecutter.venvname}}
service_name={{cookiecutter.servicecmdname}}
mainpypackage={{cookiecutter.servicename}}

#cmdpath="/usr/bin"
action="remove"

if [ "$1" = "${action}" ]; then

    echo "Deregistering service with supervisor"
    runuser -l ${user} -c "${venv}/bin/${service_name} restserver service -d"

    #ufw status | grep -qw active

    if [ "$?" = "0" ]; then
        echo "ufw active. enabling ${mainpypackage} in ufw"

        #ufw delete allow ${mainpypackage}

        #ufw reload
    else
        echo "ufw inactive. skipping enabling ${mainpypackage} in ufw"
    fi
fi

exit 0
