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

	 Purpose:    Unit testing
"""

import unittest
import mock
from mock import  Mock
from swift_repository import SwiftRepository


class TestSwiftRepo(unittest.TestCase):
    # mock configuration for swift object
    swift_config = {
        "access": {
            "account": "some_account",
            "user": "user",
            "key": "not_telling",
            "auth_url": "not_telling_either"
        },
        "container": {
            "container": "apps",
            "path": "releases"
        }
    }

    # mock response from swift driver
    swift_response = [
        {
            "content-length": "25011",
            "content-type": "application/json; charset=utf-8"
        }, [{
            "bytes": 9235,
            "last_modified": "2016-03-23T14:36:20.000Z",
            "hash": "2a43a0629a4df5033d70176b4e71a216",
            "name": "releases/spark-batch-example-app-1.0.25.tar.gz"
        }, {
            "bytes": 9247,
            "last_modified": "2016-03-23T14:44:06.000Z",
            "hash": "b54264c03eb088361f370bf0b84c18fe",
            "name": "releases/spark-batch-example-app-1.0.26.tar.gz"
        }, {
            "bytes": 9251,
            "last_modified": "2016-03-25T13:13:56.000Z",
            "hash": "cc3c56727e9b81943a6ee345040a2782",
            "name": "releases/spark-batch-example-app-c-1.0.30.tar.gz"
        }]
    ]

    @mock.patch('swiftclient.client.Connection')
    def test_list_packages(self, swift_mock):
        # mock to return fake list of swift files
        swift_mock.return_value.get_container.return_value = self.swift_response
        repo = SwiftRepository(self.swift_config)
        # get list of packages
        packages = repo.get_package_list()
        # make sure file from mock is in this list
        self.assertIn("spark-batch-example-app-1.0.26.tar.gz", packages)

    @mock.patch('swiftclient.client.Connection')
    def test_download_package(self, swift_mock):
        #setup mocks:
        swift_mock.return_value.get_container.return_value = self.swift_response
        swift_mock.return_value.get_object.return_value = ["", "abcd"]
        mock_repo_client = Mock()
        mock_repo_client.get_package = Mock(return_value="abcd")
        repo = SwiftRepository(self.swift_config)
        #download a package
        package_data = repo.download_package("spark-batch-example-app-c-1.0.30")
        #check package contents:
        self.assertEqual(package_data, "abcd")

    @mock.patch('swiftclient.client.Connection')
    def test_put_package(self, swift_mock):
        #setup mocks
        swift_mock.return_value.get_container.return_value = self.swift_response
        repo = SwiftRepository(self.swift_config)
        #put package in swift
        repo.put_package("spark-batch-example-app-c-1.0.30", "test data")

    @mock.patch('swiftclient.client.Connection')
    def test_download_package_error(self, swift_mock):
        # this will cause a key error:
        swift_mock.return_value.get_object.return_value = {}
        repo = SwiftRepository(self.swift_config)
        #check that error was raised:
        self.assertRaises(KeyError, repo.download_package, "no_such_package")
