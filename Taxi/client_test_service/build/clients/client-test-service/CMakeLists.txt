set(PROJECT "yandex-taxi-client-client-test-service")
project(${PROJECT})

file(GLOB_RECURSE SOURCES
  ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/src/*.hpp
)

add_library(${PROJECT} STATIC ${SOURCES})

set(INCLUDE_DIRS
  "${CMAKE_CURRENT_SOURCE_DIR}/src/"
  "${CMAKE_CURRENT_SOURCE_DIR}/include/"
  ${CMAKE_BINARY_DIR}/schemas/fbs/
)
target_include_directories(${PROJECT_NAME} PUBLIC ${INCLUDE_DIRS})
target_link_libraries(${PROJECT_NAME}
  PUBLIC
    yandex-userver-core
    yandex-taxi-library-codegen-clients
    yandex-taxi-library-tvm2-http-client
  )
target_link_libraries(${PROJECT_NAME} PUBLIC yandex-taxi-config-variable-client_test_service_client_qos)
target_link_libraries(${PROJECT_NAME} PUBLIC yandex-taxi-library-client-statistics)
