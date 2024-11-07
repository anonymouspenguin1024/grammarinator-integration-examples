#!/bin/bash
set -e

ROOT_DIR="$(dirname "$(realpath "$0")")"

cd $ROOT_DIR
echo "Create Python virtual environment"
mkdir -p .venv
virtualenv -p python3 .venv
source .venv/bin/activate

echo "Get requirements"
echo "================"

cd $ROOT_DIR/resources

echo "Install Python requirements"
pip3 install git+https://github.com/renatahodovan/fuzzinator.git@master
pip3 install git+https://github.com/renatahodovan/grammarinator.git@master

echo "Clone grammars-v4"
git clone --depth=1 https://github.com/antlr/grammars-v4.git

echo "Clone JerryScript"
git clone --depth=1 https://github.com/jerryscript-project/jerryscript.git

echo "Create fuzzer from ECMAScript grammar"
grammarinator-process grammars-v4/javascript/ecmascript/ECMAScript.g4 --no-actions -o .

echo "Create fuzzer population from the JavaScript tests of JerryScript"
mkdir -p population/
grammarinator-parse \
    grammars-v4/javascript/ecmascript/Python3/ECMAScript.g4 \
    -r program \
    --glob jerryscript/tests/**/*.js \
    --transformer=js_transformer.remove_asserts \
    --sys-path . \
    --sys-recursion-limit=10000 \
    -o population/

echo "Build various JerryScript configurations"
echo "========================================"

cd $ROOT_DIR/resources/jerryscript

echo "Build JerryScript with default configuration"
python3 tools/build.py --clean \
        --compile-flag=-fsanitize=address \
        --compile-flag=-fno-omit-frame-pointer \
        --compile-flag=-fno-common \
        --compile-flag=-g \
        --compile-flag=-Wno-error \
        --strip=off \
        --lto=off \
        --profile=es.next \
        --error-messages=on \
        --logging=on \
        --builddir=build_default

echo "Build JerryScript with Clang coverage"
CC=clang python3 tools/build.py --clean \
        --compile-flag=-fsanitize=address \
        --compile-flag=-fsanitize-coverage=edge,trace-cmp,trace-pc-guard \
        --compile-flag=-fno-omit-frame-pointer \
        --compile-flag=-fno-common \
        --compile-flag=-g \
        --compile-flag=-Wno-error \
        --strip=off \
        --lto=off \
        --profile=es.next \
        --error-messages=on \
        --logging=on \
        --builddir=build_coverage
