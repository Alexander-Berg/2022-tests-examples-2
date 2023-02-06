#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/test/segments/full/get/request.hpp>
#include <handlers/v1/test/segments/full/get/response.hpp>

namespace handlers::v1_test_segments_full::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_segments_full::get
