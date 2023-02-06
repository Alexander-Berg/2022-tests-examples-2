#include "circuit_tester.hpp"

#include <models/time_series.hpp>
#include <radio/selectors/time_series_selector.hpp>
#include <radio/tester/test_case_factory.hpp>
#include <radio/time_series_flow.hpp>
#include <views/circuit_schema_debug/tools.hpp>

#include <fmt/format.h>

#include <set>

#include <userver/logging/log.hpp>

namespace hejmdal::radio::tester {

using TestDataToCasesMap = std::map<int, std::set<PgTestCases::iterator>>;

namespace details {

class JsonTimeSeriesGetter : public selectors::TimeSeriesGetter {
 public:
  explicit JsonTimeSeriesGetter(const formats::json::Value& json)
      : ts_(models::TimeSeriesView(models::TimeSeries::FromJson(json))) {}

  const models::TimeSeriesView& GetTimeSeries() const override { return ts_; }
  time::TimePoint GetReceivedAt() const override { return time::TimePoint{}; }

 private:
  models::TimeSeriesView ts_;
};

void CollectResults(std::vector<TestCasePtr>&& test_cases,
                    RunTestsResult& result) {
  for (auto& test_case : test_cases) {
    auto test_case_result = test_case->GetResult();
    if (!test_case_result.passed) {
      result.state = ResultStates::WithFailures;
    }
    result.test_case_results.push_back(std::move(test_case_result));
  }
}

PreparedFlowGroup PrepareInputs(radio::CircuitPtr circuit,
                                const DataIdToDataMap& data_id_to_data,
                                int data_id) {
  if (auto data = data_id_to_data.find(data_id);
      data != data_id_to_data.end()) {
    std::vector<hejmdal::radio::PreparedFlow> flows;

    for (auto it = data->second->begin(); it != data->second->end(); ++it) {
      auto entry_point_data = it->As<formats::json::Value>();
      if (!entry_point_data.HasMember("entry_point_id") ||
          !entry_point_data.HasMember("timeseries")) {
        throw except::Error(
            "Incorrect test data format. Members "
            "'entry_point_id' and 'timeseries' are expected");
      }
      auto ep_id = entry_point_data["entry_point_id"].As<::std::string>();
      try {
        auto ts_getter =
            std::make_unique<JsonTimeSeriesGetter>(std::move(entry_point_data));
        flows.push_back(hejmdal::radio::PreparedFlow{
            std::move(ts_getter), circuit->GetEntryPoint(ep_id)});
      } catch (std::exception& ex) {
        throw except::Error(ex, "Could not create flow for entry point {}",
                            ep_id);
      }
    }

    return PreparedFlowGroup{std::move(flows), nullptr, {}};
  } else {
    throw except::NotFound("data with id {} is not found in database", data_id);
  }
}

std::vector<TestCasePtr> BuildTestCases(
    const std::set<PgTestCases::iterator>& pg_test_cases,
    radio::CircuitPtr circuit) {
  std::vector<TestCasePtr> test_cases;
  test_cases.reserve(pg_test_cases.size());

  for (auto pg_test_case : pg_test_cases) {
    auto test_id = pg_test_case->id;
    try {
      test_cases.push_back(TestCaseFactory::Build(circuit, *pg_test_case));
    } catch (std::exception& ex) {
      throw except::Error(ex, "unable to build test case with id '{}'",
                          test_id);
    }
  }
  return test_cases;
}

void SetTestCaseResult(RunTestsResult& result, const PgTestCase& pg_test_case,
                       bool passed, bool ignored, std::string msg) {
  TestCaseResult res(pg_test_case.id, pg_test_case.check_type,
                     pg_test_case.description);
  res.passed = passed;
  res.ignored = ignored;
  res.error_message = std::move(msg);
  result.test_case_results.push_back(std::move(res));
}

}  // namespace details

CircuitTester::CircuitTester(models::CircuitSchemaId schema_id,
                             formats::json::Value schema,
                             time::Duration transceiving_period,
                             time::Duration tick_period,
                             TestDataProviderPtr test_data_provider)
    : schema_id_(std::move(schema_id)),
      schema_json_(std::move(schema)),
      transceiving_period_(std::move(transceiving_period)),
      tick_period_(std::move(tick_period)),
      test_data_provider_(test_data_provider) {}

RunTestsResult CircuitTester::RunTests(PgTestCases&& pg_test_cases,
                                       bool break_on_failure,
                                       bool run_disabled) const {
  CheckTestCases(pg_test_cases);

  RunTestsResult result;
  result.state = ResultStates::Success;
  try {
    // Initialize data_id->test_cases map
    std::set<int> data_ids;
    TestDataToCasesMap data_id_to_cases;
    for (auto it = pg_test_cases.begin(); it != pg_test_cases.end(); ++it) {
      if (!it->is_enabled && !run_disabled) {
        details::SetTestCaseResult(
            result, *it, false, true,
            fmt::format("test_case {} is disabled", it->id));
        continue;
      }
      data_ids.insert(it->test_data_id);
      data_id_to_cases[it->test_data_id].insert(it);
    }

    // Initialize data_id->test_data map
    auto data_id_to_data =
        test_data_provider_->CollectTestData(std::move(data_ids));

    // Run tests
    for (const auto& [data_id, pg_test_case_iters] : data_id_to_cases) {
      LOG_DEBUG() << "CircuitTester: start running "
                  << pg_test_case_iters.size()
                  << " test cases for test data with id " << data_id;
      try {
        // Build new circuit for each test data as clean circuit is needed
        auto circuit = Circuit::Build(schema_id_.GetUnderlying(), schema_json_);

        auto inputs = details::PrepareInputs(circuit, data_id_to_data, data_id);

        auto test_cases = details::BuildTestCases(pg_test_case_iters, circuit);

        views::schema_debug::Transmit(inputs, circuit, transceiving_period_,
                                      tick_period_);

        details::CollectResults(std::move(test_cases), result);
      } catch (std::exception& ex) {
        result.state = ResultStates::WithFailures;
        for (auto& pg_test_case : pg_test_case_iters) {
          details::SetTestCaseResult(result, *pg_test_case, false, false,
                                     ex.what());
        }
      }

      if (result.state >= ResultStates::WithFailures && break_on_failure) {
        break;
      }
    }
  } catch (std::exception& ex) {
    result.test_case_results.clear();
    result.state = ResultStates::Error;
    result.error =
        fmt::format("Failed: execution is stopped by error: {}", ex.what());
  }
  return result;
}

void CircuitTester::CheckTestCases(const PgTestCases& pg_test_cases) const {
  for (auto& test_case : pg_test_cases) {
    if (test_case.schema_id != schema_id_.GetUnderlying()) {
      throw except::Error(
          "test_case {} uses schema '{}' but tester uses schema '{}'",
          test_case.id, test_case.schema_id, schema_id_.GetUnderlying());
    }
  }
}

}  // namespace hejmdal::radio::tester
