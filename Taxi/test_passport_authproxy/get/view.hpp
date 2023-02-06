#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/test_passport_authproxy/get/request.hpp>
#include <handlers/test_passport_authproxy/get/response.hpp>

namespace handlers::test_passport_authproxy::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);

  static Response HandleNonAuthorized(Request&& request,
                                      Dependencies&& dependencies);
};

}  // namespace handlers::test_passport_authproxy::get
