#!/bin/bash

  #
  # HELPER FUNCTIONS
  #

  # Run a coverage report for a module
  run() {
    coverage run --source="src/pycompss" \
                 --omit="/usr/lib/*" \
                 --omit="src/pycompss/api/tests_parallel/*" \
                 nose_tests.py False
                 # --omit="src/pycompss/util/translators/*" \
    coverage report -m
  }


  #
  # MAIN
  #

  # Run coverage on pycompss folder
  run

  # Generate XML file
  coverage xml
  ev=$?
  if [ "$ev" -ne 0 ]; then
    echo "[ERROR] Coverage XML generation failed with exit value: $ev"
    exit $ev
  fi

  # Exit all ok
  exit 0
