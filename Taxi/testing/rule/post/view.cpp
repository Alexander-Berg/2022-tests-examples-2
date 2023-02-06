#include "view.hpp"

#include <helpers/db_rules.hpp>
#include <helpers/price_conversion_test_run.hpp>
#include <pricing-extended/schemas/price_modifications.hpp>
#include <psql/execute.hpp>
#include <psql/query/delete.hpp>
#include <psql/query/operators.hpp>
#include <psql/query/select.hpp>
#include <psql/query/update.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/formats/parse/common_containers.hpp>
#include <userver/logging/log.hpp>
#include <userver/testsuite/testpoint.hpp>

namespace {

namespace pm = price_modifications;
const auto kGetTests =
    psql::Select(pm::tests.test_name, pm::tests.backend_variables,
                 pm::tests.trip_details, pm::tests.initial_price,
                 pm::tests.output_price, pm::tests.output_meta)
        .From(pm::tests)
        .Where(pm::tests.rule_name == psql::_1);

template <typename Test>
handlers::libraries::pricing_extended::RuleTest GetTest(Test&& test) {
  return handlers::libraries::pricing_extended::RuleTest{
      std::forward<decltype(test.backend_variables)>(test.backend_variables),
      test.trip_details.template As<
          handlers::libraries::pricing_extended::TripDetailsExtended>(),
      test.initial_price.template As<
          handlers::libraries::pricing_components::CompositePrice>(),
      db::helpers::OptJsonToDefault<
          handlers::libraries::pricing_components::CompositePrice>(
          test.output_price),
      db::helpers::OptJsonToDefault<
          handlers::libraries::pricing_extended::CompilerMetadata>(
          test.output_meta)};
}

std::vector<handlers::RuleTestSummary> RunAllTests(
    const storages::postgres::ClusterPtr& cluster,
    const helpers::RuleData& rule,
    const std::unordered_map<std::string, models::RuleTestWithResult>& tests,
    const dynamic_config::Snapshot& config) {
  std::vector<handlers::RuleTestSummary> testResults;
  testResults.reserve(tests.size());
  for (const auto& [test_name, test] : tests) {
    try {
      if (const auto& error = helpers::ValidateTestData(test); !!error) {
        LOG_ERROR() << "Test data is not valid for test " << test_name
                    << " for rule " << rule.name
                    << ": Error: " << error->message << ". Skipping test";
        handlers::RuleTestSummary ruleTestSummary;
        ruleTestSummary.name = test_name;
        testResults.push_back(ruleTestSummary);
        continue;
      }
      const auto& run_result = helpers::RunPriceConversion(
          test, rule.source, rule.extra_return, config);
      const auto& [ok, error_message] = VerifyRunResults(
          run_result.output.value(), test.output_price, test.output_meta);
      const bool result = run_result.success && ok;
      if (error_message) {
        LOG_WARNING() << "Error test " << test_name << " for rule " << rule.name
                      << ": " << *error_message;
      }
      db::helpers::SaveTestResult(cluster, rule.name, test_name,
                                  {result, rule.id, run_result.visited_lines});
      handlers::RuleTestSummary ruleTestSummary;
      ruleTestSummary.name = test_name;
      ruleTestSummary.test_result = result;
      testResults.push_back(ruleTestSummary);
    } catch (const storages::postgres::Error& ex) {
      LOG_ERROR() << "Error processing async test applying: DB error "
                  << ex.what() << " at test " << test_name << " for rule "
                  << rule.name << ". Abort test task for rule";
      return {};
    } catch (const std::exception& ex) {
      LOG_ERROR() << "Error processing async test applying: unknown error "
                  << ex.what() << " at test " << test_name << " for rule "
                  << rule.name << ". Abort test task for rule";
      return {};
    }
  }
  return testResults;
}

void SetAllTestNottested(
    const storages::postgres::ClusterPtr& cluster, const std::string& rule_name,
    const std::unordered_map<std::string, models::RuleTestWithResult>& tests) {
  for (const auto& [test_name, _] : tests)
    db::helpers::SaveTestResult(cluster, rule_name, test_name, {});
}

}  // namespace

namespace handlers::v1_testing_rule::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  auto cluster = dependencies.pg_pricing_data_preparer->GetCluster();

  std::optional<helpers::RuleData> rule_opt;
  try {
    rule_opt.emplace(cluster, request.rule_name, request.rule_id,
                     request.body.source, dependencies.config,
                     dependencies.taxi_approvals_client,
                     dependencies.pricing_modifications_validator_client);
  } catch (const std::logic_error& er) {
    return Response400{
        {libraries::pricing_components::BadRequestCode::kInvalidParameters,
         er.what()}};
  } catch (const std::invalid_argument& er) {
    return Response404{
        {libraries::pricing_components::NotFoundCode::kRuleNotFound,
         er.what()}};
  }
  if (!rule_opt) {
    return Response400{
        {libraries::pricing_components::BadRequestCode::kInvalidParameters,
         "Can't fetch rule for unknown reason"}};
  }
  const auto& tests = db::helpers::GetTestsForRule(cluster, rule_opt->name);
  SetAllTestNottested(cluster, rule_opt->name, tests);
  const auto& rule = rule_opt.value();
  std::vector<handlers::RuleTestSummary> testResults =
      RunAllTests(cluster, rule, tests, dependencies.config);

  return Response200{std::move(testResults)};
}

}  // namespace handlers::v1_testing_rule::post
