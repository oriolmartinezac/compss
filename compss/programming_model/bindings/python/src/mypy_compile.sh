#!/bin/bash

###################################
## Compilation with mypyc script ##
###################################

mypyc --ignore-missing-imports --exclude 'pycompss\/((tests)\/|(dds)\/|(functions\/data_tasks.py)|(functions\/elapsed_time.py)|(streams\/)|(runtime\/launch.py)|(util\/translators\/code_replacer\/tests\/original.py)|(util\/translators\/py2pycompss\/components\/loop_taskificator.py)|(util\/interactive\/events.py)|(interactive.py)|(__main__.py))$' ./pycompss/

# Copy the main pycompss compiled module one folder up to be found using
# python3 -m pycompss. Alternative would be to force use only python3 or
# define the path in PYTHONPATH (which can be dangerous).
cp *__mypyc* ..
