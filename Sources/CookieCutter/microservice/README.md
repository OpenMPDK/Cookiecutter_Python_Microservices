# Microservice Cookiecutter

This cookiecutter provides a ready-to-use template for a microservice for python flask restful service development

## Features

### Rest Service
    - A Flask based REST service
    - CORS Handled by default
    - Swagger based self documentation/test interface for REST endpoints (https://pypi.org/project/flask-restful-swagger-3 for documentation)
    - Modes
        - Multithreaded flask server
        - WSGI server capable of integrating into any WSGI compatiblle webservers

### Interface
    -   cliff based application command line interface
        -   Commands to start/stop/restart REST service
        -   Commands to register/deregister REST service with supervisor (http://supervisord.org)
        -   Interactive shell

### Ready-made development environment
    -   Python virtenv created as part of the cookiecutter template

### Configuration Management
    - 3 levels of configuration management
        - Application default configuration
        - User configuration
        - Remotely controlled configurations (via service registry concept)
    - Integrated logging with service logs
    - Central configurations to manage logs, formats and messages - without changing code

### Package Management
    - Ready made package generators with ability to generate - RPM and DEB (Linux based)
    - Package handles installation and dependencies

### Version Management
    - Both Python packages and OS packages are forced to have same versioning
    - Standard version scheme - Major.Minor.TestRelease

## Dependencies
    - Users of this cookiecutter template needs to install the cookiecutter python package
        Python3 and PIP has to be installed prior to utilizing this cookie cutter
        - Linux users
            - pip install cookiecutter --index-url=http://<ip>:8081/repository/pypi-proxy/simple --trusted-host=<ip>
        - Windows users
            - python3 -m pip install cookiecutter --index-url=http://<ip>:8081/repository/pypi-proxy/simple --trusted-host=<ip>

## Creating a new Service
    - Command line usage to create new service
        - Linux users
            cd /path/to/folder  -> where service needs to be created
            cookiecutter </path/to/cookiecutterproject.git>/Sources/CookieCutter/microservice -> Will ask the user to provide information about the project
        - Windows users
            cd /path/to/folder  -> where service needs to be created
            pyhon -m cookiecutter </path/to/cookiecutterproject.git>\Sources\CookieCutter\microservice -> Will ask the user to provide information about the project
        
        - inputs to be provided, all inputs will have default values - users can override the value by providing the input
                ```shell
                servicename [TestService]: TestExecutor
                description [A Test Service]: A Python flask restful microservice for test execution engine
                servicecmdname [testexecut]: testexecutor
                user [testex]: testexecutor
                serverport [3486]:
                packagename [testexecutor]:
                urlsuffix [testexecutor]:
                Select server_mode:
                1 - wsgi
                2 - flask
                Choose from 1, 2 [1]:
                venvname [testexecutor]:
                Select create_local_venv:
                1 - No
                2 - Yes
                Choose from 1, 2 [1]: 2
                Select create_debpkg_scripts:
                1 - No
                2 - Yes
                Choose from 1, 2 [1]:
                ```
    - Folder Structure
        .
        ├── Deployment
        │   ├── Configuration
        │   └── Docker
        ├── integrateSampleService.sh
        ├── Packaging
        │   ├── PackageFiles
        │   │   ├── etc
        │   │   │   └── ufw
        │   │   │       └── applications.d
        │   │   │           └── SampleService
        │   │   ├── opt
        │   │   │   └── supervisor
        │   │   │       └── bin
        │   │   │           └── UpdateSpervisorConf.py
        │   │   └── usr
        │   │       └── share
        │   │           └── doc
        │   │               └── sampleservice
        │   │                   └── README.md.txt
        │   ├── PackageGenerator
        │   │   ├── Dependencies.txt
        │   │   └── makelinuxpackage.sh
        │   └── PackageScripts
        │       ├── post_install.sh
        │       ├── post_uninstall.sh
        │       ├── pre_install.sh
        │       └── pre_uninstall.sh
        ├── README.md
        ├── runSampleService.sh
        ├── Sources
        │   ├── README.md
        │   ├── requirements.txt
        │   ├── SampleService
        │   │   ├── Apps
        │   │   │   ├── __init__.py
        │   │   │   └── SampleServiceApp.py
        │   │   ├── Commands
        │   │   │   ├── GetVersionCommand.py
        │   │   │   ├── __init__.py
        │   │   │   └── RestServer.py
        │   │   ├── Conf
        │   │   │   ├── SampleService.conf
        │   │   │   ├── SampleService_Log.conf
        │   │   │   └── SampleService_Rest_Server_Supervisor.conf
        │   │   ├── Core
        │   │   │   ├── __init__.py
        │   │   │   ├── RestServer.py
        │   │   │   └── SampleServiceManager.py
        │   │   ├── Datastore
        │   │   │   └── __init__.py
        │   │   ├── Errors
        │   │   │   ├── ErrorCodes.py
        │   │   │   └── __init__.py
        │   │   ├── Exception
        │   │   │   ├── __init__.py
        │   │   │   └── SampleServiceException.py
        │   │   ├── __init__.py
        │   │   ├── Interface
        │   │   │   └── __init__.py
        │   │   ├── Proxies
        │   │   │   └── __init__.py
        │   │   ├── RestResource
        │   │   │   ├── GetVersion.py
        │   │   │   ├── __init__.py
        │   │   │   └── ShutdownServer.py
        │   │   ├── TaskProcessor
        │   │   │   └── __init__.py
        │   │   ├── Utils
        │   │   │   └── __init__.py
        │   │   ├── version.txt
        │   │   └── WorkerCommands
        │   │       └── __init__.py
        │   └── setup.py

    - Building
        - WHL Packages (make sure the wheel package is installed)
            - Windows / Linux
            ```shell
            cd Sources
            (testscheduler) H:\src\TestScheduler\Sources>pip install wheel --upgrade --index-url=http://<ip>:8081/repository/pypi-proxy/simple --trusted-host=<ip>
            Looking in indexes: http://<ip>:8081/repository/pypi-proxy/simple
            Collecting wheel
            Downloading http://<ip>:8081/repository/pypi-proxy/packages/wheel/0.37.0/wheel-0.37.0-py2.py3-none-any.whl (35 kB)
            Installing collected packages: wheel
            Successfully installed wheel-0.37.0
            WARNING: You are using pip version 20.1.1; however, version 21.2.4 is available.
            You should consider upgrading via the 'h:\.virtualenvs\testscheduler\scripts\python.exe -m pip install --upgrade pip' command.

            (testscheduler) H:\src\TestScheduler\Sources>python setup.py bdist_wheel
            running bdist_wheel
            running build
            running build_py
            creating build
            creating build\lib
            creating build\lib\TestScheduler
            ...
            adding 'TestScheduler-0.0.1.dist-info/entry_points.txt'
            adding 'TestScheduler-0.0.1.dist-info/namespace_packages.txt'
            adding 'TestScheduler-0.0.1.dist-info/top_level.txt'
            adding 'TestScheduler-0.0.1.dist-info/RECORD'
            removing build\bdist.win-amd64\wheel
            (testscheduler) H:\src\TestScheduler\Sources>
            (testscheduler) H:\src\TestScheduler\Sources>dir dist
            Volume in drive H is Shared Disk
            Volume Serial Number is 8A70-A396

            Directory of H:\src\TestScheduler\Sources\dist

            08/18/2021  01:01 PM    <DIR>          .
            08/18/2021  01:01 PM    <DIR>          ..
            08/18/2021  01:01 PM            16,609 TestScheduler-0.0.1-py3-none-any.whl
                        1 File(s)         16,609 bytes
                        2 Dir(s)  102,056,648,704 bytes free
            ```

## Future Features
    -   Integrate async worker
    -   Integrate mongo db
