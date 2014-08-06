#!/bin/sh

SRC_DIR="$(dirname $(readlink -f $0))"
source "${SRC_DIR}/venv/bin/activate"
"${SRC_DIR}/mpd_add_youtube.py"
