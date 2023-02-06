#include "view.hpp"

#include <userver/server/handlers/exceptions.hpp>

namespace handlers::test_passport_authproxy::get {

Response View::Handle(Request&& request, Dependencies&& /*dependencies*/) {
  return Response200{request.x_yandex_uid};
}

Response View::HandleNonAuthorized(Request&& /*request*/,
                                   Dependencies&& /*dependencies*/) {
  throw server::handlers::Unauthorized(
      server::handlers::InternalMessage{"Not authorized by authproxy"});
}

}  // namespace handlers::test_passport_authproxy::get
