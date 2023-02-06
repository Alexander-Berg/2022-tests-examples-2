#include "test_case_factory.hpp"

#include <models/postgres/test_case.hpp>
#include <radio/tester/has_alert_test_case.hpp>
#include <radio/tester/last_state_test_case.hpp>
#include <radio/tester/worst_state_test_case.hpp>

namespace hejmdal::radio::tester {

namespace {

using BuildTestCaseFunc = TestCasePtr (*)(int, std::string&&, time::TimeRange&&,
                                          formats::json::Value&&,
                                          OutPointAccess&&);

static std::map<std::string, BuildTestCaseFunc> kTypeToBuilder = [] {
  /// Add new test_cases types here
  std::initializer_list<std::pair<std::string, BuildTestCaseFunc>> init_list = {
      {kWorstStateTestCaseType, &TestCaseBase::Build<WorstStateTestCase>},
      {kLastStateTestCaseType, &TestCaseBase::Build<LastStateTestCase>},
      {kHasAlertTestCaseType, &TestCaseBase::Build<HasAlertTestCase>}};

  std::map<std::string, BuildTestCaseFunc> result;
  for (auto&& type_builder : init_list) {
    if (auto res = result.insert(type_builder); !res.second) {
      throw except::Error("TestCaseFactory: duplicated test_case type: {}",
                          type_builder.first);
    }
  }
  return result;
}();

BuildTestCaseFunc FindBuilderOrThrow(const std::string& type) {
  auto builder_iter = kTypeToBuilder.find(type);
  if (builder_iter == kTypeToBuilder.end()) {
    throw except::Error("TestCaseFactory: unknown check type: {}", type);
  }
  return builder_iter->second;
}

}  // namespace

TestCasePtr TestCaseFactory::Build(CircuitPtr circuit,
                                   models::postgres::TestCase pg_test_case) {
  auto builder = FindBuilderOrThrow(pg_test_case.check_type);
  return builder(pg_test_case.id, std::move(pg_test_case.description),
                 time::TimeRange(std::move(pg_test_case.start_time),
                                 std::move(pg_test_case.end_time)),
                 std::move(pg_test_case.check_params),
                 circuit->GetOutPoint(pg_test_case.out_point_id));
}

}  // namespace hejmdal::radio::tester
