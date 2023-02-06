#!/bin/bash
sample_export_path=$1
output_dir=$2

rm -r "$output_dir" 2> /dev/null

YT_PROXY=hahn ./robot/library/yuppie/prepare_yt_testdata.py --prefix "$sample_export_path" --path "$sample_export_path" --output-dir "$output_dir"
mkdir -p "$output_dir/perf/task_and_offer_input"
mkdir -p "$output_dir/dyn/task_and_offer_input"
