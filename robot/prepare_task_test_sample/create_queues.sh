export YT_PROXY=hahn

prefix=//home/jupiter-test/blrt_users/alexanderplat_task_sample/external_data/caesar

ya make ./ads/bsyeti/big_rt/cli
./ads/bsyeti/big_rt/cli/big_rt_cli queue create --shards 1 "$prefix"/BannerLandTaskOrderLog
./ads/bsyeti/big_rt/cli/big_rt_cli queue create --shards 1 "$prefix"/BannerLandTaskBannerLog

./ads/bsyeti/big_rt/cli/big_rt_cli consumer create --ignore-in-trimming 0 "$prefix"/BannerLandTaskOrderLog blrt-task-resharder
./ads/bsyeti/big_rt/cli/big_rt_cli consumer create --ignore-in-trimming 0 "$prefix"/BannerLandTaskBannerLog blrt-task-resharder

ya make ./junk/alexanderplat/blrt_task_sample/event_converter
./junk/alexanderplat/blrt_task_sample/event_converter/event_converter \
--order-table "$prefix"/Order \
--banner-table "$prefix"/Banner \
--order-event-table "$prefix"/BannerLandTaskOrderLog \
--banner-event-table "$prefix"/BannerLandTaskBannerLog

yt unmount-table --sync "$prefix"/BannerLandTaskOrderLog/queue
yt unmount-table --sync "$prefix"/BannerLandTaskBannerLog/queue
