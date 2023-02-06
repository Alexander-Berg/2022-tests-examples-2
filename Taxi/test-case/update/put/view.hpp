#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/test-case/update/put/request.hpp>
#include <handlers/v1/test-case/update/put/response.hpp>

namespace handlers::v1_test_case_update::put {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_case_update::put
