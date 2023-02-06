#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/test-case/delete/del/request.hpp>
#include <handlers/v1/test-case/delete/del/response.hpp>

namespace handlers::v1_test_case_delete::del {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_case_delete::del
