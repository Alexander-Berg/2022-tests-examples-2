#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/test/mapping/save-mappings/post/request.hpp>
#include <handlers/test/mapping/save-mappings/post/response.hpp>

namespace handlers::test_mapping_save_mappings::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::test_mapping_save_mappings::post
