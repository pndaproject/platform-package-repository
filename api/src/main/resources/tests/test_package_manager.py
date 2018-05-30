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

	 Purpose:    Unit tests for the the asynchronous dispatcher
                     Run with main(), the easiest way is "nosetests test_*.py"
"""

import time
import unittest
import json
from mock import Mock
from local_package_repository import LocalPackageRepository
from package_manager import PackageManager


class GenerateRecord(unittest.TestCase):

    def _mock_get_groups(self, _):
        return []

    def test_package_versions(self):
        """
        tests that packages are grouped correctly by version
        """
        test_package = "test_temp_sr_system_test-0.0.2.tar.gz"
        old_test_package = "test_temp_sr_system_test-0.0.1.tar.gz"
        package_repository = Mock()
        package_repository.get_package_list = Mock(return_value=[test_package, old_test_package])
        data_logger = Mock()
        package_manager = PackageManager(package_repository, data_logger)
        # pylint: disable=protected-access
        package_manager._get_groups = self._mock_get_groups
        # run test with only latest versions of packages:
        single_version_list = package_manager.get_packages_grouped_by_version('someone', number_of_versions_to_list=1)
        self.assertIn(test_package, json.dumps(single_version_list), "package should be in list")
        self.assertNotIn(old_test_package, json.dumps(single_version_list), "package should not be in list")
        # run test with all versions of packages:
        multiple_version_list = package_manager.get_packages_grouped_by_version('someone', number_of_versions_to_list=10)
        self.assertIn(test_package, json.dumps(multiple_version_list), "package should be in list")
        self.assertIn(old_test_package, json.dumps(multiple_version_list), "package should  be in list")

    def test_package_contents(self):
        """
        test putting and getting packages from repo
        """
        test_package = "test_temp_sr_system_test-0.0.2.tar.gz"
        test_package_data = "some dummy data: " + str(time.time())
        package_repository = LocalPackageRepository()
        data_logger = Mock()
        package_manager = PackageManager(package_repository, data_logger)
        # pylint: disable=protected-access
        package_manager._get_groups = self._mock_get_groups
        package_manager.put_package(test_package, test_package_data, 'somebody')
        # check that what was written matches what was read
        self.assertEquals(test_package_data,
                          package_manager.read_package(test_package, 'somebody'),
                          "package contentens match what was written")
