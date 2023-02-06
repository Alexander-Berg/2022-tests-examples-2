#pragma once

#include <handlers/autogen/https/test/get/request.hpp>
#include <handlers/autogen/https/test/get/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::autogen_https_test::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::autogen_https_test::get
