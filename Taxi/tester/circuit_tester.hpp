#pragma once

#include <set>

#include <userver/formats/json.hpp>

#include <models/declarations.hpp>
#include <models/postgres/test_case.hpp>
#include <radio/tester/test_case_base.hpp>

namespace hejmdal::radio::tester {

using PgTestCase = models::postgres::TestCase;
using PgTestCases = std::vector<PgTestCase>;
using JsonValue = formats::json::Value;
using DataIdToDataMap = std::map<int, std::shared_ptr<JsonValue>>;

enum class ResultStates : int { Success = 0, WithFailures = 1, Error = 2 };

struct RunTestsResult {
  ResultStates state{};
  std::vector<TestCaseResult> test_case_results{};
  std::optional<std::string> error{};
};

class TestDataProvider {
 public:
  virtual DataIdToDataMap CollectTestData(std::set<int>&& test_data_ids) = 0;
};

using TestDataProviderPtr = std::shared_ptr<TestDataProvider>;

class CircuitTester {
 public:
  CircuitTester(models::CircuitSchemaId schema_id, JsonValue schema,
                time::Duration transceiving_period, time::Duration tick_period,
                TestDataProviderPtr test_data_provider);

  RunTestsResult RunTests(PgTestCases&& pg_test_cases, bool break_on_failure,
                          bool run_disabled) const;

 private:
  void CheckTestCases(const PgTestCases& pg_test_cases) const;

 private:
  const models::CircuitSchemaId schema_id_;
  const JsonValue schema_json_;
  const time::Duration transceiving_period_;
  const time::Duration tick_period_;
  TestDataProviderPtr test_data_provider_;
};

}  // namespace hejmdal::radio::tester
