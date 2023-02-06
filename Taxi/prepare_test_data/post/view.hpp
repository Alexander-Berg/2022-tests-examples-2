#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/v1/internal/prepare_test_data/post/request.hpp>
#include <handlers/v1/internal/prepare_test_data/post/response.hpp>

namespace handlers::v1_internal_prepare_test_data::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_internal_prepare_test_data::post
