#include "view.hpp"

#include <clients/test-service/client.hpp>

namespace handlers::invalid_names_schemas_defs::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  namespace client_ns = clients::test_service::invalid_names_schemas_defs::post;

  auto& client = dependencies.test_service_client;

  client_ns::Request client_req;
  client_req.body = clients::test_service::X1stInvalidSchemaDef{
      clients::test_service::X2ndInvalidSchemaDef{
          request.body.x1stinvalidproperty.value}};

  auto client_resp = client.InvalidNamesSchemasDefs(std::move(client_req));

  return Response200{X1stInvalidSchemaDef{
      X2ndInvalidSchemaDef{client_resp.x1stinvalidproperty.value}}};
}

}  // namespace handlers::invalid_names_schemas_defs::post
