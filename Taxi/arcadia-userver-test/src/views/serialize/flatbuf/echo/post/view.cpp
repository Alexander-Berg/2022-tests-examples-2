#include "view.hpp"

namespace handlers::serialize_flatbuf_echo::post {

Response View::Handle(Request&& request, Dependencies&& /*dependencies*/
) {
  Response200 response;
  response.body.data = request.body.data;
  response.body.misc = std::move(request.body.misc);
  return response;
}

}  // namespace handlers::serialize_flatbuf_echo::post
