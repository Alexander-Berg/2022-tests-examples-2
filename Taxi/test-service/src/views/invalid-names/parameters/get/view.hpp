#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/invalid-names/parameters/get/request.hpp>
#include <handlers/invalid-names/parameters/get/response.hpp>

namespace handlers::invalid_names_parameters::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::invalid_names_parameters::get
