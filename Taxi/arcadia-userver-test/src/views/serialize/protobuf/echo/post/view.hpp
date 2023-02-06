#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/serialize/protobuf/echo/post/request.hpp>
#include <handlers/serialize/protobuf/echo/post/response.hpp>

namespace handlers::serialize_protobuf_echo::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::serialize_protobuf_echo::post
