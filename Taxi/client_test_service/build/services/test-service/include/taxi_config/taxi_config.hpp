/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

#pragma once

#include <userver/dynamic_config/snapshot.hpp>
#include <userver/dynamic_config/value.hpp>

#include <taxi_config/variables/CLIENT_TEST_SERVICE_CLIENT_QOS.hpp>

namespace taxi_config {

struct TaxiConfig final {
  explicit TaxiConfig(const dynamic_config::DocsMap& docs_map);

  ::dynamic_config::ValueDict<
      taxi_config::client_test_service_client_qos::QosInfo>
      client_test_service_client_qos;
};

}
