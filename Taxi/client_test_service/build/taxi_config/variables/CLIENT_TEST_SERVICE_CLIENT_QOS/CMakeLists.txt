project(yandex-taxi-config-variable-client_test_service_client_qos)

file(GLOB_RECURSE SOURCES
  ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/include/*.hpp
)

add_library(${PROJECT_NAME}_obj OBJECT ${SOURCES})

target_include_directories(
  ${PROJECT_NAME}_obj PUBLIC
  "${CMAKE_CURRENT_SOURCE_DIR}/include/"
)
target_link_libraries(${PROJECT_NAME}_obj
  PUBLIC
    yandex-userver-core
    yandex-taxi-library-codegen
)

add_library(${PROJECT_NAME} INTERFACE)
target_link_libraries(${PROJECT_NAME}
  INTERFACE
    ${PROJECT_NAME}_obj
    $<TARGET_OBJECTS:${PROJECT_NAME}_obj>
)
