#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/v1/test/claim/cut/post/request.hpp>
#include <handlers/v1/test/claim/cut/post/response.hpp>

namespace handlers::v1_test_claim_cut::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_claim_cut::post
