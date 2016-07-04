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
import re
from distutils.version import StrictVersion
from data_logger_client import DataLoggerClient


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

    def read_package(self, package_name):
        """
        :returns the contents of the specified package
        """
        return self.package_repository.read_package(package_name)

    def delete_package(self, package_name):
        """
        deletes the specified package
        """
        self.package_repository.delete_package(package_name)
        self.data_logger_client.report_event(name=package_name,
                                             endpoint_type=DataLoggerClient.ENDPOINT_PACKAGES,
                                             state=DataLoggerClient.STATE_NOTCREATED)

    def put_package(self, package_name, package_contents):
        """
        updates the contents of a package in the repository
        """
        # put the package in the repository
        self.package_repository.put_package(package_name, package_contents)
        # report that a new package has been created
        self.data_logger_client.report_event(name=package_name,
                                             endpoint_type=DataLoggerClient.ENDPOINT_PACKAGES,
                                             state=DataLoggerClient.STATE_CREATED)

    def get_packages_grouped_by_version(self, number_of_versions_to_list=None):
        """
        Logic code for dealing with packages
        :param number_of_versions_to_list The number of versions to list for each package.
        Refactor Note:
        To conform with previous package management workflow,this code is extracted from:
        https://cto-github.cisco.com/CTAO-Team6-Analytics/platform-deployment-manager/blob/2.0.7/api/src/main/resources/repository.py
        The schema specifies that:
            All file which are of format:
            VERSION-major_number.minor_number.tar.gz
            Are all related the the same package.
        In the future this versioning might be moved into an explicit schema in the data layer.
        * ATM reading all the names of all versions for all files is required to return any version of any package.
        * Entries that were created and do not conform to the regex below will not be listed.
        * Might want to return a dictionary of packages instead of an array of exclusively named pairs
        """
        # get a list of ungrouped package names:
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
        if len(package_version_list) > 0:
            package_version = ''.join(package_version_list[0])
            try:
                _ = StrictVersion(package_version) # check if version conforms to strict versioning
            except Exception, exception:
                raise ValueError(str(exception) + "\n" + "Package version must be a three part major.minor.patch e.g. name-1.2.3 but found %s" %
                                 package_name_without_extension)
        else:
            raise ValueError("package version must be a three part major.minor.patch e.g. name-1.2.3 but found %s" %
                             package_name_without_extension)
