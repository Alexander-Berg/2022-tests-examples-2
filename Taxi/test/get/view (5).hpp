#pragma once

#include <handlers/autogen/mockserver/test/get/request.hpp>
#include <handlers/autogen/mockserver/test/get/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::autogen_mockserver_test::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::autogen_mockserver_test::get
