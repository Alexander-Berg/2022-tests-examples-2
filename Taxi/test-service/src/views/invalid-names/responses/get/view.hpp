#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/invalid-names/responses/get/request.hpp>
#include <handlers/invalid-names/responses/get/response.hpp>

namespace handlers::invalid_names_responses::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::invalid_names_responses::get
