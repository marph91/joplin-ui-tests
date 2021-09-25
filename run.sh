#!/bin/bash

# Run the testsuite multiple times. Only keep outputs in case of failure.

for (( i=0; i<"$1"; i++ )); do
    OUTPUT_DIR="debug_output_$i"
    mkdir -p "$OUTPUT_DIR"

    if python run_tests.py --debug-dir "$OUTPUT_DIR" &> "$OUTPUT_DIR/stdout.txt"; then
        echo "run $i, result: OK"
        rm -rf "$OUTPUT_DIR"
    else
        echo "run $i, result: FAIL"
    fi
done
