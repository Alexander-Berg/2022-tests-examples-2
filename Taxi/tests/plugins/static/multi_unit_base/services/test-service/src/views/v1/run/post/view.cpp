#include "view.hpp"

#include <handlers/dependencies.hpp>

namespace handlers::v1_run::post {

Response View::Handle(
    Request&& /*request*/, Dependencies&& /*dependencies*/
    // Remove, unless you have to pass data from Handle to *ForLogging :
    // , server::request::RequestContext& context
) {
  Response200 response;

  // TODO Add your code here

  return response;
}

// Uncomment this definition and implement the function to provide a custom
// formatter for Request body
/*
std::string View::GetRequestBodyForLogging(
  const Request* request,
      // const formats::json::Value* request_json,
    const std::string& request_body) {
  // TODO Add your code here
}
*/

// Uncomment this definition and implement the function to provide a custom
// formatter for Response data
/*
std::string View::GetResponseForLogging(
  const Response& response, const std::string& serialized_response,
  ::server::request::RequestContext& context) {
  // TODO Add your code here
}

std::string View::GetNonSchemaResponseForLogging(
  const std::string& response, ::server::request::RequestContext& context) {
  return response;  // You may change this!
}
*/

}  // namespace handlers::v1_run::post
