#!/usr/bin/env bash

# AB_config json for BucketTest could also be found in this directory

# AB test dates (for metrics)
begin=2020-09-21
end=2020-10-04

# AA test dates (for metrics)
aa_begin=$(date -d "${begin} -16 days" +%Y-%m-%d)
aa_end=$(date -d "${end} -16 days" +%Y-%m-%d)

# split dates (for AB split)
split_begin=$begin
split_end=$end

metrics_path='//home/taxi_ml/production/autoorder/demand_v5_1/metrics/{}'
split_path='//home/taxi_ml/dev/kozlatkis/lavka_sandbox/ab_results/split_wo_last'
input_path='//home/taxi_ml/dev/kozlatkis/lavka_sandbox/ab_results/input_wo_last'
input_wo_outliers_path='//home/taxi_ml/dev/kozlatkis/lavka_sandbox/ab_results/input_wo_last_wo_golden2'

#shelf_life_slices='14,30,60'
shelf_life_slices='-'

last_week_delta=16

python get_ab_split.py --path $split_path --start-date $split_begin --end-date $split_end

python mk_input_for_buckettest.py \
    --begin $begin --end $end \
    --aa-begin $aa_begin --aa-end $aa_end \
    --metrics-path $metrics_path --split-path $split_path \
    --result-path $input_path \
    --shelf-life-slices $shelf_life_slices \
    --last-week-delta $last_week_delta

python cut_outliers.py --path-from $input_path --path-to $input_wo_outliers_path
