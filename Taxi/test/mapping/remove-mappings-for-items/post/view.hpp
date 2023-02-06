#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/test/mapping/remove-mappings-for-items/post/request.hpp>
#include <handlers/test/mapping/remove-mappings-for-items/post/response.hpp>

namespace handlers::test_mapping_remove_mappings_for_items::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::test_mapping_remove_mappings_for_items::post
