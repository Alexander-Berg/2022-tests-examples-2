#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/test/save-offer/post/request.hpp>
#include <handlers/v1/test/save-offer/post/response.hpp>

namespace handlers::v1_test_save_offer::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_save_offer::post
