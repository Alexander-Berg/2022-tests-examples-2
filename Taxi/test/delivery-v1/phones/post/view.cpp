#include <views/delivery/v1/userver-sample/v1/test/delivery-v1/phones/post/view.hpp>

namespace handlers {
namespace delivery_v1_userver_sample_v1_test_delivery_v1_phones {
namespace post {

Response View::Handle(Request&& request, Dependencies&& /*dependencies*/) {
  const auto& auth_params = request.auth_params;

  using PhoneInfo =
      handlers::delivery_v1_userver_sample_v1_test_delivery_v1_phones::post::
          Response200UserphonesA;

  ::std::vector<PhoneInfo> phones;
  if (auth_params.phones_pd_info) {
    for (const auto& auth_phone : *auth_params.phones_pd_info) {
      ::std::optional<::std::chrono::system_clock::time_point> ts;
      if (auth_phone.confirmation_time) {
        ts = *auth_phone.confirmation_time;
      }
      phones.push_back(PhoneInfo{auth_phone.id, ts});
    }
  }
  return Response200{std::move(phones)};
}

Response View::HandleNonAuthorized(Request&& request,
                                   Dependencies&& dependencies) {
  return Handle(std::move(request), std::move(dependencies));
}

}  // namespace post
}  // namespace delivery_v1_userver_sample_v1_test_delivery_v1_phones
}  // namespace handlers
