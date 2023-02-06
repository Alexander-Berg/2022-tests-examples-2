#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/testing/test/get/request.hpp>
#include <handlers/v1/testing/test/get/response.hpp>

namespace handlers::v1_testing_test::get {

class View {
 public:
  static Response Handle(const Request& request,
                         const Dependencies& dependencies);
};

}  // namespace handlers::v1_testing_test::get
