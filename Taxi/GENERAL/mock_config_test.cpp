#include <utest/routing/mock_config_test.hpp>

#include <testing/taxi_config.hpp>

#include <taxi_config/client-routing/taxi_config.hpp>

using namespace std::chrono_literals;

namespace clients::routing::utest {

dynamic_config::StorageMock CreateRouterConfig() {
  return CreateRouterConfig({
      RouterSelect{
          std::nullopt,           // service
          std::nullopt,           // target
          std::nullopt,           // type
          std::nullopt,           // ids
          {"router0", "router1"}  // routers
      },
  });
}

dynamic_config::StorageMock CreateRouterConfig(
    const std::vector<RouterSelect>& router_select) {
  return dynamic_config::MakeDefaultStorage({
      {taxi_config::ROUTER_FALLBACK_DISTANCE_CORRECTION, 1.0},
      {taxi_config::ROUTER_FALLBACK_SPEED, 25},
      {taxi_config::ROUTER_TIGRAPH_USERVICES_ENABLED, true},
      {taxi_config::ROUTER_MAPS_ENABLED, true},
      {taxi_config::ROUTER_PEDESTRIAN_MAPS_ENABLED, true},
      {taxi_config::ROUTER_BICYCLE_MAPS_ENABLED, true},
      {taxi_config::ROUTER_MASSTRANSIT_MAPS_ENABLED, true},
      {taxi_config::ROUTER_MATRIX_BATCH_SIZE, 0},
      {taxi_config::ROUTER_MATRIX_MAPS_ENABLED, true},
      {taxi_config::ROUTER_MAPBOX_ENABLED, true},
      {taxi_config::ROUTE_RETRIES, 2},
      {taxi_config::ROUTER_YAMAPS_TVM_QUOTAS_MAPPING, {}},
      {taxi_config::ROUTER_PEDESTRIAN_YAMAPS_TVM_QUOTAS_MAPPING, {}},
      {taxi_config::ROUTER_BICYCLE_YAMAPS_TVM_QUOTAS_MAPPING, {}},
      {taxi_config::ROUTER_MASSTRANSIT_YAMAPS_TVM_QUOTAS_MAPPING, {}},
      {taxi_config::ROUTER_MATRIX_YAMAPS_TVM_QUOTAS_MAPPING, {}},
      {taxi_config::ROUTER_SELECT, router_select},
      {taxi_config::ROUTE_TIMEOUTS, {{"__default__", 10ms}}},
  });
}

}  // namespace clients::routing::utest
