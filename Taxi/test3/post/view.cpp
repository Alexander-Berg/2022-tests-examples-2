#include "view.hpp"

#include <atomic>

#include <userver/utils/assert.hpp>

namespace handlers::autogen_logging_test3::post {

namespace {

std::atomic<bool> get_response_data_for_logging_was_called{false};
const std::string kTestKey = "test_request_key";
const std::string kTestData{
    "Some huge data that surely does not fit into the strings SSO"};

void Validate(bool condition, const char* message) {
  if (!condition) {
    UASSERT_MSG(false, message);
    throw std::runtime_error(message);
  }
}
}  // namespace

Response View::Handle(Request&& request, Dependencies&&,
                      server::request::RequestContext& context) {
  if (request.body.key == "VALIDATE_RESPONSE_LOGGER_WAS_CALLED") {
    Validate(get_response_data_for_logging_was_called,
             "GetResponseDataForLogging was not called");
  }

  context.SetData<std::string>(kTestKey, kTestData);
  return {};
}

std::string View::GetResponseForLogging(
    const Response&, const std::string&,
    ::server::request::RequestContext& context) {
  get_response_data_for_logging_was_called = true;
  const auto* data = context.GetDataOptional<std::string>(kTestKey);
  Validate(data, "We have no data from context");
  Validate(*data == kTestData, "We have data from context, but it differs");

  return "GetResponseForLogging";
}

std::string View::GetNonSchemaResponseForLogging(
    const std::string&, ::server::request::RequestContext&) {
  return "GetNonSchemaResponseForLogging";
}

}  // namespace handlers::autogen_logging_test3::post
