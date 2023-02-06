#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/testing/test/del/request.hpp>
#include <handlers/v1/testing/test/del/response.hpp>

namespace handlers::v1_testing_test::del {

class View {
 public:
  static Response Handle(const Request& request,
                         const Dependencies& dependencies);
};

}  // namespace handlers::v1_testing_test::del
