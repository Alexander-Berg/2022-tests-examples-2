#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/v1/test/claim/search/post/request.hpp>
#include <handlers/v1/test/claim/search/post/response.hpp>

namespace handlers::v1_test_claim_search::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_claim_search::post
