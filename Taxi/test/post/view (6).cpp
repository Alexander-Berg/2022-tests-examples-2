#include <views/autogen/flatbuf/test/post/view.hpp>

#include <atomic>

#include <userver/utils/assert.hpp>

namespace handlers::autogen_flatbuf_test::post {

namespace {
std::atomic<int> request_logging_call_count{0};
std::atomic<int> response_logging_call_count{0};
}  // namespace

Response View::Handle(Request&& request, Dependencies&& /*dependencies*/) {
  if (request.fbs_body.return_error) {
    UASSERT_MSG(request_logging_call_count != 0, "Request was not logged");
    UASSERT_MSG(response_logging_call_count != 0, "Response was not logged");
    Response400 resp;
    resp.body.code = "CODE";
    resp.body.message = "MESSAGE";
    return resp;
  }

  Response200 response;

  response.body.sum = request.fbs_body.arg1 + request.fbs_body.arg2;
  response.body.echo = std::move(request.fbs_body.data);
  response.header_number = std::move(request.header_number);
  response.query_enum = ToString(request.query_enum);

  return response;
}

std::string View::GetRequestBodyForLogging(
    [[maybe_unused]] const Request* request,
    [[maybe_unused]] const std::string& request_body) {
  ++request_logging_call_count;

  UASSERT_MSG(!request_body.empty(),
              "In tests for this handle the request_body should not be empty");

  UASSERT_MSG(request != nullptr,
              "In tests for this handle the request should not be empty");

  UASSERT_MSG(
      request->fbs_body.data == "TEST_INPUT_1" ||
          request->fbs_body.data == "VERY_VERY_VERY_VERY_LONG_TEST_INPUT_2",
      "Unexpected input for the handle");

  return {};
}

std::string View::GetResponseDataForLogging(
    [[maybe_unused]] const Response* response,
    [[maybe_unused]] const std::string& response_data) {
  ++response_logging_call_count;

  UASSERT_MSG(!response_data.empty(),
              "In tests for this handle the response_data should not be empty");

  UASSERT_MSG(response != nullptr,
              "In tests for this handle the response should not be empty");

  return {};
}

}  // namespace handlers::autogen_flatbuf_test::post
