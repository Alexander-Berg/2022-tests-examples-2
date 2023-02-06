#include "view.hpp"

#include <views/circuit_schema_debug/tools.hpp>
#include <views/postgres/test_cases.hpp>
#include <views/postgres/test_data.hpp>

namespace handlers::v1_test_case_create::post {

namespace models = hejmdal::models;
namespace schema_debug = hejmdal::views::schema_debug;
namespace views = hejmdal::views;

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  // Validate request
  models::postgres::TestCase test_case;
  auto taxi_config = dependencies.config.Get<taxi_config::TaxiConfig>();
  try {
    const auto& schema_id = models::CircuitSchemaId{request.body.schema_id};
    const auto& all_schemas = dependencies.extra.schemas;
    schema_debug::ValidateSchemaId(schema_id, all_schemas);
    test_case = schema_debug::ToModelsTestCase(
        request.body.description, request.body.schema_id,
        request.body.test_data_id, request.body.is_enabled,
        request.body.test_case_info);
    auto test_data = schema_debug::GetTestData(taxi_config, dependencies,
                                               test_case.test_data_id);
    schema_debug::ValidateTestCase(test_case, test_data, schema_id,
                                   all_schemas);
  } catch (const std::exception& ex) {
    return Response400(ErrorResponse{"400", ex.what()});
  }

  // Insert to database
  Response200 response;
  const auto& command_control =
      taxi_config.hejmdal_test_cases_settings.write_db_command_control;
  views::postgres::TestCases test_cases_db(
      dependencies.pg_hejmdal->GetCluster());
  try {
    response.test_case_id = test_cases_db.Create(
        std::move(test_case), views::postgres::GetControl(command_control));
  } catch (const std::exception& ex) {
    throw hejmdal::except::Error(
        ex, "database error: could not process TestCases::Create request");
  }

  return response;
}

}  // namespace handlers::v1_test_case_create::post
