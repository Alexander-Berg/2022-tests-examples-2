#include "view.hpp"

#include <userver/server/handlers/exceptions.hpp>

#include <handlers/dependencies.hpp>

#include <helpers/testing.hpp>

namespace handlers::internal_v1_test_cart_delivery_price_surge::get {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  const helpers::testing::TestProcessor test_processor(
      dependencies.redis_delivery_price, dependencies.config);
  auto test_results_opt = test_processor.GetTestResults(request.test_id);
  if (!test_results_opt) {
    return Response404();
  }
  auto& test_results = test_results_opt.value();
  Response200 response;
  response.status = test_results.status;
  response.errors = std::move(test_results.errors);
  for (auto& test_response : test_results.responses) {
    try {
      response.responses.push_back(
          test_response.As<handlers::CartDeliveryPriceSurgeResponse>());
    } catch (const std::exception& error) {
      LOG_ERROR() << "Failed to parse test response: " << error.what();
      response.errors.push_back(error.what());
    }
  }
  return response;
}

}  // namespace handlers::internal_v1_test_cart_delivery_price_surge::get
