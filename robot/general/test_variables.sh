CONFIGURATION=test

MR_BASE_PATH_DEFAULT='//home/kwyt-test'
DST_BASE_PATH_DEFAULT='//home/kwyt-test/sample/kwyt'
DST_IMPORTS_BASE_PATH_DAFAULT='//home/kwyt-test/sample/kwyt-import'
IMPORTS_BASE_PATH_DEFAULT='//home/kwyt-test/import'

export YT_POOL=${YT_POOL:-kwyt-test}
export YT_SPEC="{ \
    \"intermediate_data_account\": \"kwyt-test\", \
    \"memory_reserve_factor\": 1, \
    \"pool\": \"$YT_POOL\", \
    \"owners\": [\"kwyt\", \"lexeyo\"] \
    }" # YT_POOL is ignored if YT_SPEC is provided - see YT-5841

SOLOMON_CLUSTER='testing'
