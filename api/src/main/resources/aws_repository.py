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
                     packges are stores in AWS S3
"""

import logging
import os.path
import re
import boto.s3
from boto.s3.key import Key

class S3Repository(object):
    def __init__(self, config):
        self._s3_connection = config['access']
        self._s3_location = config['container']

    def read_package(self, package_name):
        return self.download_package(package_name)

    def get_package_list(self):
        package_names_with_path = self.get_container_contents()
        package_names = map(os.path.basename, package_names_with_path)
        return package_names

    def put_package(self, package_name, package_contents):
        logging.debug("uploading package %s", package_name)
        connection = self._connect()
        try:
            # put object:
            bucket = connection.get_bucket(self._s3_location['bucket'])
            key = Key(bucket)
            key.key = '%s/%s' % (self._s3_location['path'], package_name)
            key.set_contents_from_string(package_contents)
        finally:
            connection.close()

    def delete_package(self, package):

        logging.debug("delete_package %s", package)

        connection = self._connect()
        try:
            bucket = connection.get_bucket(self._s3_location['bucket'])
            key = bucket.get_key('%s/%s' % (self._s3_location['path'], package))
            key.delete()
        except Exception:
            raise KeyError('Did not find package in AWS: %s' % package)
        finally:
            connection.close()

    def get_container_contents(self):
        logging.debug("list_packages")
        connection = self._connect()
        try:
            bucket = connection.get_bucket(self._s3_location['bucket'])
            items = bucket.list(prefix=self._s3_location['path'])
            candidates = []
            for item in items:
                grps = re.match(self._s3_location['path']+r'/((.*)-(\d+.\d+.\d+).*)', item.name)
                if grps is not None and len(grps.groups()) == 3:
                    candidates.append(item.name)
            return candidates
        finally:
            connection.close()

    def download_package(self, package):

        logging.debug("download_package %s", package)
        connection = self._connect()
        try:
            bucket = connection.get_bucket(self._s3_location['bucket'])
            key = bucket.get_key('%s/%s' % (self._s3_location['path'], package))
            file_data = key.get_contents_as_string()
        except Exception:
            raise KeyError('Did not find package in AWS: %s' % package)
        finally:
            connection.close()

        return file_data

    def _connect(self):
        logging.debug("_connect")

        connection = boto.s3.connect_to_region(self._s3_connection['region'],
                                               aws_access_key_id=self._s3_connection['access_key'],
                                               aws_secret_access_key=self._s3_connection['secret_access_key'])

        return connection
