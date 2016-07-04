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

	 Purpose:      Runs blocking tornado RequestHandlers on a separate threadpool.
"""

import logging
import traceback

import tornado.ioloop
from tornado.web import asynchronous, HTTPError

from async_dispatcher import AsyncDispatcher

# the maximum number of requests to handle concurrently
MAX_CONCURRENT_REQUESTS = 20
REQUEST_HANDLER_THREAD_POOL = AsyncDispatcher(num_threads=MAX_CONCURRENT_REQUESTS)


def asynchronize_tornado_handler(handler_class):
    """
    A helper function to turn a blocking handler into an async call
    :param handler_class: a tornado RequestHandler which should be made asynchronus
    :return: a class which does the same work on a threadpool
    """

    class AsyncTornadoHelper(handler_class):
        """
        A hollow wrapper class which runs requests asynchronously on a threadpool
        """

        def _do_work_and_report_error(self, work):
            try:
                # call the "real" method from the handler_class
                work()
            except HTTPError as ex:
                # request handler threw uncaught error
                logging.error(traceback.format_exc())
                # send http errors to client
                self.write(str(ex))
                self.set_status(ex.status_code)
            except Exception:
                # request handler threw uncaught error
                logging.error(traceback.format_exc())
                # send 500 error to client. Do not pass on error message
                self.write("500 Internal Server Error \n")
                self.set_status(500)
            finally:
                # finished needs to be reported from main tornado thread
                tornado.ioloop.IOLoop.instance().add_callback(
                    # report finished to main tornado thread:
                    lambda: self.finish()
                )

        @asynchronous
        def get(self, path=None):
            # bind the "real" method from the handler_class to run in another thread
            blocking_method = lambda: self._do_work_and_report_error(
                lambda: handler_class.get(self, path))
            # launch in another thread
            REQUEST_HANDLER_THREAD_POOL.run_as_asynch(blocking_method)

        @asynchronous
        def put(self, path=None):
            # bind the "real" method from the handler_class to run in another thread
            blocking_method = lambda: self._do_work_and_report_error(
                lambda: handler_class.put(self, path))
            # launch in another thread
            REQUEST_HANDLER_THREAD_POOL.run_as_asynch(blocking_method)

        @asynchronous
        def post(self, path=None):
            # bind the "real" method from the handler_class to run in another thread
            blocking_method = lambda: self._do_work_and_report_error(
                lambda: handler_class.post(self, path))
            # launch in another thread
            REQUEST_HANDLER_THREAD_POOL.run_as_asynch(blocking_method)

    # return the wrapped class instead of the original for Tornado to run asynchronously
    return AsyncTornadoHelper
