#include "view.hpp"

#include <helpers/db_rules.hpp>

#include <userver/logging/log.hpp>

namespace handlers::v1_testing_test::get {

Response View::Handle(const Request& request,
                      const Dependencies& dependencies) {
  const auto& rule_name = request.rule_name;
  const auto& test_name = request.test_name;
  const auto& rule_id = request.rule_id;

  auto cluster = dependencies.pg_pricing_data_preparer->GetCluster();

  try {
    const auto& test =
        db::helpers::GetTestForRule(cluster, rule_name, test_name);

    if (!test) {
      return Response404(
          {libraries::pricing_components::NotFoundCode::kTestNotFound,
           "Test not found."});
    }

    RuleTestWithResultA1 test_result{};
    if (!rule_id.has_value()) {
      test_result.last_result = test->last_result;
    } else {
      test_result.last_result = rule_id.value() == test->last_result_rule_id
                                    ? test->last_result
                                    : std::nullopt;
    }

    const auto& res = Response200{
        RuleTestWithResult{libraries::pricing_extended::RuleTest{test.value()},
                           std::move(test_result)}};
    return res;

  } catch (const storages::postgres::Error& ex) {
    LOG_ERROR() << "Postgres error: " << ex.what();
    throw;
  }
}

}  // namespace handlers::v1_testing_test::get
