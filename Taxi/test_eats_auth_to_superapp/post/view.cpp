#include "view.hpp"

namespace handlers::eats_v1_test_eats_auth_to_superapp::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  clients::userver_sample::eats_v1_test_superapp_to_eats_auth::post::Request
      superapp_request;
  superapp_request.superapp_auth_context =
      eats_authproxy_backend::ConvertContext(request.eats_auth_context);
  dependencies.userver_sample_client.EatsV1TestSuperappToEatsAuth(
      superapp_request);

  return Response200();
}

Response View::HandleNonAuthorized(Request&& /*request*/,
                                   Dependencies&& /*dependencies*/) {
  return Response401();
}

}  // namespace handlers::eats_v1_test_eats_auth_to_superapp::post
