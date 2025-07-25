# formsflow.ai API

[![FormsFlow API CI](https://github.com/AOT-Technologies/forms-flow-ai/actions/workflows/forms-flow-api-ci.yml/badge.svg)](https://github.com/AOT-Technologies/forms-flow-ai/actions)
![Python](https://img.shields.io/badge/python-3.13.2-blue) ![Flask](https://img.shields.io/badge/Flask-3.1.0-blue) ![postgres](https://img.shields.io/badge/postgres-11.0-blue)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)

**formsflow.ai** has built this adaptive tier for correlating form management, BPM and analytics together.

The goal of the REST API is to provide access to all relevant interfaces of
the system. It is built using Python :snake: .

## Table of Content

1. [Prerequisites](#prerequisites)
2. [Solution Setup](#solution-setup)
   * [Step 1 : Installation](#installation)
   * [Step 2 : Environment Configuration](#environment-configuration)
   * [Step 3 : Running the Application](#running-the-application)
   * [Step 4 : Verify the Application Status](#verify-the-application-status)
3. [API Documentation](#api-documentation)
4. [Unit Testing](#unit-testing)
5. [Migration Script for existing users](#migration-script-for-existing-users) (For listing existing forms for clients)

## Prerequisites

* For docker based installation [Docker](https://docker.com) need to be installed.
* Admin access to [Keycloak](../forms-flow-idm/keycloak) server and ensure audience(camunda-rest-api) is setup in Keycloak-bpm server.
* Ensure that the `forms-flow-redis` service is running and accessible on port `6379`. For more details, refer to the [forms-flow-redis README](../forms-flow-redis/README.md).


## Solution Setup

### Installation

If you are interested in contributing to the project, you can install through docker or locally.

It's recommended to download dev-packages to follow Python coding standards for project like PEP8 if you are interested in contributing to project.
You installing dev-packages using pip as follows:

```python3 -m pip install -r requirements/dev.txt```

### Keycloak Setup

No specific client creation is required. Audience has been added for clients
**forms-flow-web** and **forms-flow-bpm**.  

### Environment Configuration

* Make sure you have a Docker machine up and running.
* Make sure your current working directory is "forms-flow-ai/forms-flow-api".
* Rename the file [sample.env](./sample.env) to **.env**.
* Modify the environment variables in the newly created **.env** file if needed. Environment variables are given in the table below,
* **NOTE : {your-ip-address} given inside the .env file should be changed to your host system IP address. Please take special care to identify the correct IP address if your system has multiple network cards**

### Running the Application

* forms-flow-api service uses port 5000, make sure the port is available.
* `cd {Your Directory}/forms-flow-ai/forms-flow-api`

* Run `docker-compose up -d` to start.

*NOTE: Use --build command with the start command to reflect any future **.env** changes eg : `docker-compose up --build -d`*

#### To Stop the Application

* Run `docker-compose stop` to stop.

### Verify the Application Status

   The application should be up and available for use at port defaulted to 5000 in <http://localhost:5000/>
  
* Access the **/checkpoint** endpoint for a Health Check on API to see it's up and running.

```
GET http://localhost:5000/checkpoint

RESPONSE

{
    "message": "Welcome to formsflow.ai API"
}
```

* Get the access token

```
POST {Keycloak URL}/auth/realms/<realm>/protocol/openid-connect/token

Body:
grant_type: client_credentials
client_secret: {set client token}
client_id: forms-flow-bpm

Headers:
Content-Type : application/x-www-form-urlencoded

```

* Access the **/task** endpoint and verify response. Ensure Bearer token is passed along

```
GET http://localhost:5000/task

Headers:
Content-Type : application/json
Authorization: Bearer {access token}
```

## API Documentation

The API docs can be accessed by checking the http://localhost:5000 .

![image](https://user-images.githubusercontent.com/70306694/130730233-cf443a84-7716-4be6-b196-cb340509c495.png)

Further documentation and associated postman collection for API endpoint
can found in the [docs folder](./docs)

## Migration Script for existing users (For users below v5.2.0)

#### To display existing forms and applications for clients and reviewers, it is necessary to migrate the current Camunda authorizations. Additionally, to transfer existing task filters from forms-flow-bpm to forms-flow-api

#### Follow the steps below: 

Run a bash script inside the forms-flow-api. If you need to run this script in the instance or server, such as a Kubernetes cluster or Nginx, you have to access the Docker container of the FormsFlow web API and 
execute the bash script called [migration.sh](./migration.sh). 

#### Commands to execute:

* To migrate forms:  `migration.sh form`
* To migrate applications:  `migration.sh application`
* To migrate filter: `migration.sh filter`<br>
     * In multi-tenant environment: `migration.sh filter <tenant-key>` 
 


Alternatively, if you are setting up the environment locally and running the Docker container locally, you can get inside the FormsFlow web API container and run preferred command.

In the case of running the web API with Flask locally, you should activate the virtual environment and run the bash script within it. You can create the virtual environment by following the instructions provided in the [Makefile](./Makefile) inside the forms-flow-api.


#### References for Testing in Python

* [pytest](https://docs.pytest.org/en/latest/getting-started.html)
* [Real Python Unit Testing with Pytest](https://realpython.com/pytest-python-testing/)
* [More about similar test config we have used](http://alexmic.net/flask-sqlalchemy-pytest/)


### Additional reference

Check out the [installation documentation](https://aot-technologies.github.io/forms-flow-installation-doc/) for installation instructions and [features documentation](https://aot-technologies.github.io/forms-flow-ai-doc) to explore features and capabilities in detail.