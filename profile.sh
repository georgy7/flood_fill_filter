#!/bin/sh

# python3 -m pip install pytest-profiling

python3 -m pytest --single-thread --profile-svg
