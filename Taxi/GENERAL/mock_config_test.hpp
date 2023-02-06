#pragma once

#include <userver/dynamic_config/storage_mock.hpp>

#include <taxi_config/variables/ROUTER_SELECT.hpp>

namespace clients::routing::utest {

using RouterSelect = taxi_config::router_select::Rule;

/// generate router config for tests
/// see *_test.cpp files for examples
dynamic_config::StorageMock CreateRouterConfig();

/// generate router config for tests with custom ROUTER_SELECT
/// see *_test.cpp files for examples
dynamic_config::StorageMock CreateRouterConfig(
    const std::vector<RouterSelect>& router_select);

}  // namespace clients::routing::utest
