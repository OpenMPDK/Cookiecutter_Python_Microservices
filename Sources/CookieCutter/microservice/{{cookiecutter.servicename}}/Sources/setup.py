#!/usr/bin/env python
import os
from setuptools import setup, find_packages
import {{cookiecutter.servicename}}

try:
    long_description = open('README.md', 'rt').read()
except IOError as ex:
    long_description = ''

def load_dependency_packages():
    dep_packages = list()

    if os.path.exists('requirements.txt'):
        requirement_list = None
        with open('requirements.txt') as file_handler:
            requirement_list = file_handler.readlines()

        if requirement_list:
            dep_packages = [requirement_pkg.strip() for requirement_pkg in requirement_list ]

    return dep_packages

packages = load_dependency_packages()
package_scripts = []
package_data = ['Conf/*.conf','version.txt']

setup(
    name={{cookiecutter.servicename}}.__name__,
    version={{cookiecutter.servicename}}.__version__,
    description={{cookiecutter.servicename}}.__description__,
    long_description=long_description,
    author='',
    author_email='',
    #url='index url for pkg whl releases'
    #download_url='index url for pkg whl releases'
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: MacOS :: MaCOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Environment :: Console',
        'Topic :: Software Development'
    ],
    platforms=[],
    keywords=[],
    scripts=package_scripts,
    provides=[],
    install_requires=packages,
    python_requires=">=3.8",
    namespace_packages=[],
    packages=find_packages(),
    package_data={'{{cookiecutter.servicename}}' : package_data},
    include_package_data=True,
    cmdclass = {},
    entry_points={
        'console_scripts':[
            '{{cookiecutter.servicename}} = {{cookiecutter.servicename}}.Apps.{{cookiecutter.servicename}}App:main'
        ],
        '{{cookiecutter.servicename}}.commands':[
            'restserver = {{cookiecutter.servicename}}.Commands.RestServer:RestServer',
            'version = {{cookiecutter.servicename}}.Commands.GetVersionCommand:GetVersionCommand'
        ]
    },
    zip_safe=False,

)