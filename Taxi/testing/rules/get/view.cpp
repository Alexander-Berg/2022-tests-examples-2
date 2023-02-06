#include "view.hpp"

#include <psql/execute.hpp>
#include <psql/query/operators.hpp>
#include <psql/query/select.hpp>
#include <src/handlers/v1/settings/rules/get/request.hpp>

#include <pricing-extended/schemas/price_modifications.hpp>

#include <userver/logging/log.hpp>

namespace {

namespace pm = price_modifications;

const auto kTests =
    psql::Select(pm::tests.rule_name, pm::tests.last_result_rule_id,
                 pm::tests.test_name)
        .From(pm::tests);

const auto kRules = psql::Select(pm::rules.rule_id,  //
                                 pm::rules.name)
                        .From(pm::rules)
                        .Where(pm::rules.deleted != std::true_type{});

}  // namespace

namespace handlers::v1_testing_rules::get {

Response View::Handle(const Request& /*request*/,
                      const Dependencies& dependencies) {
  auto cluster = dependencies.pg_pricing_data_preparer->GetCluster();

  try {
    Response200 response;

    const auto& rules = psql::Execute(cluster, kRules);
    for (const auto& rule : rules) {
      if (auto it = response.extra.find(rule.name); it == response.extra.end())
        response.extra.emplace(std::make_pair(
            rule.name, handlers::RuleWithTest{rule.rule_id, {}}));
      else if (it->second.rule_id < rule.rule_id)
        it->second.rule_id = rule.rule_id;
    }

    const auto& tests = psql::Execute(cluster, kTests);
    for (const auto& test : tests) {
      if (auto it = response.extra.find(test.rule_name);
          it != response.extra.end()) {
        if (!it->second.tests.has_value())
          it->second.tests = {test.test_name};
        else
          it->second.tests->emplace_back(test.test_name);
      } else {
        response.extra[test.rule_name] =
            handlers::RuleWithTest{std::nullopt, {{test.test_name}}};
      }
    }

    return response;
  } catch (const storages::postgres::Error& ex) {
    LOG_ERROR() << "Postgres error: " << ex.what();
    throw;
  }
}

}  // namespace handlers::v1_testing_rules::get
