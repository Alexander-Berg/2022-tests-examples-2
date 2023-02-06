#include <userver/utest/utest.hpp>

// Clients

// autogen/non-json/response/post/Reponse400 is a wrapper for int
// autogen/types/post/Response400 is a strong typedef
// autogen/empty/post/Response400 is an in place schema object
#include <clients/userver-sample/responses.hpp>

// Handlers

// Reponse400 is a wrapper for int
#include <handlers/autogen/non-json/response/post/response.hpp>

// Response400 is an in place schema object
#include <handlers/autogen/empty/post/response.hpp>

// Response400 is a strong typedef
#include <handlers/autogen/types/post/response.hpp>

namespace {
template <class Exception>
[[noreturn]] void Throw() {
  throw Exception{};
}

template <class Response200>
void TestResponse200() {
  try {
    throw Response200{};
  } catch (const std::exception& e) {
    FAIL() << "Response200 was derived from std::exception: " << e.what();
  } catch (const Response200&) {
    // OK
  }
}
}  // namespace

TEST(CodegenResponses, ClientResponseWrapper) {
  namespace post = clients::userver_sample::autogen_non_json_response::post;

  EXPECT_THROW(Throw<post::Response400>(), post::Exception);
  EXPECT_THROW(Throw<post::Response400>(), clients::userver_sample::Exception);
  EXPECT_THROW(Throw<post::Response400>(), clients::codegen::Exception);
  EXPECT_THROW(Throw<post::Response400>(), std::exception);

  TestResponse200<post::Response200>();
}

TEST(CodegenResponses, ClientStrongTypedef) {
  namespace post = clients::userver_sample::autogen_types::post;

  EXPECT_THROW(Throw<post::Response400>(), post::Exception);
  EXPECT_THROW(Throw<post::Response400>(), clients::userver_sample::Exception);
  EXPECT_THROW(Throw<post::Response400>(), clients::codegen::Exception);
  EXPECT_THROW(Throw<post::Response400>(), std::exception);

  TestResponse200<post::Response200>();
}

TEST(CodegenResponses, ClientInPlaceSchema) {
  namespace post = clients::userver_sample::autogen_empty::post;

  EXPECT_THROW(Throw<post::Response400>(), post::Exception);
  EXPECT_THROW(Throw<post::Response400>(), clients::userver_sample::Exception);
  EXPECT_THROW(Throw<post::Response400>(), clients::codegen::Exception);
  EXPECT_THROW(Throw<post::Response400>(), std::exception);

  TestResponse200<post::Response200>();
}

TEST(CodegenResponses, HandlerResponseWrapper) {
  namespace post = handlers::autogen_non_json_response::post;

  EXPECT_THROW(Throw<post::Response400>(), std::exception);

  TestResponse200<post::Response200>();
}

TEST(CodegenResponses, HandlerInPlaceSchema) {
  namespace post = handlers::autogen_empty::post;

  EXPECT_THROW(Throw<post::Response400>(), std::exception);

  TestResponse200<post::Response200>();
}

TEST(CodegenResponses, HandlerStrongTypedef) {
  namespace post = handlers::autogen_types::post;

  constexpr char kTestMessage[] =
      "Long test message that describes an error code in a human readable "
      "manner.";

  EXPECT_THROW(Throw<post::Response400>(), handlers::ErrorBase);
  EXPECT_THROW(Throw<post::Response400>(), std::exception);

  try {
    throw post::Response400{{handlers::ErrorBaseCode::kOops, kTestMessage}};
  } catch (const post::Response400& e) {
    EXPECT_EQ(e.code, handlers::ErrorBaseCode::kOops);
    EXPECT_EQ(e.message, kTestMessage);
  }

  TestResponse200<post::Response200>();
}
