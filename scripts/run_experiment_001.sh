#!/bin/bash

set -u

for threads in 1 2 4; do
    for run in 1 2 3 4 5; do
        run_id="t${threads}-r$(printf '%02d' "$run")"

        echo
        echo "========================================"
        echo "Running $run_id"
        echo "========================================"

        ./scripts/run_inference.py \
            --threads "$threads" \
            --run-id "$run_id" \
            < benchmark/prompt.txt

        status=$?

        if [ "$status" -ne 0 ]; then
            echo "ERROR: $run_id failed with status $status"
            exit "$status"
        fi
    done
done

echo
echo "Experiment 001 complete."
