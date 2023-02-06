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

const auto RuleNameById = psql::Select(pm::rules.name)
                              .From(pm::rules)
                              .Where(pm::rules.rule_id == psql::_1);

void RunAllTests(
    const storages::postgres::ClusterPtr& cluster,
    const helpers::RuleData& rule,
    const std::unordered_map<std::string, models::RuleTestWithResult>& tests,
    const dynamic_config::Snapshot& config) {
  for (const auto& [test_name, test] : tests) {
    try {
      if (const auto& error = helpers::ValidateTestData(test); !!error) {
        LOG_ERROR() << "Test data is not valid for test " << test_name
                    << " for rule " << rule.name
                    << ": Error: " << error->message << ". Skipping test";
        continue;
      }
      const auto& run_result = helpers::RunPriceConversion(
          test, rule.source, rule.extra_return, config);
      if (!run_result.output) continue;
      const auto& [ok, error_message] = VerifyRunResults(
          run_result.output.value(), test.output_price, test.output_meta);

      const bool result = run_result.success && ok;
      if (error_message) {
        LOG_WARNING() << "Error test " << test_name << " for rule " << rule.name
                      << ": " << *error_message;
      }
      db::helpers::SaveTestResult(cluster, rule.name, test_name,
                                  {result, rule.id, run_result.visited_lines});
    } catch (const storages::postgres::Error& ex) {
      LOG_ERROR() << "Error processing async test applying: DB error "
                  << ex.what() << " at test " << test_name << " for rule "
                  << rule.name << ". Abort test task for rule";
      return;
    } catch (const std::exception& ex) {
      LOG_ERROR() << "Error processing async test applying: unknown error "
                  << ex.what() << " at test " << test_name << " for rule "
                  << rule.name << ". Abort test task for rule";
      return;
    }
  }
}

void SetAllTestNottested(
    const storages::postgres::ClusterPtr& cluster, const std::string& rule_name,
    const std::unordered_map<std::string, models::RuleTestWithResult>& tests) {
  for (const auto& [test_name, _] : tests)
    db::helpers::SaveTestResult(cluster, rule_name, test_name, {});
}

}  // namespace

namespace handlers::v1_testing_rules::post {

void RunAllTestForAllRules(
    const dynamic_config::Snapshot& config,
    const std::shared_ptr<storages::postgres::Cluster> cluster,
    const std::vector<helpers::RuleData> rules,
    std::unordered_map<
        int64_t, std::unordered_map<std::string, models::RuleTestWithResult>>
        rulesTestsById) {
  TESTPOINT("before_testing", formats::json::Value{});
  for (const auto& rule : rules) {
    const auto& tests = rulesTestsById[rule.id];
    RunAllTests(cluster, rule, tests, config);
  }

  TESTPOINT("testing_finished", formats::json::Value{});
}

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  auto cluster = dependencies.pg_pricing_data_preparer->GetCluster();
  if (!request.body.rule_ids) {
    return Response400{
        {libraries::pricing_components::BadRequestCode::kInvalidParameters}};
  }
  const auto& rule_ids = request.body.rule_ids.value();
  if (rule_ids.empty()) {
    return Response400{
        {libraries::pricing_components::BadRequestCode::kInvalidParameters}};
  }
  std::vector<helpers::RuleData> rules;
  rules.reserve(rule_ids.size());
  std::unordered_map<
      int64_t, std::unordered_map<std::string, models::RuleTestWithResult>>
      rulesTestsById;

  for (const auto& rule_id : rule_ids) {
    try {
      rules.emplace_back(
          helpers::RuleData(cluster, rule_id, {/*source - must be from db*/}));
      const auto& rule = rules.back();
      rulesTestsById.insert(std::make_pair(
          rule_id, db::helpers::GetTestsForRule(cluster, rule.name)));
      const auto& tests = rulesTestsById[rule_id];
      SetAllTestNottested(cluster, rule.name, tests);
    } catch (const std::invalid_argument& er) {
      return Response404{
          {libraries::pricing_components::NotFoundCode::kRuleNotFound,
           er.what()}};
    } catch (const std::logic_error& er) {
      return Response400{
          {libraries::pricing_components::BadRequestCode::kInvalidParameters,
           er.what()}};
    }
  }

  dependencies.extra.detached_tasks_storage.AsyncDetach(
      "testing_rules",
      [config = dependencies.config, cluster, rules = std::move(rules),
       rulesTestsById = std::move(rulesTestsById)]() {
        RunAllTestForAllRules(config, cluster, rules, rulesTestsById);
      });

  return Response200{};
}
}  // namespace handlers::v1_testing_rules::post
