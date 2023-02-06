#include "view.hpp"

#include <clients/test-service/client.hpp>

namespace handlers::invalid_names_responses::get {

Response View::Handle(Request&& /*request*/, Dependencies&& dependencies) {
  namespace client_ns = clients::test_service::invalid_names_responses::get;

  auto& client = dependencies.test_service_client;

  auto client_resp = client.InvalidNamesResponses();

  Response200 resp;
  resp.x1stinvalidproperty =
      X2ndInvalidSchema{client_resp.x1stinvalidproperty.value};
  return resp;
}

}  // namespace handlers::invalid_names_responses::get
