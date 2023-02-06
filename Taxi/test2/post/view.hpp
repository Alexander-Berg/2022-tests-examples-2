#pragma once

#include <handlers/autogen/logging/test2/post/request.hpp>
#include <handlers/autogen/logging/test2/post/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::autogen_logging_test2::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);

  // Request is JSON object, but we use Request instead of DOM value
  static std::string GetRequestBodyForLogging(const Request* request,
                                              const std::string& request_body);

  static std::string GetResponseDataForLogging(
      const Response* response, const std::string& response_data);
};

}  // namespace handlers::autogen_logging_test2::post
