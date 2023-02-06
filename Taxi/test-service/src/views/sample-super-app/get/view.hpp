#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/sample-super-app/get/request.hpp>
#include <handlers/sample-super-app/get/response.hpp>

namespace handlers::sample_super_app::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);

  static Response HandleNonAuthorized(Request&& request,
                                      Dependencies&& dependencies);
};

}  // namespace handlers::sample_super_app::get
