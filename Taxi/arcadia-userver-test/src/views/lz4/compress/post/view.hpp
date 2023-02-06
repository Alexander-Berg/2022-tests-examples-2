#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/lz4/compress/post/request.hpp>
#include <handlers/lz4/compress/post/response.hpp>

namespace handlers::lz4_compress::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);

  static std::string GetResponseForLogging(
      const Response& response, const std::string& serialized_response,
      ::server::request::RequestContext& context);
  static std::string GetNonSchemaResponseForLogging(
      const std::string& response, ::server::request::RequestContext& context);
};

}  // namespace handlers::lz4_compress::post
