#include "view.hpp"

#include <clients/test-service/client.hpp>

namespace handlers::response_with_headers_without_body::get {

Response View::Handle(Request&& /*request*/, Dependencies&& dependencies) {
  auto response =
      dependencies.test_service_client.ResponseWithHeadersWithoutBody();

  // For dynamic debug logs tests:
  LOG_TRACE() << "Got something for dynamic debug logging";

  return Response200{response.something};
}

}  // namespace handlers::response_with_headers_without_body::get
