#include "view.hpp"

#include <models/declarations.hpp>
#include <radio/tester/circuit_tester.hpp>
#include <utils/except.hpp>
#include <views/postgres/detail/control.hpp>
#include <views/postgres/test_cases.hpp>
#include <views/utils/pg_test_data_provider.hpp>

#include <set>

namespace handlers::v1_test_case_run::post {

namespace {

using ResultStates = hejmdal::radio::tester::ResultStates;
using CircuitTester = hejmdal::radio::tester::CircuitTester;
using TestCases = hejmdal::views::postgres::TestCases;
using PgTestCases = hejmdal::radio::tester::PgTestCases;

TestCaseResultState ParseState(ResultStates state) {
  switch (state) {
    case ResultStates::Success:
      return TestCaseResultState::kSuccess;
    case ResultStates::WithFailures:
      return TestCaseResultState::kWithfailures;
    case ResultStates::Error:
      return TestCaseResultState::kError;
  }
}

void CheckReceivedTestCases(const std::vector<int>& requested_ids,
                            const PgTestCases& pg_test_cases) {
  if (requested_ids.size() != pg_test_cases.size()) {
    std::set<int> received_ids;
    for (auto& pg_test_case : pg_test_cases) {
      received_ids.insert(pg_test_case.id);
    }
    for (auto& id : requested_ids) {
      if (received_ids.count(id) == 0) {
        throw hejmdal::except::NotFound(
            "test_case with id {} is not found in database", id);
      }
    }
  }
}

}  // namespace

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  Response200 response;

  // Specify test runner settings
  const auto& schema_id = request.body.schema_id;
  const auto schema_json = dependencies.extra.schemas->GetFinalJsonSchema(
      request.body.schema_json.extra);
  const bool break_on_failure = request.body.break_on_failure.value_or(false);
  const bool run_disabled = request.body.test_case_ids.has_value();
  const auto& cluster = dependencies.pg_hejmdal->GetCluster();
  const auto& tester_settings =
      dependencies.config.Get<taxi_config::TaxiConfig>()
          .hejmdal_circuits_tester_settings;
  const auto data_provider_ptr =
      std::make_shared<hejmdal::views::utils::PgTestDataProvider>(
          cluster, hejmdal::views::postgres::GetControl(
                       tester_settings.select_test_data_db_command_control));

  PgTestCases pg_test_cases;
  // Collect test cases
  try {
    if (auto& requested_ids = request.body.test_case_ids;
        requested_ids.has_value()) {
      pg_test_cases = TestCases(cluster).Get(
          requested_ids.value(),
          hejmdal::views::postgres::GetControl(
              tester_settings.select_test_cases_db_command_control));
      CheckReceivedTestCases(requested_ids.value(), pg_test_cases);
    } else {
      pg_test_cases = TestCases(cluster).GetForSchema(
          schema_id, hejmdal::views::postgres::GetControl(
                         tester_settings.select_test_cases_db_command_control));
    }
  } catch (hejmdal::except::NotFound& ex) {
    return Response404{
        {"404", std::string("requested test cases not found: ") + ex.what()}};
  } catch (hejmdal::except::Error& ex) {
    return Response400{
        {"400", std::string("wrong requested test cases: ") + ex.what()}};
  }

  // Run tests
  CircuitTester tester(hejmdal::models::CircuitSchemaId(schema_id), schema_json,
                       tester_settings.transceiving_period_sec,
                       tester_settings.tick_period_sec, data_provider_ptr);

  hejmdal::radio::tester::RunTestsResult result;
  try {
    result = tester.RunTests(std::move(pg_test_cases), break_on_failure,
                             run_disabled);
  } catch (hejmdal::except::Error& ex) {
    return Response400{{"400", ex.what()}};
  }

  // Parse results
  response.state = ParseState(result.state);
  response.test_case_results.reserve(result.test_case_results.size());
  for (auto& test_case_result : result.test_case_results) {
    response.test_case_results.push_back(handlers::TestCaseResult{
        test_case_result.test_case_id, test_case_result.check_type,
        test_case_result.passed, test_case_result.ignored,
        test_case_result.description,
        test_case_result.error_message.value_or("Success")});
  }
  response.error_message = result.error;
  return response;
}

}  // namespace handlers::v1_test_case_run::post
