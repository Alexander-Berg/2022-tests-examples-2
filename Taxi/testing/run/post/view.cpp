#include <views/v1/testing/run/post/view.hpp>

#include <helpers/price_conversion_test_run.hpp>
#include <pricing-extended/helpers/definitions_converters.hpp>
#include <pricing-functions/helpers/adapted_io.hpp>
#include <pricing-functions/helpers/bv_optional_parse.hpp>
#include <pricing-functions/lang/backend_variables.hpp>
#include <pricing-functions/parser/parser.hpp>
#include <userver/crypto/base64.hpp>
#include <userver/formats/json/serialize_duration.hpp>
#include <userver/formats/parse/common_containers.hpp>

namespace handlers::v1_testing_run::post {

Response View::Handle(const Request& request, const Dependencies& deps) {
  Response200 response;
  response.test_result = true;
  response.test_error = std::nullopt;

  const auto& source_code = request.body.source_code;
  const auto& extra_return =
      request.body.extra_returns.value_or(std::vector<std::string>{});
  const auto& initial_price =
      helpers::FromGenerated(request.body.initial_price);
  response.output_price = request.body.initial_price;
  const auto& trip_details = helpers::FromGenerated(request.body.trip_details);
  lang::variables::BackendVariables backend_variables;
  try {
    backend_variables = formats::parse::ParseBackendVariablesOptional(
        request.body.backend_variables.extra);
  } catch (const std::exception& ex) {
    response.test_result = false;
    response.test_error =
        response.test_error.value_or("") +
        "Error while parsing backend_variables: " + std::string(ex.what());
    return response;
  }

  const auto& run_result = helpers::RunPriceConversion(
      initial_price, trip_details, backend_variables,
      lang::models::ListFeatures(request.body.price_calc_version.value_or("")),
      source_code, extra_return, deps.config);
  response.test_result = run_result.success;
  response.test_error = run_result.error_message;
  response.execution_statistic = run_result.execution_info;
  response.visited_lines = run_result.visited_lines;
  if (run_result.output) {
    response.metadata_map.extra = run_result.output->metadata;
    response.output_price = helpers::ToGenerated(run_result.output->price);
  }
  return response;
}

}  // namespace handlers::v1_testing_run::post
