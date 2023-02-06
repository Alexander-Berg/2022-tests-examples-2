#include <views/admin/v1/test-kinds/get/view.hpp>

#include <taxi_config/taxi_config.hpp>
#include <userver/dynamic_config/snapshot.hpp>

namespace handlers::admin_v1_test_kinds::get {

Response View::Handle(Request&&, Dependencies&& dependencies) {
  Response200 response;

  for (const auto& [test_id, _] :
       dependencies.config.Get<taxi_config::TaxiConfig>()
           .persey_labs_tests.extra) {
    response.test_kinds.push_back({test_id});
  }

  return response;
}

}  // namespace handlers::admin_v1_test_kinds::get
