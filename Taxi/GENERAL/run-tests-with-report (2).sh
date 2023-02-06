#!/bin/sh

ROOT_DIR=$(node -e 'console.log(require("app-root-path").path)')
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
PROJECT_TESTS_DIST_DIR=$ROOT_DIR/projects/$PROJECT_NAME/tests/dist

export DOCKER_HOST_INTERNAL=$($SCRIPT_DIR/get-docker-intenral-host.sh)

cd $PROJECT_TESTS_DIST_DIR
echo "Run tests..."
hermione "$@"
tests_exit_status=$?
cd $SCRIPT_DIR


if [ $tests_exit_status -eq 1 ]; then
    echo "There are some tests errors."
    echo "$SCRIPT_DIR" $SCRIPT_DIR
else
   echo "All tests passed!"
fi

"$SCRIPT_DIR"/run-tests-gui.sh

echo "Quit with exit status" $tests_exit_status
exit $tests_exit_status
