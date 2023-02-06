#!/usr/bin/env bash

set -ex

BUCKET_NUMBER=0
MR_PREFIX="//tmp/$USER/jupiter_test"
JUPITER_PREFIX="//home/jupiter"
MAIN_SELECTING_RULE="random_crawl"
SERVER_NAME="arnold"
OPERATION_WEIGHT=1
SRPOOL_KEEP_MAX_AGE_DAYS=30
CURRENT_STATE=""
PREV_STATE=""


export YT_PROXY=$SERVER_NAME

if [ -z "$CURRENT_STATE" ]; then
    CURRENT_STATE=`yt get //home/jupiter/@jupiter_meta/production_current_state | tr -d \"`
fi

if [ -z "$PREV_STATE" ]; then
    PREV_STATE=`yt get //home/jupiter/@jupiter_meta/production_prev_state | tr -d \"`
fi


yt copy --recursive --force \
    $JUPITER_PREFIX/selectionrank/$CURRENT_STATE \
    $MR_PREFIX/selectionrank/$CURRENT_STATE
yt copy --recursive --force \
    $JUPITER_PREFIX/srpool/$PREV_STATE \
    $MR_PREFIX/srpool/$PREV_STATE


./srpool TrackNewSRLearningPoolUrls \
    --server-name $SERVER_NAME \
    --mr-prefix $MR_PREFIX \
    --prev-state $PREV_STATE \
    --current-state $CURRENT_STATE \
    --bucket-number $BUCKET_NUMBER \
    --operation-weight $OPERATION_WEIGHT \
    --selectionrank-main-selecting-rule $MAIN_SELECTING_RULE \
    --srpool-keep-max-age-days $SRPOOL_KEEP_MAX_AGE_DAYS

