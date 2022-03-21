#!/bin/bash
echo "Service template generated Called"
os_info=$(uname -a)
echo $os_info 
#> C:\\Users\\anjan.r\\test.txt
if [[ {{cookiecutter.create_local_venv}} == 'Yes' ]]; then
    echo "Creating virtualenv"
    python -m venv ~/.virtualenvs/{{cookiecutter.venvname}}
    if [[ $os_info == *"NT"* ]]; then
        echo "Setting up for windows "
        echo "~/.virtualenvs/{{cookiecutter.venvname}}/"
        ~/.virtualenvs/{{cookiecutter.venvname}}/Scripts/pip.exe install wheel --index-url=http://107.110.186.47:8081/repository/pypi-proxy/simple --trusted-host=107.110.186.47
        ~/.virtualenvs/{{cookiecutter.venvname}}/Scripts/pip.exe install --index-url=http://107.110.186.47:8081/repository/pypi-proxy/simple --extra-index-url=http://107.110.186.47:8081/repository/pypi-staging/simple -r Sources/requirements.txt --trusted-host=107.110.186.47 
    else
        source ~/.virtualenvs/{{cookiecutter.venvname}}/bin/activate
        python -m pip install wheel --index-url=http://107.110.186.47:8081/repository/pypi-proxy/simple --trusted-host=107.110.186.47
        python -m pip install --index-url=http://107.110.186.47:8081/repository/pypi-proxy/simple --extra-index-url=http://107.110.186.47:8081/repository/pypi-staging/simple -r Sources/requirements.txt --trusted-host=107.110.186.47 
    fi
    echo "Installing packages for requirements.txt"
    
    #--extra-index-url=https://piplocalreleaseurl/index/pypi/simple --trusted-host=piplocalreleaseurl
fi

if [[ {{cookiecutter.create_debpkg_scripts}} == 'No' ]]; then
    cd $PWD && rm -rf PackageFiles/ PackageGenerator/ PackageScripts/
fi

echo "Service template generated successfully"