#include "common_test.hpp"

#include <fstream>

#include <boost/filesystem.hpp>

#include <testing/source_path.hpp>

namespace routestats::plugins::delivery_order_flow {

using namespace clients::cargo_c2c::v1_delivery_estimate::post;

MockCargoC2cClient::MockCargoC2cClient(
    const std::optional<EstimateHandler>& handler) {
  if (handler.has_value()) {
    handler_ = [&](const C2cRequest& request) -> C2cResponse {
      times_called_.fetch_add(1);
      return (*handler)(request);
    };
    return;
  }

  handler_ = [&](const C2cRequest& request) -> C2cResponse {
    times_called_.fetch_add(1);

    C2cResponse response;
    for (const auto& tariff : request.body.taxi_tariffs) {
      clients::cargo_c2c::TariffClassEstimatingResult estimation;
      estimation.taxi_tariff = tariff.taxi_tariff;
      estimation.type = "succeed";
      estimation.offer_id = "offer_id_1";
      estimation.price = "4747.4747";
      estimation.currency = "RUB";
      estimation.decision = clients::cargo_c2c::OfferDecision::kOrderAllowed;
      response.estimations.push_back((Response200EstimationsA)estimation);
    }
    return response;
  };
}

C2cResponse MockCargoC2cClient::DeliveryEstimate(
    const C2cRequest& request,
    const clients::cargo_c2c::CommandControl&) const {
  return handler_(request);
}

size_t MockCargoC2cClient::GetTimesCalled() const {
  return times_called_.load();
}

PluginTest::PluginTest(const ContextOverrides& overrides)
    : overrides_(overrides),
      c2c_client_(MockCargoC2cClient(overrides.c2c_handler)) {}

std::vector<core::ServiceLevel> PluginTest::RunDeliveryPlugin() {
  top_level::DeliveryOrderFlowPlugin plugin;

  const auto top_level_context = GetTopLevelContext();
  plugin.OnContextBuilt(top_level_context);

  auto service_levels = GetServiceLevels();

  const auto& extensions =
      plugin.ExtendServiceLevels(top_level_context, service_levels);

  test::ApplyExtensions(extensions, service_levels);
  return service_levels;
}

size_t PluginTest::CargoC2cTimesCalled() const {
  return c2c_client_.GetTimesCalled();
}

std::shared_ptr<const ::routestats::plugins::top_level::Context>
PluginTest::GetTopLevelContext() {
  auto context = test::full::GetDefaultContext();
  context.clients.cargo_c2c =
      core::MakeClient<clients::cargo_c2c::Client>(c2c_client_);

  handlers::SupportedPayload request_payload;
  std::set<std::string> request_classes;
  request_classes.insert("courier");
  request_classes.insert("express");
  request_payload.classes = request_classes;
  context.input.supported_options["order_flow_delivery"].payload =
      request_payload;

  context.input.original_request.payment = handlers::RequestPayment{"card"};

  std::vector<geometry::Position> route;
  route.push_back(geometry::Position{0.0 * geometry::lon, 0.0 * geometry::lat});
  route.push_back(geometry::Position{1.0 * geometry::lon, 1.0 * geometry::lat});
  context.input.original_request.route = route;

  if (overrides_.experiments.has_value()) {
    context.experiments.uservices_routestats_configs = *overrides_.experiments;
  }
  if (overrides_.config) {
    context.taxi_configs = *overrides_.config;
  }
  if (overrides_.payment) {
    context.input.original_request.payment = *overrides_.payment;
  }
  context.get_experiments_mapped_data = overrides_.get_experiments_mapped_data;
  context.get_configs_mapped_data = overrides_.get_experiments_mapped_data;
  if (overrides_.translator) {
    context.rendering.translator = *overrides_.translator;
  }

  return test::full::MakeTopLevelContext(context);
}

std::vector<core::ServiceLevel> PluginTest::GetServiceLevels() {
  core::EstimatedWaiting eta;
  eta.message = "3 мин";
  eta.seconds = 180;
  core::ServiceLevel level;
  level.eta = eta;
  level.description_parts.emplace();
  level.description_parts->value = "400.000";
  level.is_fixed_price = true;

  std::vector<core::ServiceLevel> response;
  level.class_ = "courier";
  if (overrides_.tariff_unavailable) {
    level.tariff_unavailable = overrides_.tariff_unavailable;
  }
  response.push_back(level);

  level.class_ = "express";
  if (overrides_.tariff_unavailable) {
    level.tariff_unavailable = overrides_.tariff_unavailable;
  }
  response.push_back(level);
  return response;
}

const boost::filesystem::path kTestFilePath(utils::CurrentSourcePath(
    "src/tests/endpoints/full/plugins/delivery_order_flow"));
const std::string kTestDataDir = kTestFilePath.string() + "/static";

formats::json::Value LoadJsonFromFile(const std::string& filename) {
  std::ifstream f(kTestDataDir + "/" + filename);
  if (!f.is_open()) {
    throw std::runtime_error("Couldn't open file");
  }
  return formats::json::FromString(std::string(
      std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>()));
}

}  // namespace routestats::plugins::delivery_order_flow
