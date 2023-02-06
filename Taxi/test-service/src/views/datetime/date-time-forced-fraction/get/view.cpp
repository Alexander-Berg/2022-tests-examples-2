#include "view.hpp"

#include <clients/test-service/client.hpp>

namespace handlers::datetime_date_time_forced_fraction::get {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  namespace client_ns =
      clients::test_service::datetime_date_time_forced_fraction::get;

  auto& client = dependencies.test_service_client;

  auto client_req = client_ns::Request{request.value};
  auto client_resp =
      client.DatetimeDateTimeForcedFraction(std::move(client_req));

  return Response200{client_resp.value};
}

}  // namespace handlers::datetime_date_time_forced_fraction::get
