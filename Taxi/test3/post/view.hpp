#pragma once

#include <handlers/autogen/logging/test3/post/request.hpp>
#include <handlers/autogen/logging/test3/post/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::autogen_logging_test3::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies,
                         server::request::RequestContext& context);

  static std::string GetResponseForLogging(
      const Response& response, const std::string& serialized_response,
      ::server::request::RequestContext& context);
  static std::string GetNonSchemaResponseForLogging(
      const std::string& response, ::server::request::RequestContext& context);
};

}  // namespace handlers::autogen_logging_test3::post
