#include "view.hpp"

#include "utils/tests.hpp"

namespace handlers::internal_v1_tests_price::get {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  auto test_price = persey_labs::utils::GetTestPrice(
      request.id, request.lab_entity_id, request.locality_id, dependencies);

  if (!test_price) {
    return Response400({"TEST_NOT_FOUND", "Test id not found in config"});
  }

  return Response200(V1TestsPriceResponse{std::move(*test_price)});
}

}  // namespace handlers::internal_v1_tests_price::get
