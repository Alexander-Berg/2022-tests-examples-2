#include "view.hpp"

#include <clients/test-service/client.hpp>

namespace handlers::invalid_names_schemas::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  namespace client_ns = clients::test_service::invalid_names_schemas::post;

  auto& client = dependencies.test_service_client;

  client_ns::Request client_req;
  client_req.body = clients::test_service::X1stInvalidSchema{
      clients::test_service::X2ndInvalidSchema{
          request.body.x1stinvalidproperty.value}};

  auto client_resp = client.InvalidNamesSchemas(std::move(client_req));

  return Response200{X1stInvalidSchema{
      X2ndInvalidSchema{client_resp.x1stinvalidproperty.value}}};
}

}  // namespace handlers::invalid_names_schemas::post
