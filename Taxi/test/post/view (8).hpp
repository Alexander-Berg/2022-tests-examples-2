#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/eats-partners/v1/test/post/request.hpp>
#include <handlers/eats-partners/v1/test/post/response.hpp>

namespace handlers::eats_partners_v1_test::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::eats_partners_v1_test::post
