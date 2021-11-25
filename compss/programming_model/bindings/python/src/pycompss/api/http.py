#!/usr/bin/python
#
#  Copyright 2002-2021 Barcelona Supercomputing Center (www.bsc.es)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

# -*- coding: utf-8 -*-

"""
PyCOMPSs API - HTTP
==================
    HTTP Task decorator class.
"""

from pycompss.util.typing_helper import typing
from functools import wraps
import pycompss.util.context as context
from pycompss.api.commons.constants import SERVICE_NAME
from pycompss.api.commons.constants import RESOURCE
from pycompss.api.commons.constants import REQUEST
from pycompss.api.commons.constants import PAYLOAD
from pycompss.api.commons.constants import PAYLOAD_TYPE
from pycompss.api.commons.constants import PRODUCES
from pycompss.api.commons.constants import UPDATES
from pycompss.api.commons.decorator import keep_arguments
from pycompss.api.commons.decorator import CORE_ELEMENT_KEY
from pycompss.runtime.task.core_element import CE
from pycompss.util.arguments import check_arguments
from pycompss.util.serialization import serializer


if __debug__:
    import logging
    logger = logging.getLogger(__name__)

MANDATORY_ARGUMENTS = {SERVICE_NAME,
                       RESOURCE,
                       REQUEST}
SUPPORTED_ARGUMENTS = {PAYLOAD,
                       PAYLOAD_TYPE,
                       PRODUCES,
                       UPDATES}
DEPRECATED_ARGUMENTS = set()  # type: typing.Set[str]


class HTTP(object):
    """
    This decorator also preserves the argspec, but includes the __init__ and
    __call__ methods, useful on mpi task creation.
    """

    def __init__(self, *args, **kwargs):
        # type: (*typing.Any, **typing.Any) -> None
        """ Store arguments passed to the decorator.

        self = itself.
        args = not used.
        kwargs = dictionary with the given http parameters.

        :param args: Arguments
        :param kwargs: Keyword arguments
        """
        decorator_name = "".join(("@", HTTP.__name__.lower()))
        # super(HTTP, self).__init__(decorator_name, *args, **kwargs)
        self.decorator_name = decorator_name
        self.args = args
        self.kwargs = kwargs
        self.scope = context.in_pycompss()
        self.core_element = None  # type: typing.Any
        self.core_element_configured = False
        self.task_type = "http"
        if self.scope:
            # Check the arguments
            check_arguments(MANDATORY_ARGUMENTS,
                            DEPRECATED_ARGUMENTS,
                            SUPPORTED_ARGUMENTS | DEPRECATED_ARGUMENTS,
                            list(kwargs.keys()),
                            decorator_name)

    def __call__(self, user_function):
        # type: (typing.Callable) -> typing.Callable
        """ Parse and set the http parameters within the task core element.

        :param user_function: Function to decorate.
        :return: Decorated function.
        """

        @wraps(user_function)
        def http_f(*args, **kwargs):
            # type: (*typing.Any, **typing.Any) -> typing.Any
            return self.__decorator_body__(user_function, args, kwargs)

        http_f.__doc__ = user_function.__doc__
        return http_f

    def __decorator_body__(self, user_function, args, kwargs):
        # type: (typing.Callable, tuple, dict) -> typing.Any
        # force to serialize with JSON
        serializer.FORCED_SERIALIZER = 4
        if not self.scope:
            # run http
            self.__run_http__(args, kwargs)

        if __debug__:
            logger.debug("Executing http_f wrapper.")

        if (context.in_master() or context.is_nesting_enabled()) \
                and not self.core_element_configured:
            # master code - or worker with nesting enabled
            self.__configure_core_element__(kwargs, user_function)

        with keep_arguments(args, kwargs):
            # Call the method
            ret = user_function(*args, **kwargs)

        return ret

    def __run_http__(self, *args, **kwargs):
        # type: (*typing.Any, **typing.Any) -> int
        """ HTTP tasks are meant to be dummy.

        :param args: Arguments received from call.
        :param kwargs: Keyword arguments received from call.
        :return: Execution return code.
        """
        print("running http")
        return 200

    def __configure_core_element__(self, kwargs, user_function):
        # type: (dict, typing.Callable) -> None
        """ Include the registering info related to @http.

        IMPORTANT! Updates self.kwargs[CORE_ELEMENT_KEY].

        :param kwargs: Keyword arguments received from call.
        :param user_function: Decorated function.
        :return: None
        """
        if __debug__:
            logger.debug("Configuring @http core element.")
        impl_type = "HTTP"
        impl_args = [self.kwargs["service_name"],
                     self.kwargs["resource"],
                     self.kwargs["request"],
                     self.kwargs.get("payload", '#'),
                     self.kwargs.get("payload_type", "application/json"),
                     self.kwargs.get("produces", '#'),
                     self.kwargs.get("updates", '#')]

        if CORE_ELEMENT_KEY in kwargs:
            # Core element has already been created in a higher level decorator
            # (e.g. @constraint)
            kwargs[CORE_ELEMENT_KEY].set_impl_type(impl_type)
            kwargs[CORE_ELEMENT_KEY].set_impl_type_args(impl_args)
        else:
            # @binary is in the top of the decorators stack.
            # Instantiate a new core element object, update it and include
            # it into kwarg
            core_element = CE()
            core_element.set_impl_type(impl_type)
            core_element.set_impl_type_args(impl_args)
            kwargs[CORE_ELEMENT_KEY] = core_element

        # Set as configured
        self.core_element_configured = True


# ########################################################################### #
# ##################### HTTP DECORATOR ALTERNATIVE NAME ##################### #
# ########################################################################### #

http = HTTP
