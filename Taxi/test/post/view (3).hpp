#pragma once

#include <handlers/autogen/flatbuf/test/post/request.hpp>
#include <handlers/autogen/flatbuf/test/post/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::autogen_flatbuf_test::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);

  static std::string GetRequestBodyForLogging(const Request* request,
                                              const std::string& request_body);

  static std::string GetResponseDataForLogging(
      const Response* response, const std::string& response_data);
};

}  // namespace handlers::autogen_flatbuf_test::post
