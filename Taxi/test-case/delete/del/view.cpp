#include "view.hpp"

#include <views/postgres/test_cases.hpp>

namespace handlers::v1_test_case_delete::del {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  auto taxi_config = dependencies.config.Get<taxi_config::TaxiConfig>();
  const auto& command_control =
      taxi_config.hejmdal_test_cases_settings.write_db_command_control;
  hejmdal::views::postgres::TestCases test_cases_db(
      dependencies.pg_hejmdal->GetCluster());

  try {
    test_cases_db.Delete(request.id,
                         hejmdal::views::postgres::GetControl(command_control));
  } catch (const hejmdal::except::NotFound&) {
    return Response404{};
  } catch (const std::exception& ex) {
    return Response400(ErrorResponse{"400", ex.what()});
  }

  return Response200{};
}

}  // namespace handlers::v1_test_case_delete::del
