include(CTest)

add_test(
  NAME tests-pytest
  COMMAND
    env PYTHONPATH=${CMAKE_SOURCE_DIR}/submodules/pytest/src:$ENV{PYTHONPATH}
    ${PYTHON} -m pytest --tests-dir ${CMAKE_CURRENT_SOURCE_DIR}
    --yt-upload-settings ${ALL_YT_UPLOAD_SETTINGS}
       -vv -x -c ${CMAKE_CURRENT_SOURCE_DIR}/pytest.ini
       --junitxml=${CMAKE_BINARY_DIR}/test-results/junit-tests-pytest.xml
       -p no:name_of_plugin -p no:pytest-teamcity
       ${CMAKE_CURRENT_SOURCE_DIR}/tests
)
