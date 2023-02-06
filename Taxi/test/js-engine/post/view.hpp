#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/driver/v1/grocery-pro-bdu/v1/test/js-engine/post/request.hpp>
#include <handlers/driver/v1/grocery-pro-bdu/v1/test/js-engine/post/response.hpp>

namespace handlers::driver_v1_grocery_pro_bdu_v1_test_js_engine::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::driver_v1_grocery_pro_bdu_v1_test_js_engine::post
