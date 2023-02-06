#pragma once

#include <handlers/autogen/testpoint/callback/get/request.hpp>
#include <handlers/autogen/testpoint/callback/get/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::autogen_testpoint_callback::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::autogen_testpoint_callback::get
