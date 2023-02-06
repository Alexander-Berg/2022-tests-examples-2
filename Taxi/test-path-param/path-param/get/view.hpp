#pragma once

#include <handlers/autogen/test-path-param/path-param/get/request.hpp>
#include <handlers/autogen/test-path-param/path-param/get/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::autogen_test_path_param_path_param::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::autogen_test_path_param_path_param::get
