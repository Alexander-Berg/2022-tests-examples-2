#pragma once

#include <handlers/autogen/protobuf/test/post/request.hpp>
#include <handlers/autogen/protobuf/test/post/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::autogen_protobuf_test::post {

class View {
 public:
  static Response Handle(const Request& request,
                         const Dependencies& dependencies);
};

}  // namespace handlers::autogen_protobuf_test::post
