#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/invalid-names/responses-defs/get/request.hpp>
#include <handlers/invalid-names/responses-defs/get/response.hpp>

namespace handlers::invalid_names_responses_defs::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::invalid_names_responses_defs::get
