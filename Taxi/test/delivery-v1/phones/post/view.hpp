#pragma once

#include <handlers/delivery/v1/userver-sample/v1/test/delivery-v1/phones/post/request.hpp>
#include <handlers/delivery/v1/userver-sample/v1/test/delivery-v1/phones/post/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers {
namespace delivery_v1_userver_sample_v1_test_delivery_v1_phones {
namespace post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);

  static Response HandleNonAuthorized(Request&& request,
                                      Dependencies&& dependencies);
};

}  // namespace post
}  // namespace delivery_v1_userver_sample_v1_test_delivery_v1_phones
}  // namespace handlers
