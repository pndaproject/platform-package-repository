"""
Name:       authorizer.py
Purpose:    Interface definition for modules that validate requests to access resources by comparing the attributes of an
            identity, a resource and an action against a set of rules.

Author:     PNDA team

Created:    17/05/2018

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

class Authorizer(object):
    '''
    Interface definition that validate requests to access resources
    '''
    def authorize(self, identity, resource, action):
        '''
        Validate a request to access a resource
        Parameters:
         - identity: dictionary of attributes defining the user performing the action
         - resource: dictionary of attributes defining the resource that access is required for
         - action: dictionary of attributes defining the action being performed
        '''
        pass
