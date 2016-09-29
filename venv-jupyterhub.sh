#!/bin/sh

CNF_DIR="$(dirname "$(readlink -f "$0")")"
. "${CNF_DIR}/../venv/bin/activate"

[ -f "${CNF_DIR}/jupyterhub_config.py" ] || jupyterhub --generate-config -f "${CNF_DIR}/jupyterhub_config.py"

jupyterhub --no-ssl -f "${CNF_DIR}/jupyterhub_config.py"

deactivate
