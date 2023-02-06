#pragma once

#include <endpoints/full/plugins/delivery_order_flow/plugin.hpp>

#include <clients/cargo-c2c/client.hpp>
#include <clients/cargo-c2c/client_mock_base.hpp>
#include <core/context/clients/clients_impl.hpp>
#include <experiments3/delivery_slow_courier_flow.hpp>
#include <tests/context/taxi_config_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include "tests/context_mock_test.hpp"

namespace routestats::plugins::delivery_order_flow {

using C2cRequest = clients::cargo_c2c::v1_delivery_estimate::post::Request;
using C2cResponse = clients::cargo_c2c::v1_delivery_estimate::post::Response;
using EstimateHandler = std::function<C2cResponse(const C2cRequest&)>;

class MockCargoC2cClient : public clients::cargo_c2c::ClientMockBase {
 public:
  MockCargoC2cClient(
      const std::optional<EstimateHandler>& handler = std::nullopt);

  void SetHandler(const EstimateHandler& handler);

  C2cResponse DeliveryEstimate(
      const C2cRequest& request,
      const clients::cargo_c2c::CommandControl&) const override;

  size_t GetTimesCalled() const;

 private:
  EstimateHandler handler_;
  std::atomic<size_t> times_called_ = 0;
};

formats::json::Value LoadJsonFromFile(const std::string& filename);

struct ContextOverrides {
  std::optional<handlers::RequestPayment> payment;
  std::optional<core::Configs3> experiments;
  std::optional<std::shared_ptr<test::TaxiConfigsMock>> config;
  std::optional<EstimateHandler> c2c_handler;
  std::optional<routestats::core::TariffUnavailable> tariff_unavailable;
  routestats::full::GetConfigsMappedData get_experiments_mapped_data =
      [](const experiments3::models::KwargsBuilderWithConsumer &
         /*kwargs*/) -> experiments3::models::ClientsCache::MappedData {
    auto result = experiments3::models::ClientsCache::MappedData{};
    return result;
  };
  std::optional<std::shared_ptr<core::Translator>> translator;
};

class PluginTest {
 public:
  PluginTest(const ContextOverrides& overrides = {});

  std::vector<core::ServiceLevel> RunDeliveryPlugin();

  size_t CargoC2cTimesCalled() const;

 private:
  std::shared_ptr<const ::routestats::plugins::top_level::Context>
  GetTopLevelContext();

  std::vector<core::ServiceLevel> GetServiceLevels();

  ContextOverrides overrides_;
  MockCargoC2cClient c2c_client_;
};

}  // namespace routestats::plugins::delivery_order_flow
