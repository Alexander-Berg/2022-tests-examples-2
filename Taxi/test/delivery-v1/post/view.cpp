#include <views/delivery/v1/userver-sample/v1/test/delivery-v1/post/view.hpp>

namespace handlers::delivery_v1_userver_sample_v1_test_delivery_v1::post {

Response View::Handle(Request&& request, Dependencies&& /*dependencies*/) {
  const auto& auth_params = request.auth_params;
  return Response200{true,
                     ToString(auth_params.yandex_uid),
                     auth_params.user_ticket,
                     auth_params.is_registered,
                     auth_params.phone_id,
                     auth_params.user.ip};
}

Response View::HandleNonAuthorized(Request&& request,
                                   Dependencies&& /*dependencies*/) {
  const auto& auth_params = request.auth_params;
  return Response200{false,
                     ToString(auth_params.yandex_uid),
                     auth_params.user_ticket,
                     auth_params.is_registered,
                     auth_params.phone_id,
                     auth_params.user.ip};
}

}  // namespace handlers::delivery_v1_userver_sample_v1_test_delivery_v1::post
