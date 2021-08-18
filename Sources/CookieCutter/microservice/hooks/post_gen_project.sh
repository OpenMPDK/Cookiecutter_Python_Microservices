#!/bin/bash
echo "Service template generated Called"
if [[ {{cookiecutter.create_local_venv}} == 'Yes' ]]; then
    echo "Creating virtualenv"
    python -m venv ~/.virtualenvs/{{cookiecutter.venvname}}
    source ~/.virtualenvs/{{cookiecutter.venvname}}/bin/activate
    echo "Installing packages for requirements.txt"
    pip install wheel
    pip install --index-url=http://107.110.186.47:8081/repository/pypi-proxy/simple --extra-index-url=http://107.110.186.47:8081/repository/pypi-staging//simple CommonLibrary --trusted-host=107.110.186.47 -r Sources/requirements.txt
    pip install --index-url=http://107.110.186.47:8081/repository/pypi-proxy/simple --trusted-host=107.110.186.47 -r Sources/requirements.txt
    #--extra-index-url=https://piplocalreleaseurl/index/pypi/simple --trusted-host=piplocalreleaseurl
fi

if [[ {{cookiecutter.create_debpkg_scripts}} == 'No' ]]; then
    cd $PWD && rm -rf PackageFiles/ PackageGenerator/ PackageScripts/
fi

echo "Service template generated successfully"