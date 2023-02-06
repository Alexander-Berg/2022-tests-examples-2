#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/lz4/decompress/post/request.hpp>
#include <handlers/lz4/decompress/post/response.hpp>

namespace handlers::lz4_decompress::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);

  static std::string GetRequestBodyForLogging(const Request* request,
                                              const std::string& request_body);
};

}  // namespace handlers::lz4_decompress::post
