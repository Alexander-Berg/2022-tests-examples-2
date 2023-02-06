#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/js/pipeline/test/post/request.hpp>
#include <handlers/v1/js/pipeline/test/post/response.hpp>

namespace handlers::v1_js_pipeline_test::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_js_pipeline_test::post
