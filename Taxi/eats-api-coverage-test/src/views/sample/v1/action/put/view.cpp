#include "view.hpp"

#include <fmt/format.h>

namespace handlers::sample_v1_action::put {

Response View::Handle(Request&&, Dependencies&&) {
  Response200 response;
  response.result = "OK";
  return response;
}

}  // namespace handlers::sample_v1_action::put
