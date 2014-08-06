#!/bin/sh

set -e

SRC_DIR="$(dirname $(readlink -f $0))"
virtualenv "${SRC_DIR}/venv"
source "${SRC_DIR}/venv/bin/activate"
pip install flup python-mpd2 simplejson youtube-dl
