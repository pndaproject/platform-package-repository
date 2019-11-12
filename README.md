# Platform Package Repository #

## Overview

Packages are independently deployable units of application layer functionality. Each package consists of one or more components, each of which has a defined type. The `platform-deployment-manager` documentation details the format and usage of packages.

The platform-package-repository component provides a REST API that allows:

 - a package to be uploaded
 - a package to be downloaded
 - the contents of repository to be listed

## Repository configuration

All the configuration is defined in the file pr-config.json. Currently, the package repository supports Swift / AWS S3 or file system backend storage. 

Here are some example configurations for each supported option.

- Swift: use the settings from the openrc script available through the OpenStack Horizon console. This assumes that the apps container with the folder releases is already created and also that the user has access to Swift.

```json
    "SwiftRepository": {
        "access": {
            "account":"OS_PROJECT_NAME",
            "user": "OS_USERNAMAE",
            "key": "OS_PASSWORD",
            "auth_url": "OS_AUTH_URL"
        },
        "container": {
            "container": "apps",
            "path": "releases"
        }
    },
```

- AWS S3:
```json
    "S3Repository": {
        "access": {
            "region": "AWS_REGION",
            "access_key": "AWS_KEY",
            "secret_access_key": "AWS_SECRET_KEY"
        },
        "container": {
            "bucket": "apps",
            "path": "releases"
        }
    },
```
- File system: this could be local filesystem, sshfs or mounted volume but is transparent from a package repository point of view.
```json
    "FsRepository": {
        "location": {
            "path": "/opt/packages"
        }
    }
```

## Repository API

### Base URL

All API paths below are relative to a base URL is defined by schemes, host, port and base path on the root level of this API specification.

```
<scheme>://<host>:<port>/<base path>
```

By default, the API uses 'https' scheme as the transfer protocol. Host is the domain name or hostname that serves the API. In order to access the API outside PNDA security perimeter, it has to via knox service by using the domain name or FQDN when creating a PNDA cluster. The domain name or FQDN must be resolvable via public or private DNS service. To access repository API, the base path, `/gateway/pnda/repository`, must be used as prefixes for all API paths. 

e.g. ```https://knox.example.com:8443/gateway/pnda/repository```

### List packages from the repository

?recency=n may be used to control how many versions of each package are listed, by default recency=1
````
GET /packages?user.name=<username>

Response Codes:
200 - OK
403 - Unauthorised user
500 - Server Error

Query Parameters:
user.name - User name to run this command as. Should have permissions to perform the action as defined in authorizer_rules.yaml. 

Example response:
[
  {
    "latest_versions": [
      {
        "version": "1.0.23",
        "file": "spark-batch-example-app-1.0.23.tar.gz"
      }
    ],
    "name": "spark-batch-example-app"
  }
]
````

### Get package contents
````
Downloads a package from the repository
GET /packages/<package>?user.name=<username>

Response Codes:
200 - OK
403 - Unauthorised user
404 - Not Found
500 - Server Error

Query Parameters:
user.name - User name to run this command as. Should have permissions to perform the action as defined in authorizer_rules.yaml. 

Response body:
The binary contents of the package that was uploaded
````

### Upload a package to the repository
````
PUT /packages/<package>?user.name=<username>

Response Codes:
200 - Accepted
403 - Unauthorised user
500 - Server Error

Query Parameters:
user.name - User name to run this command as. Should have permissions to perform the action as defined in authorizer_rules.yaml. 

e.g.
curl http://host:8888/packages/my-package-1.0.0.tar.gz --upload-file my-package-1.0.0.tar.gz

````
### Delete a package from the repository
````
DELETE /packages/<package>?user.name=<username>

Response Codes:
200 - Accepted
403 - Unauthorised user
404 - Not Found
500 - Server Error

Query Parameters:
user.name - User name to run this command as. Should have permissions to perform the action as defined in authorizer_rules.yaml. 

e.g.
curl -X DELETE http://host:8888/packages/my-package-1.0.0.tar.gz
````
