ROOT_DIR="$(dirname "$(realpath "$0")")"

cd $ROOT_DIR
cd $ROOT_DIR/resources

echo "Create fuzzer population from the JavaScript tests of JerryScript"
mkdir -p population/
grammarinator-parse \
    grammars-v4/javascript/ecmascript/Python3/ECMAScript.g4 \
    -r program \
    -i jerryscript/tests/jerry/*.js \
    --transformer=js_transformer.remove_asserts \
    --sys-path . \
    --sys-recursion-limit=100000 \
    -v \
    -o population/