#include "view.hpp"

#include <unordered_map>

#include <names/error_codes.hpp>
#include <radio/blocks/utils/sample_buffers.hpp>
#include <radio/detail/schemas/templatizer.hpp>
#include <radio/selectors/solomon_time_series_selector.hpp>
#include <views/circuit_schema_debug/tools.hpp>
#include <views/utils/custom_check.hpp>

#include <userver/logging/log.hpp>

namespace handlers::v1_custom_checks_test::post {

namespace utils = hejmdal::views::utils;
namespace radio = hejmdal::radio;

namespace names {
static const std::string kMetric = "metric";
}  // namespace names

namespace {

radio::CircuitPtr CreateCircuit(const Dependencies& deps,
                                const std::string preset_id,
                                const formats::json::Value& params) {
  const auto schemas_cache = deps.extra.schemas;
  const auto schema_tpl =
      schemas_cache->GetRawSchema(hejmdal::models::CircuitSchemaId{preset_id});
  if (schema_tpl == nullptr) {
    throw hejmdal::except::NotFound("Preset with id '{}' is not found",
                                    preset_id);
  }
  auto schema_override = utils::BuildCustomCheckSchemaOverride(
      preset_id, params, schema_tpl->schema);
  auto final_schema = radio::detail::schemas::ApplyTemplate(schema_override,
                                                            schema_tpl->schema);
  return radio::Circuit::Build("id", final_schema);
}

utils::GroupByLabelVals ExtractAndValidateGroupByLabelVals(
    const Dependencies& dependencies,
    const handlers::TestCustomCheckRequest& request) {
  utils::GroupByLabelVals group_by_label_vals;

  radio::selectors::RequestContainer container;
  auto selectors = utils::GetSelectors(request.flows.extra);
  const auto range = hejmdal::time::TimeRange(request.from, request.to);

  for (auto&& [name, selector] : selectors) {
    selector->MakeRequest(range, container);
  }
  dependencies.extra.solomon_client->FetchSensorsData(
      container.GetSolomonRequests());

  utils::ExtractAndValidateCustomCheckTimeLines(
      request.group_by_labels.value_or(utils::GroupByLabels{}),
      group_by_label_vals, container.GetSolomonRequests());

  return group_by_label_vals;
}

radio::PreparedFlowGroup PrepareInputs(
    const handlers::TestCustomCheckRequest& request,
    const hejmdal::radio::CircuitPtr& circuit,
    radio::selectors::RequestContainer& container,
    const std::optional<std::string>& label = std::nullopt,
    const std::optional<std::string>& label_val = std::nullopt) {
  std::vector<radio::PreparedFlow> flows;

  auto selectors = utils::GetSelectors(request.flows.extra, label, label_val);
  const auto range = hejmdal::time::TimeRange(request.from, request.to);

  for (auto&& [name, selector] : selectors) {
    auto ts_getter = selector->MakeRequest(range, container);
    flows.push_back(radio::PreparedFlow{std::move(ts_getter),
                                        circuit->GetEntryPoint(name)});
  }

  return radio::PreparedFlowGroup{std::move(flows), nullptr, request.to};
}

std::vector<hejmdal::radio::blocks::DebugBufferPtr>
CreateCircuitAndTransmitData(
    const Dependencies& dependencies,
    const handlers::TestCustomCheckRequest& request,
    const taxi_config::hejmdal_circuits_tester_settings::
        HejmdalCircuitsTesterSettings& transmit_settings,
    const std::optional<std::string>& label = std::nullopt,
    const std::optional<std::string>& label_val = std::nullopt) {
  auto circuit =
      CreateCircuit(dependencies, request.preset_id, request.params.extra);
  auto buffers = circuit->CreateDebugBuffers(
      hejmdal::time::As<hejmdal::time::Seconds>(request.to - request.from)
          .count());

  radio::selectors::RequestContainer container;
  auto flow_group =
      PrepareInputs(request, circuit, container, label, label_val);

  dependencies.extra.solomon_client->FetchSensorsData(
      container.GetSolomonRequests());
  hejmdal::views::schema_debug::Transmit(
      flow_group, circuit, transmit_settings.transceiving_period_sec,
      transmit_settings.tick_period_sec);

  return buffers;
}

handlers::StatePointState ToHandlers(radio::blocks::State&& state) {
  switch (state.GetStateValue()) {
    case radio::blocks::State::kNoData:
      return handlers::StatePointState::kNodata;
    case radio::blocks::State::kOk:
      return handlers::StatePointState::kOk;
    case radio::blocks::State::kWarn:
      return handlers::StatePointState::kWarning;
    case radio::blocks::State::kError:
      return handlers::StatePointState::kError;
    case radio::blocks::State::kCritical:
      return handlers::StatePointState::kCritical;
  }
}

handlers::CircuitStatePoints ToHandlers(
    std::vector<hejmdal::radio::blocks::DebugBufferPtr>&& buffers) {
  handlers::CircuitStatePoints result;

  if (auto size = buffers.size(); size != 1) {
    LOG_WARNING() << "CustomChecks::Test: expected to have 1 debug buffer but "
                  << size << " are created";
    if (size == 0) {
      return result;
    }
  }

  for (auto& buf : buffers) {
    auto state_buffer =
        std::dynamic_pointer_cast<radio::blocks::StateBufferSample>(buf);
    if (state_buffer != nullptr) {
      LOG_DEBUG() << "CustomChecks::Test: extract state values from buffer "
                  << state_buffer->GetId();
      auto state_points = state_buffer->ExtractState();
      result.state_points.reserve(state_points.size());
      for (auto&& state_point : state_points) {
        auto state = state_point.GetValue();
        result.state_points.push_back(handlers::StatePoint{
            state_point.GetTime(), ToHandlers(state.GetStateValue()),
            state.GetDescription()});
      }
      return result;
    }
  }

  LOG_WARNING() << "CustomChecks::Test: unable to convert debug buffer to "
                   "StateBufferSample";
  return result;
}

}  // namespace

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  auto taxi_config = dependencies.config.Get<taxi_config::TaxiConfig>();
  const auto& transmit_settings =
      dependencies.config.Get<taxi_config::TaxiConfig>()
          .hejmdal_circuits_tester_settings;

  try {
    auto group_by_label_vals =
        ExtractAndValidateGroupByLabelVals(dependencies, request.body);

    if (group_by_label_vals.empty()) {
      auto buffers = CreateCircuitAndTransmitData(dependencies, request.body,
                                                  transmit_settings);
      return Response200{{{names::kMetric, ToHandlers(std::move(buffers))}}};
    }

    auto label = *request.body.group_by_labels->begin();
    std::unordered_map<std::string, handlers::CircuitStatePoints>
        circuit_buffers;

    for (const auto& label_val : group_by_label_vals) {
      auto buffers = CreateCircuitAndTransmitData(
          dependencies, request.body, transmit_settings, label, label_val);
      circuit_buffers.insert({label_val, ToHandlers(std::move(buffers))});
    }

    return Response200{std::move(circuit_buffers)};
  } catch (const std::exception& ex) {
    LOG_WARNING() << "CustomChecks::Test: " << ex.what();
    return Response400(
        {hejmdal::names::error_codes::kInvalidRequest, ex.what()});
  }
}

}  // namespace handlers::v1_custom_checks_test::post
