#include <views/internal/v1/tests/get/view.hpp>

#include "utils/tests.hpp"

namespace handlers::internal_v1_tests::get {

Response View::Handle(Request&& /*request*/, Dependencies&& dependencies) {
  Response200 response;
  response.tests = persey_labs::utils::GetTests(dependencies);
  return response;
}

}  // namespace handlers::internal_v1_tests::get
