#include "view.hpp"

#include <yt_pg/read.hpp>
#include <yt_pg/types.hpp>

namespace handlers::v1_test_cargo_order_features::post {

const std::string kHandleUrl = "/test/cargo-order/features";

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  const auto features = cargo_claims::yt_pg::GetCargoPhoenixOrderFeatures(
      dependencies, request.body.cargo_order_ids, kHandleUrl);
  Response200 response;

  response.features.reserve(features.size());

  std::transform(
      features.begin(), features.end(), std::back_inserter(response.features),
      [](const cargo_claims::yt_pg::CargoOrderFeatures& feature) {
        return Response200FeaturesA{feature.cargo_order_id, feature.claim_uuid,
                                    feature.features};
      });

  return response;
}

}  // namespace handlers::v1_test_cargo_order_features::post
