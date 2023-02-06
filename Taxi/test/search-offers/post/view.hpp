#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/test/search-offers/post/request.hpp>
#include <handlers/v1/test/search-offers/post/response.hpp>

namespace handlers::v1_test_search_offers::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_search_offers::post
