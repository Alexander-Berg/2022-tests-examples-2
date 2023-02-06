include(CTest)

set(GENNGINX_SCRIPT
    ${CMAKE_SOURCE_DIR}/submodules/testsuite/taxi_tests/utils/gennginx.py)

if(TESTSUITE_PYTEST_DIRS)
  add_test(
    NAME testsuite
    COMMAND ${CMAKE_CURRENT_BINARY_DIR}/runtests
            -vv
            --junitxml=${CMAKE_BINARY_DIR}/test-results/junit-testsuite.xml
            -p no:name_of_plugin -p no:pytest-teamcity
            -p tests_plugins.rerunfailures --reruns 1 --skip-flaps
            --mockserver-nofail
            ${TESTSUITE_PYTEST_DIRS}
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  )
  set_tests_properties(testsuite PROPERTIES TIMEOUT 10000)

  if($ENV{IS_TEAMCITY})
      list(APPEND PYTEST_FLAGS "-n4")
  endif($ENV{IS_TEAMCITY})

  if(TESTSUITE_NGINX_SERVICES)
    add_custom_target(testsuite-configs ALL
      COMMAND mkdir -p ${CMAKE_BINARY_DIR}/test-results
      DEPENDS testsuite-fixtures
              testsuite-nginx-config
    )

    list(REMOVE_DUPLICATES TESTSUITE_NGINX_SERVICES)

    add_custom_target(
      testsuite-nginx-config-tpl
      COMMENT "Generating nginx.conf.tpl for testsuite"
      COMMAND mkdir -p ${CMAKE_CURRENT_BINARY_DIR}/nginx
      COMMAND mkdir -p ${CMAKE_CURRENT_BINARY_DIR}/configs
      COMMAND ${TESTSUITE_PYTHON}
              ${GENNGINX_SCRIPT}
              create
              -i=${CMAKE_CURRENT_SOURCE_DIR}/configs/nginx
              -b=${CMAKE_CURRENT_BINARY_DIR}/tmp/nginx
              -s ${TESTSUITE_NGINX_SERVICES}
              -o=${CMAKE_CURRENT_BINARY_DIR}/configs
      DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/configs/nginx/nginx.conf.in
      DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/configs/nginx/nginx_service.conf.in
    )
    add_custom_target(
      testsuite-nginx-config
      COMMENT "Generating nginx.conf for services"
      COMMAND ${TESTSUITE_PYTHON}
              ${GENNGINX_SCRIPT}
              substitute
              -o=${CMAKE_CURRENT_BINARY_DIR}/configs
              ${CMAKE_CURRENT_BINARY_DIR}/configs/nginx.conf.tpl
      DEPENDS testsuite-nginx-config-tpl
    )
  else()
    list(APPEND PYTEST_FLAGS "--no-nginx")
  endif()
  configure_file(scripts/runtests.in runtests @ONLY)
endif(TESTSUITE_PYTEST_DIRS)

configure_file(scripts/taxi-env.in taxi-env @ONLY)
configure_file(scripts/start-service.in start-service @ONLY)
