#pragma once

#include <handlers/autogen/logging/test/post/request.hpp>
#include <handlers/autogen/logging/test/post/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::autogen_logging_test::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);

  static std::string GetRequestBodyForLogging(
      const Request* request, const formats::json::Value* request_json,
      const std::string& request_body);

  static std::string GetResponseDataForLogging(
      const Response* response, const std::string& response_data);
};

}  // namespace handlers::autogen_logging_test::post
