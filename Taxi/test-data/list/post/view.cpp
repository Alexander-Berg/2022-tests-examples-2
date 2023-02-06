#include "view.hpp"

#include <views/postgres/test_data.hpp>

namespace handlers::v1_test_data_list::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  auto taxi_config = dependencies.config.Get<taxi_config::TaxiConfig>();
  hejmdal::views::postgres::TestData test_data_db(
      dependencies.pg_hejmdal->GetCluster());
  const auto& command_control =
      taxi_config.hejmdal_test_data_settings.read_db_command_control;

  Response200 response;
  std::vector<hejmdal::models::TestDataInfo> test_data_list;
  hejmdal::views::postgres::TestDataToCasesMap data_to_cases;
  try {
    test_data_list = test_data_db.List(
        request.schema_id,
        hejmdal::views::postgres::GetControl(command_control));
    data_to_cases = test_data_db.GetTestDataToCases(
        hejmdal::views::postgres::GetControl(command_control));
  } catch (const std::exception& ex) {
    throw hejmdal::except::Error(
        ex, "database error: could not process TestData::List request");
  }

  response.test_data_items.reserve(test_data_list.size());
  for (auto&& test_data : test_data_list) {
    handlers::TestDataListItem item;
    item.id = std::move(test_data.id);
    item.description = std::move(test_data.description);
    item.schema_id = std::move(test_data.schema_id.GetUnderlying());
    if (auto test_cases = data_to_cases.find(test_data.id);
        test_cases != data_to_cases.end()) {
      item.test_case_ids = std::move(test_cases->second);
    }
    response.test_data_items.push_back(std::move(item));
  }
  return response;
}

}  // namespace handlers::v1_test_data_list::post
