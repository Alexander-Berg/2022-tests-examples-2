#include "view.hpp"

#include <userver/server/handlers/exceptions.hpp>

#include <clients/userver-sample/client.hpp>

namespace handlers::eats_v1_test::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  dependencies.userver_sample_client.EatsV1Test({request.eats_auth_context});

  Response200 response;

  response.inner_session = request.eats_auth_context.inner_session;
  response.login_id = request.eats_auth_context.login_id;
  response.session_type = request.eats_auth_context.session_type;
  response.yandex_uid = request.eats_auth_context.yandex_uid;
  response.eats_session = request.eats_auth_context.eats_session;

  response.bound_sessions = request.eats_auth_context.bound_sessions;
  response.taxi_session = request.eats_auth_context.taxi_session;
  response.is_eats_session_domain =
      eats_authproxy_backend::SessionHasEatsDomain(
          request.eats_auth_context.taxi_session);
  response.is_taxi_session_domain =
      eats_authproxy_backend::SessionHasTaxiDomain(
          request.eats_auth_context.taxi_session);

  const auto& taxi_personal = request.eats_auth_context.taxi_personal;
  response.taxi_personal = {
      taxi_personal.phone_id,
      taxi_personal.email_id,
      taxi_personal.eats_id,
  };
  const auto& eats_personal = request.eats_auth_context.eats_personal;
  response.eats_personal = {
      eats_personal.user_id,    eats_personal.phone_id,
      eats_personal.email_id,   eats_personal.partner_user_id,
      eats_personal.eater_uuid,
  };

  const auto& flags = request.eats_auth_context.flags;
  if (flags.has_portal)
    response.flags.extra[http::kXYandexTaxiPassportFlagPortal] = true;
  if (flags.has_pdd) response.flags.extra["pdd"] = true;
  if (flags.has_phonish) response.flags.extra["phonish"] = true;
  if (flags.has_neophonish) response.flags.extra["neophonish"] = true;
  if (flags.has_lite) response.flags.extra["lite"] = true;
  if (flags.has_social) response.flags.extra["social"] = true;
  if (flags.has_ya_plus) response.flags.extra["ya-plus"] = true;
  if (flags.no_login) response.flags.extra["no-login"] = true;
  if (flags.phone_confirm_required)
    response.flags.extra["phone_confirmation_required"] = true;
  if (flags.has_plus_cashback) response.flags.extra["cashback-plus"] = true;

  response.locale = request.eats_auth_context.locale;
  for (auto it = request.eats_auth_context.app_vars.begin();
       it != request.eats_auth_context.app_vars.end(); it++)
    response.app_vars.extra[it->first] = it->second;
  response.remote_ip = request.eats_auth_context.remote_ip;

  response.device_id = request.eats_auth_context.device_id;
  response.raw_app_metrics_device_id =
      request.eats_auth_context.app_metrica_device_id;

  response.raw_app_var =
      eats_authproxy_backend::GetHeaderRawValue(http::kXRequestApplication,
                                                request.eats_auth_context)
          .value();
  if (!request.eats_auth_context.eats_session.empty()) {
    response.raw_eats_personal =
        eats_authproxy_backend::GetHeaderRawValue(http::eats::kEatsUser,
                                                  request.eats_auth_context)
            .value();
  }

  return response;
}

Response View::HandleNonAuthorized(Request&& /*request*/,
                                   Dependencies&& /*dependencies*/) {
  throw server::handlers::Unauthorized(
      server::handlers::InternalMessage{"Not authorized by authproxy"});
}

// clang-format off
} // namespace handlers::eats_v1_test::post
// clang-format on
