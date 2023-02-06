#include "view.hpp"

namespace handlers::autogen_logging_test2::post {

Response View::Handle(Request&&, Dependencies&&) {
  Response200 response;
  return response;
}

std::string View::GetRequestBodyForLogging(const Request* request,
                                           const std::string& request_body) {
  if (request) {
    return "<data key=" + request->body.key + ">";
  } else {
    return "<no data size=" + std::to_string(request_body.size()) + ">";
  }
}

std::string View::GetResponseDataForLogging(
    const Response* /*response*/, const std::string& /*response_data*/) {
  return "";
}

}  // namespace handlers::autogen_logging_test2::post
