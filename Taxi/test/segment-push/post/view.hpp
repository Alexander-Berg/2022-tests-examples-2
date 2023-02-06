#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/test/segment-push/post/request.hpp>
#include <handlers/test/segment-push/post/response.hpp>

namespace handlers::test_segment_push::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::test_segment_push::post
