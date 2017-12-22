# Change Log
All notable changes to this project will be documented in this file.

## [0.3.1] 2017-05-23
### Changed
- PNDA-2577: review python deps versions
- PNDA-2883: add `auth_version` to `pr-config.json` to set the swift keystone auth version associated with `auth_url`
- PNDA-3601: disable emailtext in Jenkins file and replace it with notifier stage and job

## [0.3.0] 2017-01-20
### Changed
- PNDA-2485: Pinned all python libraries to strict version numbers

## [0.2.1] 2016-12-12
### Changed
- Externalized build logic from Jenkins to shell script so it can be reused

### Fixed
- PNDA-2265: Fix logging config

## [0.2.0] 2016-10-21
### Added
- PNDA-1211: add FS repository as backend storage

## [0.1.1] 2016-09-07
### Changed
- PNDA-1811. Added timeout parameter to swift connection
- Enhancements to CI

## [0.1.0] 2016-07-01
### First version

## [Pre-release]

- Added option to use AWS S3 for application packages.
- PANDA-1728   Validate package names before upload and while fetching packages.
- PANDA-1585   Added delete package API.
- PANDA-1584   Fixed a lint error introduced as part of the last release.
- PANDA-1584   Fixed bug occurring when trying to notify the data logger that a new package has been created.
- PANDA-1413   Added cisco copyright headers
- PANDA-1413   fixed deprecated api bugs
- PANDA-1392   removed openstack credentials
- PANDA-1295   Removed UI code, and POST command
- PANDA-843   Using python logging framework
- PANDA-843   Running work in threadpool
- PANDA-843 initial packaging with maven
