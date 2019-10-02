"""
	 Copyright (c) 2016 Cisco and/or its affiliates.
	 This software is licensed to you under the terms of the Apache License, Version 2.0 (the "License").
	 You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
	 The code, technical concepts, and all information contained herein, are the property of Cisco Technology, Inc.
	 and/or its affiliated entities, under various laws including copyright, international treaties, patent, and/or contract.
	 Any use of the material herein must be in accordance with the terms of the License.
	 All rights not expressly granted by the License are reserved.
	 Unless required by applicable law or agreed to separately in writing, software distributed under the License is
	 distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

	 Purpose:    Manages packages
"""
import grp
import pwd
import re
from distutils.version import StrictVersion

import authorizer_local
from data_logger_client import DataLoggerClient
import exceptiondef

class Resources(object):
    REPOSITORY = "package_repository:repository"


class Actions(object):
    DELETE = "delete"
    READ = "read"
    WRITE = "write"

class PackageManager(object):
    """
    Contains logic for working with package repositories
    """

    def __init__(self, package_repository, data_logger_client):
        """
        :param package_repository: Am implementation of a package repository to work wirf
        """
        self.package_repository = package_repository
        self.data_logger_client = data_logger_client
        self._authorizer = authorizer_local.AuthorizerLocal()

    def _get_groups(self, user):
        groups = []
        if user:
            try:
                groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
                gid = pwd.getpwnam(user).pw_gid
                groups.append(grp.getgrgid(gid).gr_name)
            except:
                raise exceptiondef.Forbidden('Failed to find details for user "%s"' % user)
        return groups

    def _authorize(self, user_name, resource_type, resource_owner, action_name):
        qualified_action = '%s:%s' % (resource_type, action_name)
        identity = {'user': user_name, 'groups': self._get_groups(user_name)}
        resource = {'type': resource_type, 'owner': resource_owner}
        action = {'name': qualified_action}
        if not self._authorizer.authorize(identity, resource, action):
            raise exceptiondef.Forbidden('User "%s" does not have authorization for "%s"' % (user_name, qualified_action))

    def read_package(self, package_name, user_name):
        """
        :returns the contents of the specified package
        """
        self._authorize(user_name, Resources.REPOSITORY, None, Actions.READ)
        return self.package_repository.read_package(package_name)

    def delete_package(self, package_name, user_name):
        """
        deletes the specified package
        """
        self._authorize(user_name, Resources.REPOSITORY, None, Actions.DELETE)
        self.package_repository.delete_package(package_name)
        self.data_logger_client.report_event(name=package_name,
                                             endpoint_type=DataLoggerClient.ENDPOINT_PACKAGES,
                                             state=DataLoggerClient.STATE_NOTCREATED)

    def put_package(self, package_name, package_contents, user_name):
        """
        updates the contents of a package in the repository
        """
        self._authorize(user_name, Resources.REPOSITORY, None, Actions.WRITE)
        # put the package in the repository
        self.package_repository.put_package(package_name, package_contents)
        # report that a new package has been created
        self.data_logger_client.report_event(name=package_name,
                                             endpoint_type=DataLoggerClient.ENDPOINT_PACKAGES,
                                             state=DataLoggerClient.STATE_CREATED)

    def get_packages_grouped_by_version(self, user_name, number_of_versions_to_list=None):
        """
        Logic code for dealing with packages
        :param number_of_versions_to_list The number of versions to list for each package.
        All file names are formatted as:
            VERSION-major_number.minor_number.tar.gz
        """
        # get a list of ungrouped package names:
        self._authorize(user_name, Resources.REPOSITORY, None, Actions.READ)
        package_names = self.get_package_list()
        candidates = {}
        for item in package_names:
            try:
                # if package name does not match the validation rules, drop it from the list
                self.validate_package_name(item)
            except ValueError:
                continue
            grps = re.match(r'((.*)-(\d+.\d+.\d+).*)', item)
            if grps is not None:
                groups = grps.groups()
                if len(groups) == 3:
                    fullname, shortname, version = groups
                entry = {'version': version, 'file': fullname}
                try:
                    candidates[shortname].append(entry)
                except KeyError:
                    candidates[shortname] = [entry]

        packages_list = []
        for can in candidates:
            last = sorted(
                candidates[can],
                key=lambda x: StrictVersion(
                    x['version']),
                reverse=True)[:number_of_versions_to_list]
            packages_list.append({'name': can, 'latest_versions': last})
        return packages_list

    def get_package_list(self):
        """
        :returns a list of all packages in the repository
        """
        return self.package_repository.get_package_list()

    def validate_package_name(self, package_name):
        """
        validates the package name and checks if it conforms to PEP-386 standards
        """

        parts = package_name.split('-')
        tar_archive = '.'.join(package_name.split('.')[-2:]) # get the tar archive extension

        package_name_without_extension = '.'.join(package_name.split('.')[:-2]) # get the package name without .tar.gz extemsion

        if tar_archive != 'tar.gz':
            raise ValueError("sorry. the archive must end with a tar.gz extension ")

        if len(parts) < 2:
            raise ValueError("package name must be of the form name-version e.g. name-0.1.2 but found %s" %
                             package_name_without_extension)

        package_version_list = re.findall(r'(\d+\.\d+\.\d+)([-]?[a-zA-Z]*)', package_name_without_extension) # get the package version
        if package_version_list:
            package_version = ''.join(package_version_list[0])
            try:
                _ = StrictVersion(package_version) # check if version conforms to strict versioning
            except Exception as exception:
                raise ValueError(str(exception) + "\n" + "Package version must be a three part major.minor.patch e.g. name-1.2.3 but found %s" %
                                 package_name_without_extension)
        else:
            raise ValueError("package version must be a three part major.minor.patch e.g. name-1.2.3 but found %s" %
                             package_name_without_extension)
