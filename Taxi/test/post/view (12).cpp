#include <views/superapp/test/post/view.hpp>

#include <clients/userver-sample/client.hpp>

namespace handlers::superapp_test::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  dependencies.userver_sample_client.SuperappTest({request.auth_context});

  return Response200();
}

Response View::HandleNonAuthorized(Request&& /*request*/,
                                   Dependencies&& /*dependencies*/) {
  throw Response403(Response403Code::kAccessDenied, "");
}

}  // namespace handlers::superapp_test::post
