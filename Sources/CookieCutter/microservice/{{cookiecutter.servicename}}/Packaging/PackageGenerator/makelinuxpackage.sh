#!/bin/bash
dependency_file_path=./Depedencies.txt
name={{cookiecutter.packagename}}
supervisor_users_group=supervisors
description="{{cookiecutter.description}}"
license=""
maintainer=""
package_url=""
vendor=""
version=$(cat ../../Sources/{{cookiecutter.servicename}}/version.txt)

sed -i "s/VERSION=##VERSION_REPLACE/VERSION=${version}/g" ../PackageScripts/post_install.sh

dependencies=""

while read line
do
    if ! [ -z ${line} ]; then
        dependencies="${dependencies} -d ${line}"
    fi
done < ${dependency_file_path}

dependencies=$(echo ${dependencies} | xargs)

if [ "$#" -eq 0]; then
    if [ -z "${display}" ]; then
        read -p "Package Type (deb/rpm) : " pkgtype
    else
        pkgtype=$(zenity --list --text "Which type of package you want to generata?" --radiolist --column "Select" --column "Package Type" TRUE deb FALSE rpm);
    fi
else
    pkgtype=$1
fi

if ! [[ ${pkgtype} == "deb" || ${pkgtype} == "rpm" ]]; then
    echo "Invalid package type selected"
    exit -1
fi

echo "Building a ${pkgtype} for ${name}"

fpm \
    -s dir \
    -t ${pkgtype} \
    -n "$name" \
    -v ${version} \
    -m "${maintainer}" \
    ${dependencies} \
    --vendor "${vendor}" \
    --license "${license}" \
    --before-install ../PackageScripts/pre_install.sh \
    --before-remove ../PackageScripts/pre_uninstall.sh \
    --after-install ../PackageScripts/post_install.sh \
    --after-remove ../PackageScripts/post_uninstall.sh \
    ../PackageFiles/=/
    
sed -i "s/VERSION=##VERSION_REPLACE/VERSION=${version}/g" ../PackageScripts/post_install.sh