#include "view.hpp"

#include <handlers/dependencies.hpp>

namespace handlers::json_echo::post {

Response View::Handle(Request&& /*request*/, Dependencies&& /*dependencies*/
) {
  Response200 response;
  return response;
}

}  // namespace handlers::json_echo::post
