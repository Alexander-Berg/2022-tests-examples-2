#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/serialize/flatbuf/echo/post/request.hpp>
#include <handlers/serialize/flatbuf/echo/post/response.hpp>

namespace handlers::serialize_flatbuf_echo::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::serialize_flatbuf_echo::post
