#include "view.hpp"

#include <views/postgres/test_cases.hpp>

namespace handlers::v1_test_case_list::post {

namespace postgres = hejmdal::models::postgres;

namespace {

handlers::TestCaseListItem ModelsToHandlers(postgres::TestCaseInfo&& info) {
  return handlers::TestCaseListItem{
      std::move(info.id), std::move(info.description),
      std::move(info.schema_id), std::move(info.check_type), info.is_enabled};
}

}  // namespace

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  auto taxi_config = dependencies.config.Get<taxi_config::TaxiConfig>();
  hejmdal::views::postgres::TestCases test_cases_db(
      dependencies.pg_hejmdal->GetCluster());
  const auto& command_control =
      taxi_config.hejmdal_test_cases_settings.read_db_command_control;

  Response200 response;
  std::vector<postgres::TestCaseInfo> test_cases_list;
  try {
    test_cases_list = test_cases_db.List(
        request.schema_id,
        hejmdal::views::postgres::GetControl(command_control));
  } catch (const std::exception& ex) {
    throw hejmdal::except::Error(
        ex, "database error: could not process TestCases::List request");
  }

  response.enabled.reserve(test_cases_list.size());
  response.disabled.reserve(test_cases_list.size());
  for (auto&& test_case : test_cases_list) {
    auto handlers_test_case = ModelsToHandlers(std::move(test_case));
    if (handlers_test_case.is_enabled) {
      response.enabled.push_back(std::move(handlers_test_case));
    } else {
      response.disabled.push_back(std::move(handlers_test_case));
    }
  }
  return response;
}

}  // namespace handlers::v1_test_case_list::post
