#include "view.hpp"

#include <psql/execute.hpp>
#include <psql/query/delete.hpp>
#include <psql/query/operators.hpp>

#include <pricing-extended/schemas/price_modifications.hpp>

#include <userver/logging/log.hpp>

namespace {

namespace pm = price_modifications;

const auto kDeleteTest = psql::DeleteFrom(pm::tests)
                             .Where(pm::tests.rule_name == psql::_1 &&
                                    pm::tests.test_name == psql::_2)
                             .Returning(pm::tests.test_name);
}  // namespace

namespace handlers::v1_testing_test::del {

Response View::Handle(const Request& request,
                      const Dependencies& dependencies) {
  const auto& rule_name = request.rule_name;
  const auto& test_name = request.test_name;

  auto cluster = dependencies.pg_pricing_data_preparer->GetCluster();

  try {
    const auto& check =
        psql::Execute(cluster, kDeleteTest, rule_name, test_name);
    if (check.empty()) {
      return Response404{
          {libraries::pricing_components::NotFoundCode::kTestNotFound,
           "Test not found."}};
    }

    return Response200{};
  } catch (const storages::postgres::Error& ex) {
    LOG_ERROR() << "Postgres error: " << ex.what();
    throw;
  }
}

}  // namespace handlers::v1_testing_test::del
