#!/bin/sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$SCRIPT_DIR"/../../../tests/temp/dist
hermione "$@"
tests_exit_status=$?
cd $SCRIPT_DIR

if [ $tests_exit_status -eq 1 ]; then
    echo "There are some tests errors."
    echo "$SCRIPT_DIR" $SCRIPT_DIR
    "$SCRIPT_DIR"/run-tests-gui.sh
else
   echo "All tests passed!"
fi

echo "Quit with exit status" $tests_exit_status
exit $tests_exit_status
