#include <views/autogen/protobuf/test/post/view.hpp>

#include <handlers/example.pb.h>  // making sure that local protos are available

namespace handlers::autogen_protobuf_test::post {

Response View::Handle(const Request& request,
                      const Dependencies& /*dependencies*/) {
  Response200 response;

  response.body.set_sum(request.body.first() + request.body.second());

  return response;
}

}  // namespace handlers::autogen_protobuf_test::post
