#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/test-data/delete/del/request.hpp>
#include <handlers/v1/test-data/delete/del/response.hpp>

namespace handlers::v1_test_data_delete::del {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_data_delete::del
