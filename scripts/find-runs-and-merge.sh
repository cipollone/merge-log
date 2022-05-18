#!/bin/bash
files=$(find $1 -type f -name 'evaluation*.yaml' -print)
xargs -t -o poetry run python -m merge_logs --format 2 --out $2 <<<$files
