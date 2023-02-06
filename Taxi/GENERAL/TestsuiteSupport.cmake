set(TESTSUITE_ROOT_DIR ${CMAKE_SOURCE_DIR}/submodules/testsuite)
set(TESTSUITE_PYTHON
  PYTHONPATH=${CMAKE_SOURCE_DIR}/submodules/pytest/src:${TESTSUITE_ROOT_DIR}:${CMAKE_SOURCE_DIR}/testsuite
  ${PYTHON}
)
set(TESTSUITE_GEN_FASTCGI
  ${TESTSUITE_PYTHON} ${CMAKE_SOURCE_DIR}/testsuite/scripts/genfastcgi.py)
set(TESTSUITE_GENSECDIST
  ${TESTSUITE_PYTHON} ${TESTSUITE_ROOT_DIR}/taxi_tests/utils/gensecdist.py)
set(TESTSUITE_CONFIGS_FALLBACK
  ${CMAKE_BINARY_DIR}/common/generated/fallback/configs.json)
set(COMMON_GENSECDIST
  ${TESTSUITE_PYTHON} ${CMAKE_SOURCE_DIR}/testsuite/scripts/common_gensecdist.py)
set(COMMON_SECDIST_PATH
  ${CMAKE_BINARY_DIR}/testsuite/configs/common-secdist.json)
unset(TESTSUITE_NGINX_SERVICES CACHE)
unset(TESTSUITE_PYTEST_DIRS CACHE)

add_custom_target(testsuite-fixtures ALL)

function(testsuite_generate_service_descriptor NAME BINARY CONFIG SOURCE_DIR
         SECDIST_DEV OUTPUT_SECDIST_PATH SECDIST_TEMPLATE)
  configure_file(
    ${CMAKE_SOURCE_DIR}/testsuite/scripts/service.in
    ${CMAKE_BINARY_DIR}/testsuite/services/${NAME}.service
    @ONLY)
endfunction()

add_custom_target(
  common-secdist
  COMMENT "Creating common secdist config"
  COMMAND mkdir -p ${CMAKE_BINARY_DIR}/testsuite/configs/
  COMMAND ${COMMON_GENSECDIST}
              --output ${COMMON_SECDIST_PATH}
              --source-dir ${CMAKE_SOURCE_DIR}
              --mongo-schema ${CMAKE_SOURCE_DIR}/schemas/mongo
  DEPENDS ${CMAKE_SOURCE_DIR}/testsuite/scripts/common_gensecdist.py
)
add_dependencies(testsuite-fixtures
  common-secdist)

function(add_testsuite_directory TESTSUITE_DIRECTORY)
  set(TESTSUITE_PYTEST_DIRS ${TESTSUITE_PYTEST_DIRS} ${TESTSUITE_DIRECTORY}
      CACHE STRING "Directories with all necessary tests." FORCE)
endfunction(add_testsuite_directory)

function(add_testsuite_fastcgi_fixture)
  set(options)
  set(oneValueArgs NAME MODULE_TARGET CONFIG CONFIG_TARGET MODULE_ALIAS CONFIG_PATH TESTS_PATH)
  set(multiValueArgs)
  cmake_parse_arguments(
    FIXTURE "${options}" "${oneValueArgs}" "${multiValueArgs}"  ${ARGN})

  if (FIXTURE_UNPARSED_ARGUMENTS)
    message(FATAL_ERROR
      "Unknown keywords given to add_testsuite_fastcgi_fixture(): "
      "${FIXTURE_UNPARSED_ARGUMENTS}")
    return()
  endif()

  if (NOT FIXTURE_NAME)
    message(FATAL_ERROR "No NAME given for fixture")
    return()
  endif()

  if (NOT FIXTURE_MODULE_TARGET)
    message(FATAL_ERROR "No MODULE_TARGET given for fixture")
    return()
  endif()

  if (NOT FIXTURE_CONFIG_TARGET)
    set(FIXTURE_CONFIG_TARGET "${FIXTURE_MODULE_TARGET}-make-config")
  endif()

  if (NOT FIXTURE_CONFIG_PATH)
    get_target_property(CONFIG_BINARY_DIR ${FIXTURE_CONFIG_TARGET} BINARY_DIR)
    set(FIXTURE_CONFIG_PATH "${CONFIG_BINARY_DIR}/conf")
  endif()

  set(CONFIG_PATH "${FIXTURE_CONFIG_PATH}/files/fastcgi.testsuite.conf")

  get_target_property(MODULE_BINARY_DIR ${FIXTURE_MODULE_TARGET} BINARY_DIR)
  set(MODULE_PATH "${MODULE_BINARY_DIR}/lib${FIXTURE_MODULE_TARGET}.so")

  if (NOT FIXTURE_MODULE_ALIAS)
    set(FIXTURE_MODULE_ALIAS "${FIXTURE_NAME}")
  endif()

  if(FIXTURE_TESTS_PATH)
    add_testsuite_directory(${FIXTURE_TESTS_PATH})
  endif(FIXTURE_TESTS_PATH)

  set(TESTSUITE_NGINX_SERVICES ${TESTSUITE_NGINX_SERVICES} ${FIXTURE_NAME}
          CACHE STRING "Target services for generation in nginx.conf" FORCE)
  set(SERVICE_SECDIST_PATH
    ${CMAKE_BINARY_DIR}/testsuite/configs/${PROJECT}-secdist.json)
  add_custom_target(
    testsuite-fixture-${FIXTURE_NAME}-config
    COMMENT "Creating testsuite config for ${FIXTURE_NAME}"
    COMMAND mkdir -p ${CMAKE_BINARY_DIR}/testsuite/configs
    COMMAND
      ${TESTSUITE_GEN_FASTCGI} --project="${FIXTURE_NAME}"
      --fastcgi-module="${MODULE_PATH}"
      --fastcgi-module-alias="${FIXTURE_MODULE_ALIAS}"
      --configs-fallback-path="${TESTSUITE_CONFIGS_FALLBACK}"
      --secdist-path="@@SERVICE_SECDIST_PATH@@"
      --build-path="${CMAKE_BINARY_DIR}/testsuite/"
      ${CONFIG_PATH}
      ${CMAKE_BINARY_DIR}/testsuite/configs/${FIXTURE_NAME}.conf
    DEPENDS
      yandex-taxi-common-configs-fallback-gen
      ${TESTSUITE_CONFIGS_FALLBACK}
      ${FIXTURE_CONFIG_TARGET}
      ${CMAKE_SOURCE_DIR}/testsuite/scripts/genfastcgi.py)
  add_dependencies(testsuite-fixtures testsuite-fixture-${FIXTURE_NAME}-config)

  set(SERVICE_DESCRIPTOR
    ${CMAKE_BINARY_DIR}/testsuite/services/${FIXTURE_NAME}.service)

  set(SERVICE_SECDIST_TEMPLATE
    ${CMAKE_CURRENT_SOURCE_DIR}/testsuite/secdist_template.json)
  if(EXISTS ${SERVICE_SECDIST_TEMPLATE})
    set(SECDIST_TEMPLATE ${SERVICE_SECDIST_TEMPLATE})
  else()
    set(SECDIST_TEMPLATE ${CMAKE_SOURCE_DIR}/testsuite/secdist_template.json)
  endif()
  testsuite_generate_service_descriptor(
    ${FIXTURE_NAME}
    ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT}
    ${CMAKE_BINARY_DIR}/testsuite/configs/${FIXTURE_NAME}.conf
    ${CMAKE_SOURCE_DIR}/testsuite
    ${CMAKE_SOURCE_DIR}/manual/secdist.json
    ${SERVICE_SECDIST_PATH}
    ${SECDIST_TEMPLATE})

   add_custom_target(
    service-secdist-${FIXTURE_NAME}
    COMMAND mkdir -p ${CMAKE_BINARY_DIR}/testsuite/configs
    COMMAND
      ${TESTSUITE_GENSECDIST} "${SERVICE_DESCRIPTOR}"
      --output="${SERVICE_SECDIST_PATH}"
      --mongo-schema="${CMAKE_SOURCE_DIR}/schemas/mongo"
    DEPENDS
      ${SERVICE_DESCRIPTOR}
      ${TESTSUITE_ROOT_DIR}/taxi_tests/utils/gensecdist.py)
   add_dependencies(testsuite-fixtures
    service-secdist-${FIXTURE_NAME})
endfunction()
