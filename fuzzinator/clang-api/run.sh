#!/bin/bash

RUN_DIR="$(dirname "$(realpath "$0")")"
cd $RUN_DIR

PYTHONPATH=".:../../resources/" \
  fuzzinator \
  --wui --bind-ip-all \
  ../clang.ini \
  api.ini \
  -Dfuzzinator:config_root=$PWD/../../ \
  -Dfuzzinator:cost_budget=1
