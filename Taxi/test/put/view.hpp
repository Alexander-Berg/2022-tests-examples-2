#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/testing/test/put/request.hpp>
#include <handlers/v1/testing/test/put/response.hpp>

namespace handlers::v1_testing_test::put {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_testing_test::put
