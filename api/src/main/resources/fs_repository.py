"""
Name:       repository.py
Purpose:    Retrieves packages and lists of available packages from FileSystem
            which could be either local or using sshfs
Author:     PNDA team

Created:    21/03/2016

Copyright (c) 2016 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

The code, technical concepts, and all information contained herein, are the property of Cisco Technology, Inc.
and/or its affiliated entities, under various laws including copyright, international treaties, patent,
and/or contract. Any use of the material herein must be in accordance with the terms of the License.
All rights not expressly granted by the License are reserved.

Unless required by applicable law or agreed to separately in writing, software distributed under the
License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied.
"""

import re
import os
import logging
from distutils.version import StrictVersion

class FsRepository(object):
    def __init__(self, location):
        self._location = location

    def read_package(self, package_name):
        return self.download_package(self._location['path']+"/"+package_name)

    def get_package_list(self):

        path = self._location['path']
        package_names = [item.replace(path + "/", "") for item in os.listdir(path)]
        return package_names

    def is_available(self, package):
        logging.debug("is_available %s", package)
        path = self._location['path']
        found = False
        for item in os.listdir(path):
            if '/' + package + '.' in "%s%s" % (path, item):
                found = True
                break
        logging.debug(found)
        return found

    def download_package(self, package):
        logging.debug("download_package %s", package)
        with open("%s" % package, "rb") as in_file:
            package_data = in_file.read()
        return package_data
