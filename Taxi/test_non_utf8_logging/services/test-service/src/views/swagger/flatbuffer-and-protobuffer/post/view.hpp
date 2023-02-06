#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/swagger/flatbuffer-and-protobuffer/post/request.hpp>
#include <handlers/swagger/flatbuffer-and-protobuffer/post/response.hpp>

namespace handlers::swagger_flatbuffer_and_protobuffer::post {

class View {
 public:
  static Response Handle(
      Request&& request, Dependencies&& dependencies
      // Remove, unless you have to pass data from Handle to *ForLogging :
      // , server::request::RequestContext& context
  );
  // Uncomment this declaration and implement the function in cpp file
  // to provide a custom formatter for Request body.
  // A custom formatter is required if the request contains sensitive or binary
  // data or it is too large to write to log.
  /*
  static std::string GetRequestBodyForLogging(
    const Request* request,
          // Uncomment if you really need DOM
      // (warning: it requires slower DOM parsing)
      // const formats::json::Value* request_json,
        const std::string& request_body);
  */

  // Uncomment these two declarations and implement the functions in cpp file
  // to provide a custom formatter for response data.
  //
  // A custom formatter is required if the response contains sensitive, or
  // binary data or it is too large to write to log.
  /*
  static std::string GetResponseForLogging(
      const Response& response, const std::string& serialized_response,
      ::server::request::RequestContext& context);
  static std::string GetNonSchemaResponseForLogging(
      const std::string& response, ::server::request::RequestContext& context);
  */
};

}  // namespace handlers::swagger_flatbuffer_and_protobuffer::post
