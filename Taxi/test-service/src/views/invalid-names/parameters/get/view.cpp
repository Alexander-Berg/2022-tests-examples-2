#include "view.hpp"

#include <clients/test-service/client.hpp>

namespace handlers::invalid_names_parameters::get {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  namespace client_ns = clients::test_service::invalid_names_parameters::get;

  auto& client = dependencies.test_service_client;

  client_ns::Request client_req;
  client_req.x1stinvalidparameter = request.x1stinvalidparameter;
  client_req.x2ndinvalidparameter = request.x2ndinvalidparameter;
  auto client_resp = client.InvalidNamesParameters(std::move(client_req));

  Response200 resp;
  resp.x1stinvalidparameter = client_resp.x1stinvalidparameter;
  resp.x2ndinvalidparameter = client_resp.x2ndinvalidparameter;
  return resp;
}

}  // namespace handlers::invalid_names_parameters::get
