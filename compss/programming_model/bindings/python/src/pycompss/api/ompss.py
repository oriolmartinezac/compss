#!/usr/bin/python
#
#  Copyright 2002-2019 Barcelona Supercomputing Center (www.bsc.es)
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
PyCOMPSs API - OMPSS
==================
    This file contains the class constraint, needed for the OmpSs task
    definition through the decorator.
"""

from functools import wraps
import pycompss.util.context as context
from pycompss.api.commons.error_msgs import not_in_pycompss
from pycompss.api.commons.decorator import PyCOMPSsDecorator
from pycompss.api.commons.decorator import process_computing_nodes
from pycompss.api.commons.decorator import get_module
from pycompss.api.commons.decorator import keep_arguments
from pycompss.util.arguments import check_arguments

if __debug__:
    import logging
    logger = logging.getLogger(__name__)

MANDATORY_ARGUMENTS = {'binary'}
SUPPORTED_ARGUMENTS = {'computing_nodes',
                       'working_dir',
                       'binary',
                       'fail_by_exit_value'}
DEPRECATED_ARGUMENTS = {'computingNodes',
                        'workingDir'}


class OmpSs(PyCOMPSsDecorator):
    """
    This decorator also preserves the argspec, but includes the __init__ and
    __call__ methods, useful on mpi task creation.
    """

    def __init__(self, *args, **kwargs):
        """
        Store arguments passed to the decorator
        # self = itself.
        # args = not used.
        # kwargs = dictionary with the given constraints.

        :param args: Arguments
        :param kwargs: Keyword arguments
        """
        decorator_name = '@' + self.__class__.__name__.lower()
        super(self.__class__, self).__init__(decorator_name, *args, **kwargs)
        if self.scope:
            # Check the arguments
            check_arguments(MANDATORY_ARGUMENTS,
                            DEPRECATED_ARGUMENTS,
                            SUPPORTED_ARGUMENTS | DEPRECATED_ARGUMENTS,
                            list(kwargs.keys()),
                            decorator_name)

            # Get the computing nodes
            process_computing_nodes(decorator_name, self.kwargs)
        else:
            pass

    def __call__(self, func):
        """
        Parse and set the ompss parameters within the task core element.

        :param func: Function to decorate
        :return: Decorated function.
        """
        @wraps(func)
        def ompss_f(*args, **kwargs):
            if not self.scope:
                raise Exception(not_in_pycompss("ompss"))

            if __debug__:
                logger.debug("Executing ompss_f wrapper.")

            if context.in_master():
                # master code
                self.module = get_module(func)

                if not self.registered:
                    # Register

                    # Resolve @ompss specific parameters
                    binary = self.kwargs['binary']

                    # Resolve the working directory
                    self.__resolve_working_dir__()
                    # Resolve the fail by exit value
                    self.__resolve_fail_by_exit_value__()

                    impl_signature = 'OMPSS.' + binary
                    impl_args = [binary,
                                 self.kwargs['working_dir'],
                                 self.kwargs['fail_by_exit_value']]

                    # Retrieve the base core_element established at @task
                    # decorator and update the core element information with
                    # the @ompss information
                    from pycompss.api.task import current_core_element as cce
                    cce.set_impl_type("OMPSS")
                    cce.set_impl_signature(impl_signature)
                    cce.set_impl_type_args(impl_args)

                    # Set as registered
                    self.registered = True
            else:
                # worker code
                pass

            # Set the computing_nodes variable in kwargs for its usage
            # in @task decorator
            kwargs['computing_nodes'] = self.kwargs['computing_nodes']

            with keep_arguments(args, kwargs, prepend_strings=False):
                # Call the method
                ret = func(*args, **kwargs)

            return ret

        ompss_f.__doc__ = func.__doc__
        return ompss_f


# ########################################################################### #
# #################### OMPSs DECORATOR ALTERNATIVE NAME ##################### #
# ########################################################################### #

ompss = OmpSs
