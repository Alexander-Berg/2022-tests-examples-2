#include "view.hpp"

#include <radio/selectors/time_series_selector.hpp>
#include <radio/tester/test_case_factory.hpp>
#include <views/circuit_schema_debug/tools.hpp>

namespace handlers::v1_debug_run_test_case::post {

namespace models = hejmdal::models;
namespace schema_debug = hejmdal::views::schema_debug;
namespace views = hejmdal::views;
namespace tester = hejmdal::radio::tester;

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  auto config = dependencies.config.Get<taxi_config::TaxiConfig>();
  std::vector<handlers::NamedTimeSeries> timeseries;
  tester::TestCasePtr test_case_ptr;

  try {
    const auto& transmit_settings =
        dependencies.config.Get<taxi_config::TaxiConfig>()
            .hejmdal_circuits_tester_settings;
    auto circuit = schema_debug::CreateCircuit(request.body.schema.extra);
    auto [flows, requests] =
        schema_debug::PrepareInputs(request.body.test_data, circuit);
    auto buffer_size = schema_debug::CalcDebugBufferSize(
        requests, config.hejmdal_circuits_component_settings.tick_period);

    dependencies.extra.solomon_client->FetchSensorsData(
        requests.GetSolomonRequests());
    dependencies.extra.yasm_client->FetchSignalsData(
        requests.GetYasmRequests());

    auto buffers = circuit->CreateDebugBuffers(buffer_size);

    test_case_ptr =
        schema_debug::BuildTestCase(circuit, request.body.test_case);

    schema_debug::Transmit(flows, circuit,
                           transmit_settings.transceiving_period_sec,
                           transmit_settings.tick_period_sec);

    timeseries = schema_debug::CollectTimeSeriesFromBuffers(buffers);
  } catch (const std::exception& ex) {
    return Response400(ErrorResponse{"400", ex.what()});
  }

  Response200 response;
  auto test_case_result = test_case_ptr->GetResult();
  response.passed = test_case_result.passed;
  response.message = test_case_result.error_message;
  response.named_timeseries_list = std::move(timeseries);
  return response;
}

}  // namespace handlers::v1_debug_run_test_case::post
