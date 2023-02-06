#include "view.hpp"

#include <handlers/dependencies.hpp>

namespace handlers::eats_partners_v1_test::post {

Response View::Handle(Request&& request, Dependencies&& /*dependencies*/) {
  Response200 response;

  const auto& auth_context = request.eats_partners_auth_context;

  response.partner_id = auth_context.partner_id;
  response.partner_uid = auth_context.partner_uid;

  if (auth_context.partner_places.has_value()) {
    std::vector<int64_t> places(std::begin(auth_context.partner_places.value()),
                                std::end(auth_context.partner_places.value()));
    std::sort(std::begin(places), std::end(places));

    response.places = std::move(places);
  }

  response.country_code = auth_context.country_code;
  response.personal_email_id = auth_context.personal_email_id;

  response.partner_has_access_to_places =
      auth_context.CheckAccess(request.body.places_to_check);

  return response;
}

}  // namespace handlers::eats_partners_v1_test::post
