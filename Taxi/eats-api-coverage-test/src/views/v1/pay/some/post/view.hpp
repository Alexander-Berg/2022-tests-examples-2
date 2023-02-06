#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/v1/pay/some/post/request.hpp>
#include <handlers/v1/pay/some/post/response.hpp>

namespace handlers::v1_pay_some::post {

class View {
 public:
  static Response Handle(
      Request&& request, Dependencies&& dependencies
      // Remove, unless you have to pass data from Handle to *ForLogging :
      // , server::request::RequestContext& context
  );
};

}  // namespace handlers::v1_pay_some::post
