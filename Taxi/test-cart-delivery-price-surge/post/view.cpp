#include "view.hpp"

#include <userver/server/handlers/exceptions.hpp>
#include <userver/utils/uuid4.hpp>

#include <handlers/dependencies.hpp>
#include <stq/client/queues.hpp>

#include <helpers/auth.hpp>
#include <helpers/parser.hpp>
#include <helpers/testing.hpp>

namespace handlers::internal_v1_test_cart_delivery_price_surge::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  const auto place_info_optional =
      helpers::ParsePlaceInfo(request.body.payload.place_info);
  if (!place_info_optional.has_value()) {
    Response400 bad_request;
    bad_request.error = "Failed to parse request.body.place_info";
    return bad_request;
  }
  stq_clients::eda_delivery_price_test_cart_delivery_price_surge::Args args;
  args.requests_count = request.body.requests_count;
  args.payload.extra = Serialize(
      request.body.payload, formats::serialize::To<formats::json::Value>());
  args.headers.extra = auth::MakeHeadersMap(request.eats_auth_context);
  const auto test_id = utils::generators::GenerateUuid();
  const helpers::testing::TestProcessor test_processor(
      dependencies.redis_delivery_price, dependencies.config);
  test_processor.StartTest(test_id);
  dependencies.stq->eda_delivery_price_test_cart_delivery_price_surge.Call(
      test_id, args);
  Response200 response;
  response.test_id = test_id;
  return response;
}

Response View::HandleNonAuthorized(Request&& request,
                                   Dependencies&& dependencies) {
  LOG_INFO()
      << "unauthorized request to /internal/v1/test-cart-delivery-price-surge";
  return Handle(std::move(request), std::move(dependencies));
}

}  // namespace handlers::internal_v1_test_cart_delivery_price_surge::post
