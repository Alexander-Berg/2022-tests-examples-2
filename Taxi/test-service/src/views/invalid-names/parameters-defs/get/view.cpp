#include "view.hpp"

#include <clients/test-service/client.hpp>

namespace handlers::invalid_names_parameters_defs::get {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  namespace client_ns =
      clients::test_service::invalid_names_parameters_defs::get;

  auto& client = dependencies.test_service_client;

  client_ns::Request client_req;
  client_req.x1stinvalidparameter = request.x1stinvalidparameter;
  auto client_resp = client.InvalidNamesParametersDefs(std::move(client_req));

  Response200 resp;
  resp.x1stinvalidparameter = client_resp.x1stinvalidparameter;
  return resp;
}

}  // namespace handlers::invalid_names_parameters_defs::get
