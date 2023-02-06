#
# Regular cron jobs for the yandex-taxi-docker-integration-tests package
#
TESTS_DIR=/usr/lib/yandex/taxi-integration-tests
MAILTO=taxi-buildagent-pull-images@yandex-team.ru
7 *	* * *	buildfarm   cd $TESTS_DIR && scripts/image_updater.sh
