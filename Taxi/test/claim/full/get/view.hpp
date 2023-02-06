#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/v1/test/claim/full/get/request.hpp>
#include <handlers/v1/test/claim/full/get/response.hpp>

namespace handlers::v1_test_claim_full::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_claim_full::get
