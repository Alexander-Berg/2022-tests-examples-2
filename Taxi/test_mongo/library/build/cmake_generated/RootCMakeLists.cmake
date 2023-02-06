# AUTOGENERATED, DON'T CHANGE THIS FILE!

include(CTest)

message(STATUS "BUILD_TYPE: ${CMAKE_BUILD_TYPE}")

# Function for colored output of service name
function(service_found name)
  string(ASCII 27 Esc)
  set(ColourReset "${Esc}[m")
  set(Green "${Esc}[32m")

  message("Configuring service: ${Green}${name}${ColourReset}")
endfunction()

service_found("test-service")
add_subdirectory(${CMAKE_SOURCE_DIR}/services/test-service)

add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/api-over-db)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/basic-http-client)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/client-statistics)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/client-stq-agent)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/codegen)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/codegen-clients)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/db-adapter)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/driver-authproxy-backend)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/json-converters)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/market-spok-infra-deploy)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/market-spok-infra-monitoring)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/mongo-collections)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/mongo-lib)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/passenger-authorizer-backend)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/segmented-dict)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/set-rules-matcher)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/solomon-stats)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/stq)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/stq-dispatcher)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/tvm2)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/tvm2-http-client)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/user-agent-parser)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/yt-logger)
add_subdirectory(${CMAKE_SOURCE_DIR}/libraries/yt-replica-reader)
add_subdirectory(${CMAKE_SOURCE_DIR}/userver/mongo)


target_link_libraries(objects-all
      yandex-taxi-library-api-over-db_all_obj
      yandex-taxi-library-basic-http-client_all_obj
      yandex-taxi-library-client-statistics_all_obj
      yandex-taxi-library-client-stq-agent_all_obj
      yandex-taxi-library-codegen-clients_all_obj
      yandex-taxi-library-codegen_all_obj
      yandex-taxi-library-db-adapter_all_obj
      yandex-taxi-library-driver-authproxy-backend_all_obj
      yandex-taxi-library-json-converters_all_obj
      yandex-taxi-library-market-spok-infra-deploy_all_obj
      yandex-taxi-library-market-spok-infra-monitoring_all_obj
      yandex-taxi-library-mongo-collections_all_obj
      yandex-taxi-library-mongo-lib_all_obj
      yandex-taxi-library-passenger-authorizer-backend_all_obj
      yandex-taxi-library-segmented-dict_all_obj
      yandex-taxi-library-set-rules-matcher_all_obj
      yandex-taxi-library-solomon-stats_all_obj
      yandex-taxi-library-stq-dispatcher_all_obj
      yandex-taxi-library-stq_all_obj
      yandex-taxi-library-tvm2-http-client_all_obj
      yandex-taxi-library-tvm2_all_obj
      yandex-taxi-library-user-agent-parser_all_obj
      yandex-taxi-library-yt-logger_all_obj
      yandex-taxi-library-yt-replica-reader_all_obj
      yandex-taxi-test-service_all_obj
  )

# This should go last to have all testsuite dirs to be collected before
add_subdirectory(testsuite)

# Tests
add_subdirectory(util/swaggen/tests)

# Common third_party libraries for uservices
set(TAXI_THIRD_PARTY_USERVICES_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/third_party)