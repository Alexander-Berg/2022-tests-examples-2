#include "view.hpp"

#include <views/postgres/test_data.hpp>

namespace handlers::v1_test_data_read::post {

namespace {

// entry_point_data format is:
//{
//  "timeseries": {
//    "values": [...],
//    "timestamps": [...],
//    "type": "..."
//  },
//  "entry_point_id": "..."
//}
handlers::NamedTimeSeries ToHandlers(
    const formats::json::Value& entry_point_data) {
  handlers::NamedTimeSeries result;
  result.name = entry_point_data["entry_point_id"].As<std::string>();
  const auto& timeseries = entry_point_data["timeseries"];
  result.timeseries.timestamps =
      timeseries["timestamps"].As<std::vector<std::int64_t>>();
  result.timeseries.values = timeseries["values"].As<std::vector<double>>();
  result.timeseries.type = "data";
  return result;
}

}  // namespace

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  auto taxi_config = dependencies.config.Get<taxi_config::TaxiConfig>();
  const auto& command_control =
      taxi_config.hejmdal_test_data_settings.read_db_command_control;
  hejmdal::views::postgres::TestData test_data_db(
      dependencies.pg_hejmdal->GetCluster());

  Response200 response;
  try {
    auto db_test_data = test_data_db.Get(
        request.id, hejmdal::views::postgres::GetControl(command_control));
    response.description = db_test_data.description;
    response.schema_id = db_test_data.schema_id.GetUnderlying();
    response.start_time = db_test_data.start_time;
    response.end_time = db_test_data.end_time;
    response.test_data.reserve(db_test_data.data.GetSize());
    for (auto it = db_test_data.data.begin(); it != db_test_data.data.end();
         ++it) {
      response.test_data.push_back(ToHandlers(*it));
    }
  } catch (hejmdal::except::NotFound) {
    return Response404{};
  } catch (std::exception& ex) {
    return Response400(ErrorResponse{"400", ex.what()});
  }

  return response;
}

}  // namespace handlers::v1_test_data_read::post
