#include "view.hpp"

#include <userver/server/handlers/exceptions.hpp>

namespace handlers::eats_v1_test_superapp_to_eats_auth::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  clients::userver_sample::eats_v1_test_eats_auth_to_superapp::post::Request
      eats_request;
  eats_request.eats_auth_context = eats_authproxy_backend::ConvertContext(
      request.auth_context,
      eats_authproxy_backend::SuperappToEatsAdditionalHeaders{});
  dependencies.userver_sample_client.EatsV1TestEatsAuthToSuperapp(eats_request);

  return Response200();
}

Response View::HandleNonAuthorized(Request&& /*request*/,
                                   Dependencies&& /*dependencies*/) {
  return Response401();
}

}  // namespace handlers::eats_v1_test_superapp_to_eats_auth::post
