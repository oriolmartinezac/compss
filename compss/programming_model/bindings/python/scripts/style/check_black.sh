#!/bin/bash

CURRENT_DIR="$(pwd)"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# shellcheck disable=SC2164
cd "${SCRIPT_DIR}/../../src/"

#################
## Check Black ##
#################

black --check --diff ./pycompss/
ev=$?
if [ "$ev" -ne 0 ]; then
  echo "[ERROR] Black check failed with exit value: $ev"
  echo ""
  echo "Please, run:"
  echo "    black $(pwd)/pycompss"
  echo "Then, review changes and push them again."
  echo ""
  exit $ev
fi

# shellcheck disable=SC2164
cd "${CURRENT_DIR}"

echo "[OK] Black check success"

# Exit all ok
exit 0
