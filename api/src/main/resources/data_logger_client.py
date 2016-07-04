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

	 Purpose:    REST client for the external data-logging API
"""

import time
import logging
import re
import requests

def milli_time():
    return int(round(time.time() * 1000))


class DataLoggerClient(object):
    """
    A rest client for the data logger api
    Important, this file is an extract and duplicate of deployment-manager code. might want to look into implementing
     a shared code base for "library" type modules
    """
    # a list of endpoints that can be called:
    ENDPOINT_PACKAGES = "package_callback"

    # a list of states that can be reported:
    STATE_CREATED = "CREATED"
    STATE_NOTCREATED = "NOTCREATED"

    def __init__(self, config):
        self._config = config
        self.rest_client = requests

    def report_event(self, name, endpoint_type, state, information=None):
        logging.debug("callback: %s %s %s", endpoint_type, name, state)
        callback_url = self._config[endpoint_type]
        if callback_url:
            callback_payload = {
                "data": [
                    {
                        "id": re.sub(r'\.tar\.gz$', '', name),
                        "state": state,
                        "timestamp": milli_time()
                    }
                ],
                "timestamp": milli_time()
            }
            # add additional optional information
            if information:
                callback_payload["data"][0]["information"] = information
            logging.debug(callback_url + " - " + str(callback_payload))
            self.rest_client.post(callback_url, json=callback_payload)
