#include "view.hpp"

#include <userver/server/handlers/exceptions.hpp>

namespace handlers::test_bank_authproxy::get {

Response View::Handle(Request&& request, Dependencies&& /*dependencies*/) {
  return Response200{request.auth_context.yandex_uid,
                     request.auth_context.ya_bank_phone_id,
                     request.auth_context.ya_bank_session_uuid,
                     request.auth_context.yandex_buid,
                     request.auth_context.ya_user_ticket,
                     request.auth_context.locale,
                     request.auth_context.app_vars.GetApplicationName(),
                     request.auth_context.app_vars.GetVarAppVer1(),
                     SerializeChannelType(request.auth_context.channel_type)};
}

Response View::HandleNonAuthorized(Request&& /*request*/,
                                   Dependencies&& /*dependencies*/) {
  throw server::handlers::Unauthorized(
      server::handlers::InternalMessage{"Not authorized by authproxy"});
}

}  // namespace handlers::test_bank_authproxy::get
