#!/bin/bash

venv=/opt/{{cookiecutter.venvname}}
service_name={{cookiecutter.servicecmdname}}
supervisors_group_name=supervisors
supervisors_config_path="/etc/supervisor/supervisord.conf"
supervisors_user_config_path=/opt/supervisor/conf.d
update_supervisor_script_path=/opt/supervisor/bin/UpdateSpervisorConf.py

user={{cookiecutter.user}}

cmdpath="/usr/bin"
action="install"

if [ "$1" = "${action}" ]; then

    if [ $(getent group ${supervisors_group_name}) ]; then
        echo "Already available, skipping this part"
    else
        echo "Creating supervisor group"
        groupadd ${supervisors_group_name}
    fi   

    [ -d ${supervisors_user_config_path} ] || mkdir -p ${supervisors_user_config_path}

    #provide ownership and write access for ${supervisors_user_config_path}
    chown -R root:${supervisors_group_name} ${supervisors_user_config_path}
    chmod g+w ${supervisors_user_config_path}

    echo "Updating supervisor config path location"
    ${cmdpath}/python3.8 ${update_supervisor_script_path} -p ${supervisors_user_config_path} -c ${supervisors_config_path}

    if id "${user}" > /dev/null 2>&1 ; then
        echo "User already exists : ${user}"
    else
        echo "Creating user ${user}"
        useradd -m -s /bin/bash "${user}"
        usermod -a -G ${supervisor_users_group} ${user}
    fi

    if [ -d "${venv}" ]; then
        echo "virtual env already exists : ${venv}"
        #rm -rf ${venv}
        exit 1
    fi

    if [ ! -d "${cmdpath}" ]; then
        echo "${cmdpath}  missing"
        exit 1
    fi

    echo "Creating virtual environment for python 3.8"
    cmdpath=${cmdpath}
    #${cmdpath}/virtualenv --no-site-packages ${venv}
    python -m venv ${venv}

    ${venv}/bin/pip install pip --upgrade --index-url=http://107.110.186.47:8081/repository/pypi-proxy/simple --trusted-host=107.110.186.47
    ${venv}/bin/pip install wheel --upgrade --index-url=http://107.110.186.47:8081/repository/pypi-proxy/simple --trusted-host=107.110.186.47
    #--extra-index-url=https://piplocalreleaseurl/index/pypi/simple --trusted-host=piplocalreleaseurl

    #ufw enable
fi

exit 0
