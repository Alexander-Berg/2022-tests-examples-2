#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/response-ref-usage/service-partial-defs/get/request.hpp>
#include <handlers/response-ref-usage/service-partial-defs/get/response.hpp>

namespace handlers::response_ref_usage_service_partial_defs::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::response_ref_usage_service_partial_defs::get
