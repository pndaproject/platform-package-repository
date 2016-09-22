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

	 Purpose:    Retrieves packages and lists of available packages from the repository
                     Implementations include
                     packges are stores in OpenStack Swift
"""

import logging
import swiftclient


class SwiftRepository(object):
    def __init__(self, config):
        self._connection = config['access']
        self._location = config['container']
        self.path = self._location["path"]

    def read_package(self, package_name):
        return self.download_package(package_name)

    def get_package_list(self):
        # get information from swift:
        swift_packages = self.get_contatniner_contents(None)[1]
        # return a clean list of packages:
        package_names_with_path = [swift_item["name"] for swift_item in swift_packages]
        # remove pesky path from package names
        package_names = [swift_item.replace(self.path + "/", "") for swift_item in package_names_with_path]
        # return a clean list of packages:
        return package_names

    def put_package(self, package_name, package_contents):
        logging.debug("uploading package %s", package_name)
        connection = self._connect()
        container_name = self._location['container']
        path = self._location['path']
        try:
            # put object on swift:
            connection.put_object(container_name, path + '/' + package_name, package_contents)
        finally:
            connection.close()

    def delete_package(self, package):

        logging.debug("delete_package %s", package)

        try:
            connection = self._connect()
            container_name = self._location['container']
            path = self._location['path']

            try:
                connection.delete_object(container_name, path + '/' + package)
            except swiftclient.exceptions.ClientException:
                raise KeyError('Did not find package in swift: %s' % package)
        finally:
            connection.close()

    def get_contatniner_contents(self, recency):
        logging.debug("list_packages %s", recency)
        try:
            connection = self._connect()
            container_name = self._location['container']
            path = self._location['path']
            container_contents = connection.get_container(container_name, prefix=path)
            return container_contents
        finally:
            connection.close()

    def download_package(self, package):

        logging.debug("download_package %s", package)

        try:
            connection = self._connect()
            container_name = self._location['container']
            path = self._location['path']

            try:
                obj_tuple = connection.get_object(
                    container_name, path + '/' + package)
            except swiftclient.exceptions.ClientException:
                raise KeyError('Did not find package in swift: %s' % package)

        finally:
            connection.close()
        return obj_tuple[1]

    def _connect(self):
        logging.debug("_connect")

        connection = swiftclient.client.Connection(auth_version='2',
                                                   user=self._connection[
                                                       'user'],
                                                   key=self._connection['key'],
                                                   tenant_name=self._connection[
                                                       'account'],
                                                   authurl=self._connection['auth_url'],
                                                   timeout=30)

        return connection
