#!/bin/bash

RUN_DIR="$(dirname "$(realpath "$0")")"
cd $RUN_DIR

PYTHONPATH=".:../../resources/" \
  fuzzinator \
  --wui --bind-ip-all \
  ../jerryscript.ini \
  guided.ini \
  -Dfuzzinator:config_root=$PWD/../../ \
  -Djerry:build_type=build_coverage \
  -Dfuzzinator:cost_budget=1
