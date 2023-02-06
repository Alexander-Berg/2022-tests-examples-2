#include "view.hpp"

#include <utils/time.hpp>
#include <views/circuit_schema_debug/tools.hpp>
#include <views/postgres/detail/control.hpp>
#include <views/postgres/test_data.hpp>

#include <fmt/format.h>

namespace handlers::v1_test_data_update::put {

namespace models = hejmdal::models;
namespace schema_debug = hejmdal::views::schema_debug;
namespace time = hejmdal::time;
namespace views = hejmdal::views;

namespace {

bool NeedUpdate(const models::TestData& db_test_data,
                const models::TestData& test_data) {
  return db_test_data.description != test_data.description ||
         db_test_data.data != test_data.data;
}

formats::json::Value UpdateMeta(formats::json::Value&& meta) {
  auto builder = formats::json::ValueBuilder(meta);
  builder["updated"].PushBack(time::Now());
  return builder.ExtractValue();
}

}  // namespace

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  auto taxi_config = dependencies.config.Get<taxi_config::TaxiConfig>();
  const auto& read_command_control =
      taxi_config.hejmdal_test_data_settings.read_db_command_control;
  hejmdal::views::postgres::TestData test_data_db(
      dependencies.pg_hejmdal->GetCluster());

  models::TestData db_test_data;
  try {
    db_test_data = test_data_db.Get(
        request.id, hejmdal::views::postgres::GetControl(read_command_control));
  } catch (hejmdal::except::NotFound) {
    return Response404{};
  } catch (std::exception& ex) {
    return Response400(ErrorResponse{"400", ex.what()});
  }

  // Validate request
  models::TestData test_data;
  try {
    const auto& schema_id = models::CircuitSchemaId{request.body.schema_id};
    if (db_test_data.schema_id != schema_id) {
      return Response400(ErrorResponse{
          "400",
          fmt::format("changing schema_id from '{}' to '{}' is forbidden",
                      db_test_data.schema_id, request.body.schema_id)});
    }
    const auto& all_schemas = dependencies.extra.schemas;
    schema_debug::ValidateEntryPointInputs(request.body.entry_point_inputs,
                                           schema_id, all_schemas);
    auto entry_point_to_ts = schema_debug::ReceiveInputData(
        request.body.entry_point_inputs, dependencies);
    test_data = schema_debug::BuildTestData(request.body.description, schema_id,
                                            entry_point_to_ts,
                                            formats::json::MakeObject());
    test_data.id = db_test_data.id;
  } catch (const std::exception& ex) {
    return Response400(ErrorResponse{"400", ex.what()});
  }

  // Insert to database if need
  Response200 response;
  response.test_data_id = request.id;
  response.start_time = test_data.start_time;
  response.end_time = test_data.end_time;

  if (NeedUpdate(db_test_data, test_data)) {
    const auto& write_command_control =
        taxi_config.hejmdal_test_data_settings.write_db_command_control;
    test_data.meta = UpdateMeta(std::move(db_test_data.meta));
    try {
      test_data_db.Update(request.id, std::move(test_data),
                          views::postgres::GetControl(write_command_control));
    } catch (const std::exception& ex) {
      throw hejmdal::except::Error(
          ex, "database error: could not process TestData::Update request");
    }
  }
  return response;
}

}  // namespace handlers::v1_test_data_update::put
