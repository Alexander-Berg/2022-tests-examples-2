#include "view.hpp"

#include <userver/server/handlers/exceptions.hpp>

#include <handlers/dependencies.hpp>

namespace handlers::sample_super_app::get {

Response View::Handle(Request&& /*request*/, Dependencies&& /*dependencies*/) {
  return Response200{};
}

Response View::HandleNonAuthorized(Request&& /*request*/,
                                   Dependencies&& /*dependencies*/) {
  throw server::handlers::Unauthorized(
      server::handlers::InternalMessage{"Not authorized by authproxy"});
}

}  // namespace handlers::sample_super_app::get
