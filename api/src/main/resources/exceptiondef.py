"""
Name:       exceptiondef.py
Purpose:    Custom exceptions for use across the project
Author:     PNDA team

Created:    29/05/2018

Copyright (c) 2018 Cisco and/or its affiliates.

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

class PrException(Exception):
    """
    Any exception derived from this class should be exposed through the API to the caller.
    """
    def __init__(self, arg):
        super(PrException, self).__init__(arg)
        self.msg = arg

    def __str__(self):
        return str(self.msg)

class Forbidden(PrException):

    def __init__(self, arg):
        super(Forbidden, self).__init__(arg)
        self.msg = arg
