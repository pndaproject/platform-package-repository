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

	 Purpose:    runs system tests on the rest server
"""

import json
import threading
import time

from package_repository_rest_server import PackageRepositoryRestServer
from package_repo_rest_client import PackageRepoRestClient


def run_system_tests(api_url):
    print("Running system tests for: " + api_url)
    test_package = "test_temp_sr_system_test-0.0.2.tar.gz"
    old_test_package = "test_temp_sr_system_test-0.0.1.tar.gz"
    old_test_package_data = "some older dummy data: " + str(time.time())
    test_package_data = "some dummy data: " + str(time.time())
    client = PackageRepoRestClient("http://localhost:8888")
    # test a bad package in repository
    client.get_package("ThisPackageShouldReallyNotExist", [404])
    # testing putting a new package in the repository:
    client.put_package(test_package, test_package_data)
    # get the package data from the repository:
    downloaded_package_contents = client.get_package(test_package)
    # make sure that the package contents match what we just posted
    assert downloaded_package_contents == test_package_data
    # test package listing:
    client.put_package(old_test_package, old_test_package_data)
    package_list = client.get_package_list(recency=1)
    assert is_package_in_package_list(test_package, package_list)
    # older version of test package should not be in list with a recency of a single version
    assert not is_package_in_package_list(old_test_package, package_list)
    # get more versions of each package:
    package_list2 = client.get_package_list(recency=2)
    # older version of test package should be in list with a recency of a 2 versions
    assert is_package_in_package_list(old_test_package, package_list2)
    # finsihed testing:
    print("TESTS SUCCEEDED!!!")


def is_package_in_package_list(package_name, package_list):
    """
    :returns true if package_name exists in package_list
    """
    package_found_in_list = False
    for item in package_list:
        versions = item["latest_versions"]
        for version in versions:
            file_name = version["file"]
            if file_name == package_name:
                package_found_in_list = True
    return package_found_in_list


if __name__ == "__main__":
    print("Configuring test server...")
    with open('../pr-config.json', 'r') as f:
        CONFIG = json.load(f)
    TEST_SERVER = PackageRepositoryRestServer(configuration=CONFIG)
    try:
        threading.Thread(target=lambda: TEST_SERVER.run()).start()
        TEST_SERVER.wait_for_server_to_start()
        run_system_tests("http://localhost:8888")
    finally:
        TEST_SERVER.stop()
