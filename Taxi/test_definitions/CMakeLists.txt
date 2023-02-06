set(PROJECT "yandex-taxi-stq-client-definitions-test_definitions")
project(${PROJECT})

file(GLOB_RECURSE SOURCES
  ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/include/*.hpp
)

add_library(${PROJECT} STATIC ${SOURCES})

target_include_directories(
  ${PROJECT_NAME} PUBLIC
  "${CMAKE_CURRENT_SOURCE_DIR}/include/"
)
target_link_libraries(${PROJECT_NAME}
  PUBLIC
    yandex-userver-core
    yandex-taxi-library-codegen
    yandex-taxi-library-stq
)
