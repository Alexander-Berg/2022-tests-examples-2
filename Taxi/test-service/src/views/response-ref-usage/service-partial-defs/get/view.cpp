#include "view.hpp"

#include <clients/test-service/client.hpp>

namespace handlers::response_ref_usage_service_partial_defs::get {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  namespace client_ns =
      clients::test_service::response_ref_usage_service_partial_defs::get;
  auto& client = dependencies.test_service_client;

  auto client_request = client_ns::Request{request.value};
  auto client_response =
      client.ResponseRefUsageServicePartialDefs(std::move(client_request));

  return Response200{{client_response.value}};
}

}  // namespace handlers::response_ref_usage_service_partial_defs::get
