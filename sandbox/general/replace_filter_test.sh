./scripts/set_hint.sh TESTTACCHANGES 61c5fc9b7fbb752b2bc831be tacman_filter_issue_hint STOP_SERVER
echo
./bin/partner_share_tasks run --enable-taskbox --owner YABS_SERVER_SANDBOX_TESTS --tid `./scripts/last_task.sh TACMAN_FILTER_SERVER TESTTACCHANGES`
./scripts/clear_hint.sh TESTTACCHANGES 61c5fc9b7fbb752b2bc831be tacman_filter_issue_hint
echo
