#include <views/autogen/logging/test/post/view.hpp>

#include <atomic>

#include <userver/utils/assert.hpp>

namespace handlers::autogen_logging_test::post {

namespace {
std::atomic<bool> get_request_body_for_logging_was_called{false};
std::atomic<bool> get_response_data_for_logging_was_called{false};

void Validate(bool condition, const char* message) {
  UINVARIANT(condition, message);
}
}  // namespace

Response View::Handle(Request&& request, Dependencies&& /*dependencies*/) {
  Validate(get_request_body_for_logging_was_called,
           "GetRequestBodyForLogging was not called");

  if (request.body.key == "VALIDATE_RESPONSE_LOGGER_WAS_CALLED") {
    Validate(get_response_data_for_logging_was_called,
             "GetResponseDataForLogging was not called");
  }

  request.body.key = {};
  return {};
}

std::string View::GetRequestBodyForLogging(
    const Request* request, const formats::json::Value* request_json,
    const std::string& request_body) {
  const auto npos = std::string::npos;

  // TESTING:
  get_request_body_for_logging_was_called = true;
  if (request_body.find("VALID_JSON_REQUEST") != npos) {
    Validate(request != nullptr, "'request' is nullptr");
    Validate(request_json != nullptr, "'request_json' is nullptr");

    Validate(!request->body.key.empty(), "'request' was moved out");
  } else if (request_body.find("JSON_REQUEST_SCHEMA_MISSMATCH") != npos) {
    Validate(
        request == nullptr,
        "'request' is not nullptr on a request that does not match schema");
    Validate(
        request_json != nullptr,
        "'request_json' is nullptr on a request that does not match schema");

    Validate(request_json->HasMember("other_key"),
             "'request_json' does not have 'other_key' on a request that does "
             "not match schema");

    Validate(
        (*request_json)["other_key"].As<std::string>() ==
            "JSON_REQUEST_SCHEMA_MISSMATCH and some string",
        "'request_json['other_key']' is not 'JSON_REQUEST_SCHEMA_MISSMATCH and "
        "some string' on a request that does "
        "not match schema");
  } else if (request_body.find("NOT_A_JSON_REQUEST") != npos) {
    Validate(request == nullptr,
             "'request' is not nullptr on a not JSON request");
    Validate(request_json == nullptr,
             "'request_json' is not nullptr on a not JSON request");
  } else if (request_body.find("VALIDATE_RESPONSE_LOGGER_WAS_CALLED") != npos) {
    // Do nothing
  }

  return "OK";
}

std::string View::GetResponseDataForLogging(const Response* response,
                                            const std::string& response_data) {
  // TESTING:
  Validate(get_request_body_for_logging_was_called,
           "GetRequestBodyForLogging was not called");
  get_response_data_for_logging_was_called = true;
  if (response) {
    Validate(!response_data.empty(),
             "We have 'response', but no 'response_data'");
  }

  return "OK";
}

}  // namespace handlers::autogen_logging_test::post
