#include "view.hpp"

#include <clients/test-service/client.hpp>

namespace handlers::echo_no_body::get {

Response View::Handle(Request&& /*request*/, Dependencies&& dependencies) {
  dependencies.test_service_client.EchoNoBody();
  return Response200{};
}

}  // namespace handlers::echo_no_body::get
