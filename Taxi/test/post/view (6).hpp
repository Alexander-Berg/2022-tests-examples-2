#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/driver/v1/userver-sample/v1/test/post/request.hpp>
#include <handlers/driver/v1/userver-sample/v1/test/post/response.hpp>

namespace handlers::driver_v1_userver_sample_v1_test::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);

  static Response HandleNonAuthorized(Request&& request,
                                      Dependencies&& dependencies);
};

}  // namespace handlers::driver_v1_userver_sample_v1_test::post
