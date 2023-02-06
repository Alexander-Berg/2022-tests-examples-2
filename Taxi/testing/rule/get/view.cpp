#include "view.hpp"

#include <psql/execute.hpp>
#include <psql/query/operators.hpp>
#include <psql/query/select.hpp>
#include <src/handlers/v1/settings/rules/get/request.hpp>

#include <pricing-extended/schemas/price_modifications.hpp>

#include <userver/logging/log.hpp>

namespace {
namespace pm = price_modifications;

const auto kRuleNameById = psql::Select(pm::rules.name)
                               .From(pm::rules)
                               .Where(pm::rules.rule_id == psql::_1);

const auto kRuleTests =
    psql::Select(pm::tests.test_name, pm::tests.last_result,
                 pm::tests.last_result_rule_id, pm::tests.last_visited_lines)
        .From(pm::tests)
        .Where(pm::tests.rule_name == psql::_1);
}  // namespace

namespace handlers::v1_testing_rule::get {

Response View::Handle(const Request& request,
                      const Dependencies& dependencies) {
  const auto& rule_name = request.rule_name;
  const auto& rule_id = request.rule_id;
  auto cluster = dependencies.pg_pricing_data_preparer->GetCluster();

  try {
    if (rule_id) {
      const auto& name = psql::Execute(cluster, kRuleNameById, rule_id.value());
      if (name.empty()) {
        return Response404(
            {libraries::pricing_components::NotFoundCode::kRuleNotFound,
             "Rule name with corresponding id not found."});
      }
      if (name.front() != rule_name) {
        return Response400(
            {libraries::pricing_components::BadRequestCode::kInvalidParameters,
             "Rule id doesn't match rule name."});
      }
    }
    const auto& rule_tests = psql::Execute(cluster, kRuleTests, rule_name);

    std::vector<handlers::RuleTestSummary> tests;
    for (const auto& test : rule_tests) {
      if (rule_id) {
        std::optional<bool> last_result{};
        std::optional<std::vector<int>> last_visited_lines{};
        if (rule_id.value() == test.last_result_rule_id) {
          last_result.emplace(test.last_result.value());
          last_visited_lines = test.last_visited_lines;
        }
        tests.emplace_back(
            RuleTestSummary{test.test_name, last_result, last_visited_lines});
      } else {
        tests.emplace_back(RuleTestSummary{test.test_name, test.last_result,
                                           test.last_visited_lines});
      }
    }

    return Response200{std::move(tests)};
  } catch (const storages::postgres::Error& ex) {
    LOG_ERROR() << "Postgres error: " << ex.what();
    throw;
  }
}

}  // namespace handlers::v1_testing_rule::get
