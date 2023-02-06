#include "view.hpp"

#include <models/postgres/test_case.hpp>
#include <views/circuit_schema_debug/tools.hpp>
#include <views/postgres/detail/control.hpp>
#include <views/postgres/test_cases.hpp>
#include <views/postgres/test_data.hpp>

#include <fmt/format.h>

namespace handlers::v1_test_case_update::put {

namespace models = hejmdal::models;
namespace schema_debug = hejmdal::views::schema_debug;
namespace views = hejmdal::views;

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  auto taxi_config = dependencies.config.Get<taxi_config::TaxiConfig>();
  const auto& read_command_control =
      taxi_config.hejmdal_test_cases_settings.read_db_command_control;
  hejmdal::views::postgres::TestCases test_cases_db(
      dependencies.pg_hejmdal->GetCluster());

  models::postgres::TestCase db_test_case;
  try {
    db_test_case = test_cases_db.Get(
        request.id, hejmdal::views::postgres::GetControl(read_command_control));
  } catch (hejmdal::except::NotFound) {
    return Response404{};
  } catch (std::exception& ex) {
    return Response400(ErrorResponse{"400", ex.what()});
  }
  auto test_case = schema_debug::ToModelsTestCase(
      request.body.description, request.body.schema_id,
      request.body.test_data_id, request.body.is_enabled,
      request.body.test_case_info);
  test_case.id = db_test_case.id;
  if (test_case == db_test_case) {
    return Response200{};
  }

  // Validate request
  try {
    if (db_test_case.schema_id != test_case.schema_id) {
      return Response400(ErrorResponse{
          "400",
          fmt::format("changing schema_id from '{}' to '{}' is forbidden",
                      db_test_case.schema_id, test_case.schema_id)});
    }
    const auto& schema_id = models::CircuitSchemaId{test_case.schema_id};
    const auto& all_schemas = dependencies.extra.schemas;
    schema_debug::ValidateSchemaId(schema_id, all_schemas);
    auto test_data = schema_debug::GetTestData(taxi_config, dependencies,
                                               test_case.test_data_id);
    schema_debug::ValidateTestCase(test_case, test_data, schema_id,
                                   all_schemas);
  } catch (const std::exception& ex) {
    return Response400(ErrorResponse{"400", ex.what()});
  }

  // Insert to database
  const auto& write_command_control =
      taxi_config.hejmdal_test_cases_settings.write_db_command_control;
  try {
    test_cases_db.Update(request.id, std::move(test_case),
                         views::postgres::GetControl(write_command_control));
  } catch (const std::exception& ex) {
    throw hejmdal::except::Error(
        ex, "database error: could not process TestCases::Update request");
  }
  return Response200{};
}

}  // namespace handlers::v1_test_case_update::put
