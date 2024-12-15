#!/bin/bash
TEST=$1

# Run the pipeline
/scratch/eric/llvm-project/build/bin/clang -c -emit-llvm -fpermissive -Wno-everything -ferror-limit=1 -Xclang -disable-O0-optnone -O0 "$TEST" -o - | \
/scratch/eric/llvm-project/build/bin/opt -S -passes=gvn --stats

# Capture exit codes of all commands in the pipeline
clang_exit_code=${PIPESTATUS[0]}
opt_exit_code=${PIPESTATUS[1]}

# Return the exit code of clang (or handle it however you like)
exit $clang_exit_code