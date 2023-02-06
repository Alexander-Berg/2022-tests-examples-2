#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/internal/v1/tests/get/request.hpp>
#include <handlers/internal/v1/tests/get/response.hpp>

namespace handlers::internal_v1_tests::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
  // Uncomment this declaration and implement the function in cpp file
  // to provide a custom formatter for Request body.
  // A custom formatter is required if the request contains sensitive or binary
  // data or it is too large to write to log.
  /*
  static std::string GetRequestBodyForLogging(
    const Request* request,
          const formats::json::Value* request_json,
        const std::string& request_body);
  */

  // Uncomment this declaration and implement the function in cpp file
  // to provide a custom formatter for Response data
  // A custom formatter is required if the response contains sensitive or binary
  // data or it is too large to write to log.
  /*
  static std::string GetResponseDataForLogging(
    const Response* response,
        const std::string& response_data);
  */
};

}  // namespace handlers::internal_v1_tests::get
