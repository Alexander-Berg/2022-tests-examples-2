#include "view.hpp"

#include <models/postgres/test_case.hpp>
#include <views/postgres/test_cases.hpp>

namespace handlers::v1_test_case_read::post {

namespace {

handlers::TestCaseInfo ModelsToHandlers(
    hejmdal::models::postgres::TestCase&& test_case) {
  handlers::TestCaseInfo result{
      std::move(test_case.out_point_id), std::move(test_case.start_time),
      std::move(test_case.end_time), std::move(test_case.check_type)};
  result.check_params.extra = std::move(test_case.check_params);
  return result;
}

}  // namespace

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  auto taxi_config = dependencies.config.Get<taxi_config::TaxiConfig>();
  const auto& command_control =
      taxi_config.hejmdal_test_cases_settings.read_db_command_control;
  hejmdal::views::postgres::TestCases test_cases_db(
      dependencies.pg_hejmdal->GetCluster());

  Response200 response;
  try {
    auto db_test_case = test_cases_db.Get(
        request.id, hejmdal::views::postgres::GetControl(command_control));
    response.description = db_test_case.description;
    response.schema_id = db_test_case.schema_id;
    response.test_data_id = db_test_case.test_data_id;
    response.is_enabled = db_test_case.is_enabled;
    response.test_case_info = ModelsToHandlers(std::move(db_test_case));
  } catch (hejmdal::except::NotFound) {
    return Response404{};
  } catch (std::exception& ex) {
    return Response400(ErrorResponse{"400", ex.what()});
  }

  return response;
}

}  // namespace handlers::v1_test_case_read::post
