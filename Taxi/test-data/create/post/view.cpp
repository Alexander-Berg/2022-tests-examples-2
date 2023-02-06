#include "view.hpp"

#include <models/circuit_schema.hpp>
#include <models/test_data.hpp>
#include <utils/time.hpp>
#include <views/circuit_schema_debug/tools.hpp>
#include <views/postgres/detail/control.hpp>
#include <views/postgres/test_data.hpp>

namespace handlers::v1_test_data_create::post {

namespace models = hejmdal::models;
namespace schema_debug = hejmdal::views::schema_debug;
namespace time = hejmdal::time;
namespace views = hejmdal::views;

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  // Validate request
  models::TestData test_data;
  try {
    const auto& schema_id = models::CircuitSchemaId{request.body.schema_id};
    const auto& all_schemas = dependencies.extra.schemas;
    schema_debug::ValidateSchemaId(schema_id, all_schemas);
    schema_debug::ValidateEntryPointInputs(request.body.entry_point_inputs,
                                           schema_id, all_schemas);
    auto entry_point_to_ts = schema_debug::ReceiveInputData(
        request.body.entry_point_inputs, dependencies);
    test_data = schema_debug::BuildTestData(
        request.body.description, schema_id, entry_point_to_ts,
        formats::json::MakeObject("created", time::Now(), "source",
                                  "test-data/create"));
  } catch (const std::exception& ex) {
    return Response400(ErrorResponse{"400", ex.what()});
  }

  // Insert to database
  Response200 response;
  response.start_time = test_data.start_time;
  response.end_time = test_data.end_time;

  auto taxi_config = dependencies.config.Get<taxi_config::TaxiConfig>();
  const auto& command_control =
      taxi_config.hejmdal_test_data_settings.write_db_command_control;
  views::postgres::TestData test_data_db(dependencies.pg_hejmdal->GetCluster());
  try {
    auto result = test_data_db.Create(
        std::move(test_data), views::postgres::GetControl(command_control));
    response.test_data_id = result.id;
  } catch (const std::exception& ex) {
    throw hejmdal::except::Error(
        ex, "database error: could not process TestData::Create request");
  }
  return response;
}

}  // namespace handlers::v1_test_data_create::post
