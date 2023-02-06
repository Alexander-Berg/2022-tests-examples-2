#include "view.hpp"

#include <algorithm>

#include <fmt/format.h>

#include <userver/formats/json/value_builder.hpp>
#include <userver/logging/log.hpp>

#include <models/test_data.hpp>
#include <models/time_series_view.hpp>
#include <names/circuit_schema.hpp>
#include <radio/selectors/time_series_selector.hpp>
#include <radio/spec/specification.hpp>
#include <utils/except.hpp>
#include <views/circuit_schema_debug/tools.hpp>
#include <views/postgres/test_data.hpp>

namespace handlers::v1_test_data_save::post {

namespace schema_debug = hejmdal::views::schema_debug;
namespace views = hejmdal::views;

namespace meta {
constexpr auto kCircuitId = "circuit_id";
constexpr auto kAlertState = "alert_state";
constexpr auto kHowBadIsIt = "how_bad";
constexpr auto kReason = "reason";
constexpr auto kLogin = "login";
}  // namespace meta

namespace {

formats::json::Value MakeMeta(const Request& request) {
  formats::json::ValueBuilder builder;
  builder["created"] = hejmdal::time::Now();
  builder["source"] = "test-data/save";
  builder[meta::kCircuitId] = request.body.circuit_id;
  if (request.body.alert_state) {
    builder[meta::kAlertState] = request.body.alert_state.value();
  }
  if (request.body.how_bad_is_it) {
    builder[meta::kHowBadIsIt] = request.body.how_bad_is_it.value();
  }
  if (request.body.reason) {
    builder[meta::kReason] = request.body.reason.value();
  }
  if (request.x_yandex_login) {
    builder[meta::kLogin] = request.x_yandex_login.value();
  }
  return builder.ExtractValue();
}

}  // namespace

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  static const hejmdal::time::Minutes kDefaultHistoryDurationMin{3600};

  const auto& circuit_id = request.body.circuit_id;

  auto all_specs = dependencies.extra.tuner_data.running_specs_ptr->GetSpecs();
  auto it = all_specs.enabled.find(circuit_id);
  if (it == all_specs.enabled.end()) {
    LOG_WARNING() << "TestData::Save: could not find spec for circuit "
                  << circuit_id;
    return Response404{{"404", "circuit not found"}};
  }
  const auto& spec = it->second;
  const auto& json_schema = spec->GetSchema();

  // prepare range
  auto history_data_duration =
      hejmdal::models::GetHistoryDataDuration(json_schema)
          .value_or(kDefaultHistoryDurationMin);
  auto taxi_config = dependencies.config.Get<taxi_config::TaxiConfig>();

  auto precedent_time = request.body.precedent_time;

  // TODO fix after TAXICOMMON-1751
  auto duration_before = request.body.duration_before_min.value_or(
      taxi_config.hejmdal_test_data_saver.default_duration_before_min);
  auto duration_after = request.body.duration_after_min.value_or(
      taxi_config.hejmdal_test_data_saver.default_duration_after_min);

  hejmdal::time::TimeRange range(
      precedent_time - duration_before - history_data_duration,
      precedent_time + duration_after);

  LOG_INFO() << "TestData::Save: saving range " << range.GetStart() << " - "
             << range.GetEnd() << " for " << circuit_id;

  // prepare flows
  auto entry_point_to_ts =
      schema_debug::ReceiveInputData(range, spec->GetFlows(), dependencies);
  auto test_data = schema_debug::BuildTestData(
      fmt::format("Test data for circuit '{}'", circuit_id),
      spec->GetSchemaId(), entry_point_to_ts, MakeMeta(request));
  test_data.precedent_time = precedent_time;

  const auto& command_control =
      taxi_config.hejmdal_test_data_settings.write_db_command_control;
  views::postgres::TestData test_data_db(dependencies.pg_hejmdal->GetCluster());
  try {
    test_data_db.Create(std::move(test_data),
                        views::postgres::GetControl(command_control));
  } catch (const std::exception& ex) {
    throw hejmdal::except::Error(
        ex, "database error: could not process TestData::Create request");
  }

  return Response200{};
}

}  // namespace handlers::v1_test_data_save::post
