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

	 Purpose:     Simple file upload handler based on Tornado
"""

import json
import logging
import mimetypes
import sys
import traceback
from threading import Event

import tornado.httpserver
import tornado.ioloop
import tornado.log
import tornado.options
import tornado.web
from tornado.options import define, options

from asynchronize_tornado_handler import asynchronize_tornado_handler
from data_logger_client import DataLoggerClient
from package_manager import PackageManager
from swift_repository import SwiftRepository
from aws_repository import S3Repository
from fs_repository import FsRepository
from exceptiondef import Forbidden

define("port", default=8888, help="run on the given port", type=int)

tornado.options.parse_command_line()
options.logging = None

class PackageRepositoryRestServer(object):
    """
    A package which starts the tornado server
    """

    def __init__(self, configuration):
        # This event will fire after the server starts listening:
        self._started = Event()
        self.config = configuration

    def run(self):
        """
        Start running a rest interface using tornado
        """
        if 'SwiftRepository' in self.config:
            package_repository = SwiftRepository(self.config['SwiftRepository'])
        elif 'S3Repository' in self.config:
            package_repository = S3Repository(self.config['S3Repository'])
        elif 'FsRepository'in self.config:
            package_repository = FsRepository(self.config['FsRepository']['location'])
        else:
            logging.error("missing repository configuration, should be SwiftRepository, S3Repository or FsRepository")
            self.stop()

        data_logger = DataLoggerClient(self.config['config'])
        package_manager = PackageManager(package_repository, data_logger)

        # setup various handlers:
        class Application(tornado.web.Application):
            def __init__(self):
                handlers = [
                    (r"/packages/(.+)", asynchronize_tornado_handler(PackageHandler)),
                    (r"/packages", PackagesHandler),
                ]
                tornado.web.Application.__init__(self, handlers)

        class PackageHandler(tornado.web.RequestHandler):
            def get(self, path):
                """
                REST interface for getting packages from the repository
                :param path:
                :return:
                """
                logging.info("Getting: %s", path)
                content_type, _ = mimetypes.guess_type(path)
                if content_type:
                    self.set_header('Content-Type', content_type)
                try:
                    self.write(package_manager.read_package(path, self.get_argument("user.name")))
                except (KeyError, IOError):
                    logging.error(traceback.format_exc())
                    self.write("404 not found")
                    self.set_status(404)
                except Forbidden as ex:
                    logging.error(traceback.format_exc())
                    self.write("403 Forbidden - %s" % str(ex.msg))
                    self.set_status(403)

            def put(self, path):
                """
                REST interface for adding packages to the repository
                :param path:
                :return:
                """
                logging.info("Putting: %s", path)
                try:
                    package_manager.validate_package_name(path)
                    package_manager.put_package(path, self.request.body, self.get_argument("user.name"))
                except ValueError, exception:
                    logging.error(traceback.format_exc())
                    self.set_status(400)
                    self.write(str(exception) + "\n")
                except Forbidden as ex:
                    logging.error(traceback.format_exc())
                    self.write("403 Forbidden - %s" % str(ex.msg))
                    self.set_status(403)

            def delete(self, path):
                """
                REST interface for deleting packages from the repository
                :param path:
                :return:
                """
                logging.info("Deleting: %s", path)
                try:
                    package_manager.delete_package(path, self.get_argument("user.name"))
                except KeyError:
                    logging.error(traceback.format_exc())
                    self.write("404 not found")
                    self.set_status(404)
                except Forbidden as ex:
                    logging.error(traceback.format_exc())
                    self.write("403 Forbidden - %s" % str(ex.msg))
                    self.set_status(403)

        class PackagesHandler(tornado.web.RequestHandler):
            def get(self, path=None):
                """
                REST interface for getting a list of packages from the repository
                :return:
                """
                logging.info("fetching package list... ")
                try:
                    # group packages by version and return:
                    recency = None
                    recency_parameter = self.get_arguments('recency')
                    if recency_parameter:
                        recency = int(recency_parameter[0])
                    ret = package_manager.get_packages_grouped_by_version(self.get_argument("user.name"), number_of_versions_to_list=recency)
                    # convert to json and return
                    self.write(json.dumps(ret))
                    # silencing pylint about unused variable
                    if not path:
                        path = False
                except Forbidden as ex:
                    logging.error(traceback.format_exc())
                    self.write("403 Forbidden - %s" % str(ex.msg))
                    self.set_status(403)

        logging.info("Starting up...")
        http_server = tornado.httpserver.HTTPServer(Application(), max_buffer_size=100000000)
        http_server.listen(options.port)
        logging.info("Listening on port: %s", str(options.port))
        # notify that server has started:
        self._started.set()
        # start handling incomming requests:
        tornado.ioloop.IOLoop.instance().start()

    def wait_for_server_to_start(self):
        """
        Blocks until the server istarts listening for incomming requests
        """
        if not self._started.is_set():
            logging.info("waiting for server to start...")
            self._started.wait()

    def stop(self):
        """
        Stops server
        """
        tornado.ioloop.IOLoop.instance().stop()


def main():
    # run the server automatically if module is run as main:
    # try to open configuration file
    with open('pr-config.json', 'r') as config_file:
        # load the config file as json
        config = json.load(config_file)
        # run with configuration

    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.getLevelName(config['config']['log_level']),
                        stream=sys.stderr)

    PackageRepositoryRestServer(config).run()


if __name__ == "__main__":
    main()
