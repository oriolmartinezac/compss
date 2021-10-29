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
PyCOMPSs API - MPMD MPI
==================
    This file contains the class mpmd mpi, needed for the multiple program mpi
    definition through the decorator.
"""

from functools import wraps
import pycompss.util.context as context
from pycompss.api.commons.decorator import PyCOMPSsDecorator
from pycompss.api.commons.decorator import keep_arguments
from pycompss.api.commons.decorator import CORE_ELEMENT_KEY
from pycompss.api.commons.decorator import run_command
from pycompss.runtime.task.core_element import CE
from pycompss.util.arguments import check_arguments
from pycompss.util.exceptions import PyCOMPSsException


if __debug__:
    import logging

    logger = logging.getLogger(__name__)

MANDATORY_ARGUMENTS = {'runner'}
SUPPORTED_ARGUMENTS = {'programs',
                       'working_dir',
                       'processes_per_node',
                       'fail_by_exit_value'}
DEPRECATED_ARGUMENTS = set()


class MPMDMPI(PyCOMPSsDecorator):
    """
    """

    __slots__ = ['task_type', 'decorator_name']

    def __init__(self, *args, **kwargs):
        """ Store arguments passed to the decorator.

        self = itself.
        args = not used.
        kwargs = dictionary with the given mpi parameters.

        :param args: Arguments
        :param kwargs: Keyword arguments
        """
        self.task_type = "mpmd_mpi"
        self.decorator_name = "".join(('@', MPMDMPI.__name__.lower()))
        super(MPMDMPI, self).__init__(self.decorator_name, *args, **kwargs)
        if self.scope:
            if __debug__:
                logger.debug("Init @mpmd_mpi decorator...")

            # Add <param_name>_layout params to SUPPORTED_ARGUMENTS
            for key in self.kwargs.keys():
                if "_layout" in key:
                    SUPPORTED_ARGUMENTS.add(key)

            # Check the arguments
            check_arguments(MANDATORY_ARGUMENTS,
                            DEPRECATED_ARGUMENTS,
                            SUPPORTED_ARGUMENTS | DEPRECATED_ARGUMENTS,
                            list(kwargs.keys()),
                            self.decorator_name)

    def __call__(self, user_function):
        """ Parse and set the mpmd mpi parameters within the task core element.

        :param user_function: Function to decorate.
        :return: Decorated function.
        """

        @wraps(user_function)
        def mpmd_mpi(*args, **kwargs):
            return self.__decorator_body__(user_function, args, kwargs)

        mpmd_mpi.__doc__ = user_function.__doc__
        return mpmd_mpi

    def __decorator_body__(self, user_function, args, kwargs):
        if not self.scope:
            raise NotImplementedError

        if __debug__:
            logger.debug("Executing mpmd_mpi_f wrapper.")

        if (context.in_master() or context.is_nesting_enabled()) \
                and not self.core_element_configured:
            # master code - or worker with nesting enabled
            self.__configure_core_element__(kwargs, user_function)

        # The processes parameter will have to go down until the execution
        # is invoked. To this end, set the computing_nodes variable in kwargs
        # for its usage in @task decorator
        # WARNING: processes can be an int, a env string, a str with
        #          dynamic variable name.
        # if "processes" in self.kwargs:
        #     kwargs['computing_nodes'] = self.kwargs['processes']
        # else:
        #     # If processes not defined, check computing_units or set default
        #     self.__process_computing_nodes__(self.decorator_name)
        #     kwargs['computing_nodes'] = self.kwargs['computing_nodes']
        if "processes_per_node" in self.kwargs:
            kwargs['processes_per_node'] = self.kwargs['processes_per_node']
        else:
            kwargs['processes_per_node'] = 1

        with keep_arguments(args, kwargs):
            # Call the method
            ret = user_function(*args, **kwargs)

        return ret

    def _get_programs_params(self):
        # type: () -> list
        """ Resolve the collection layout, such as blocks, strides, etc.

        :return: list(param_name, block_count, block_length, stride)
        :raises PyCOMPSsException: If the collection layout does not contain block_count.
        """
        programs = self.kwargs["programs"]
        programs_params = [len(programs)]

        for program in programs:
            if not isinstance(program, dict):
                raise PyCOMPSsException("Incorrect 'program' param in MPMD MPI")

            binary = program.get("binary", None)
            if not binary:
                raise PyCOMPSsException("No binary file provided for MPMD MPI")

            params = program.get("params", "#")
            procs = program.get("processes", "#")
            programs_params.extend([binary, params, procs])

        return programs_params

    def __configure_core_element__(self, kwargs, user_function):
        # type: (dict, ...) -> None
        """ Include the registering info related to @mpmd_mpi.

        IMPORTANT! Updates self.kwargs[CORE_ELEMENT_KEY].

        :param kwargs: Keyword arguments received from call.
        :param user_function: Decorated function.
        :return: None
        """
        if __debug__:
            logger.debug("Configuring @mpmd_mpi core element.")

        # Resolve @mpmd_mpi specific parameters
        impl_type = "MPMDMPI"
        runner = self.kwargs['runner']

        # Resolve the working directory
        self.__resolve_working_dir__()
        # Resolve the fail by exit value
        self.__resolve_fail_by_exit_value__()

        ppn = str(self.kwargs.get("processes_per_node", 1))
        impl_signature = '.'.join((impl_type, str(ppn)))

        prog_params = self._get_programs_params()

        impl_args = [runner,
                     ppn,
                     self.kwargs['working_dir'],
                     self.kwargs['fail_by_exit_value']]
        impl_args.extend(prog_params)

        if CORE_ELEMENT_KEY in kwargs:
            kwargs[CORE_ELEMENT_KEY].set_impl_type(impl_type)
            kwargs[CORE_ELEMENT_KEY].set_impl_signature(impl_signature)
            kwargs[CORE_ELEMENT_KEY].set_impl_type_args(impl_args)
        else:
            core_element = CE()
            core_element.set_impl_type(impl_type)
            core_element.set_impl_signature(impl_signature)
            core_element.set_impl_type_args(impl_args)
            kwargs[CORE_ELEMENT_KEY] = core_element

        # Set as configured
        self.core_element_configured = True


# ########################################################################### #
# ##################### MPI DECORATOR ALTERNATIVE NAME ###################### #
# ########################################################################### #

mpmd_mpi = MPMDMPI
