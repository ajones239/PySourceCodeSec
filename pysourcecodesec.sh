#!/bin/sh

if ! [[ $PYTHON_ENV ]]; then
    $PYTHON_ENV=$(which python)
fi
$PYTHON_ENV ./pysourcecodesec.py $@ 2> /dev/null
