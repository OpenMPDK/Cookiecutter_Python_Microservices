#!/bin/bash

venv=/opt/{{cookiecutter.venvname}}
service_name={{cookiecutter.servicecmdname}}
user={{cookiecutter.user}}
version=##VERSION_REPLACE##
mainpypackage={{cookiecutter.servicename}}

#cmdpath="/usr/bin"
action="configure"

if [ "$1" = "${action}" ]; then
    ${venv}/bin/pip install ${mainpypackage}==${version} --upgrade --index-url=http://107.110.186.47:8081/repository/pypi-proxy/simple --trusted-host=107.110.186.47
    #--extra-index-url=https://piplocalreleaseurl/index/pypi/simple --trusted-host=piplocalreleaseurl

    echo "Registering service with supervisor"
    runuser -l ${user} -c "${venv}/bin/${service_name} restserver service -r"

    #ufw status | grep -qw active

    if [ "$?" = "0" ]; then
        echo "ufw active. enabling ${mainpypackage} in ufw"

        #ufw allow ${mainpypackage}

        #ufw reload
    else
        echo "ufw inactive. skipping enabling ${mainpypackage} in ufw"
    fi
fi

exit 0
