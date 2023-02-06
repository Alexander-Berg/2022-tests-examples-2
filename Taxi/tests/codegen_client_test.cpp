#include <userver/utest/utest.hpp>

#include <userver/utest/http_client.hpp>
#include <userver/utest/http_server_mock.hpp>

#include <userver/compiler/demangle.hpp>
#include <userver/concurrent/variable.hpp>
#include <userver/engine/sleep.hpp>

#include <tvm2/utest/mock_client_context.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/http/content_type.hpp>

#include <clients/userver-sample/client.hpp>
#include <tests/client_with_mock.hpp>
#include <userver/http/common_headers.hpp>

#include <handlers/autogen/empty/post/request.hpp>

namespace {

// TODO: move to userver?
clients::http::Headers GetUserHeaders(const clients::http::Headers& headers) {
  clients::http::Headers result(headers);

  // Default headers set by userver HTTP server / base handler
  result.erase(http::headers::kXYaRequestId);
  result.erase(http::headers::kXYaTraceId);
  result.erase(http::headers::kXYaSpanId);
  result.erase(http::headers::kAccept);
  result.erase(http::headers::kAcceptEncoding);
  result.erase(http::headers::kContentLength);
  result.erase(http::headers::kHost);
  result.erase(http::headers::kUserAgent);
  result.erase(http::headers::kXYaTaxiClientTimeoutMs);

  return result;
}

template <class T>
void Throw() {
  throw T();
}

}  // namespace

UTEST(CodegenClient, Ctr) {
  int count = 0;
  utest::HttpServerMock mock(
      [&count](const utest::HttpServerMock::HttpRequest& request) {
        count++;
        EXPECT_EQ(clients::http::HttpMethod::kGet, request.method);
        EXPECT_EQ("/autogen/empty", request.path);
        EXPECT_EQ(0, request.query.size());
        EXPECT_EQ((clients::http::Headers{
                      {tvm2::http::kXYaServiceTicket, "SERVICE TICKET"}}),
                  GetUserHeaders(request.headers));
        EXPECT_EQ("", request.body);

        return utest::HttpServerMock::HttpResponse{
            200,
            {},
            "{}",
        };
      });

  ClientWithMock client(mock.GetBaseUrl());

  EXPECT_NO_THROW(client->AutogenEmptyGet());
  EXPECT_EQ(1, count);

  static_assert(!std::is_base_of_v<
                clients::codegen::ExceptionWithStatusCode,
                clients::userver_sample::autogen_empty::get::Response200>);
}

UTEST(CodegenClient, Required) {
  utest::HttpServerMock mock(
      [](const utest::HttpServerMock::HttpRequest& request) {
        EXPECT_EQ((clients::http::Headers{
                      {tvm2::http::kXYaServiceTicket, "SERVICE TICKET"},
                      {http::headers::kContentType,
                       http::content_type::kApplicationJson.ToString()}}),
                  GetUserHeaders(request.headers));

        EXPECT_EQ(handlers::autogen_empty::post::BodyVar{"val"},
                  formats::json::FromString(request.body)
                      .As<handlers::autogen_empty::post::BodyVar>());

        return utest::HttpServerMock::HttpResponse{
            200,
            {},
            "",
        };
      });

  // Do not use ClientImpl in production code!
  ClientWithMock client(mock.GetBaseUrl());

  try {
    client->AutogenEmptyPost({{"val"}});
    FAIL() << "no throw";
  } catch (const clients::codegen::ExceptionWithStatusCode& e) {
    EXPECT_EQ(e.GetStatusCode(), 200);
  } catch (const std::exception& e) {
    FAIL() << "thrown " << e.what() << ", " << compiler::GetTypeName(typeid(e));
  }
}

UTEST(CodegenClient, Tvm2) {
  int count = 0;
  utest::HttpServerMock mock(
      [&count](const utest::HttpServerMock::HttpRequest& request) {
        count++;

        auto headers = GetUserHeaders(request.headers);
        EXPECT_EQ("SERVICE TICKET", headers.at("X-Ya-Service-Ticket"));

        EXPECT_EQ(
            (std::unordered_map<std::string, std::string>{{"foo", "val"}}),
            request.query);

        return utest::HttpServerMock::HttpResponse{
            200,
            {},
            "{\"test_message\": \"1234\"}",
        };
      });

  // Do not use ClientImpl in production code!
  ClientWithMock client(mock.GetBaseUrl());

  auto response = client->AutogenTvmServicePost({std::string("val")});
  EXPECT_EQ(1, count);
  EXPECT_EQ("1234", response.test_message);
}

UTEST(CodegenClient, Tvm2Testing) {
  int count = 0;
  utest::HttpServerMock mock(
      [&count](const utest::HttpServerMock::HttpRequest& request) {
        count++;

        auto headers = GetUserHeaders(request.headers);
        EXPECT_EQ("SERVICE TICKET", headers.at("X-Ya-Service-Ticket"));

        EXPECT_EQ(
            (std::unordered_map<std::string, std::string>{{"foo", "val"}}),
            request.query);

        return utest::HttpServerMock::HttpResponse{
            200,
            {},
            "{\"test_message\": \"1234\"}",
        };
      });

  // Do not use ClientImpl in production code!
  ClientWithMock client(mock.GetBaseUrl());

  auto response = client->AutogenTvmServicePut(
      {std::string("val"),
       {formats::json::ValueBuilder(formats::json::Type::kObject)
            .ExtractValue()}});
  EXPECT_EQ(1, count);
  EXPECT_EQ("1234", response.test_message);
}

UTEST(CodegenClient, Tvm2UserTickets) {
  int count = 0;
  utest::HttpServerMock mock(
      [&count](const utest::HttpServerMock::HttpRequest& request) {
        count++;
        EXPECT_EQ("abba", request.headers.at("X-Ya-User-Ticket"));
        EXPECT_EQ("12", request.headers.at("X-Yandex-UID"));

        return utest::HttpServerMock::HttpResponse{
            200,
            {},
            "{\"test_value\": \"33\"}",
        };
      });

  // Do not use ClientImpl in production code!
  ClientWithMock client(mock.GetBaseUrl());

  auto response = client->AutogenTvmWithUserTicketAndScopes({
      {
          server::auth::UserId(12),
          server::auth::UserAuthInfo::Ticket("abba"),
          tvm2::models::BlackboxEnv::kTest,
          server::auth::UserProvider::kYandex,
      },
      std::string("baz"),
  });
  EXPECT_EQ(1, count);
  EXPECT_EQ("33", response.test_value);
}

UTEST(CodegenClient, NonJsonResponse200) {
  int count = 0;
  utest::HttpServerMock mock(
      [&count](const utest::HttpServerMock::HttpRequest& /*request*/) {
        count++;

        return utest::HttpServerMock::HttpResponse{
            200,
            {},
            "1234",
        };
      });

  // Do not use ClientImpl in production code!
  ClientWithMock client(mock.GetBaseUrl());

  auto response = client->AutogenNonJsonResponse({"val"});
  EXPECT_EQ(1, count);
  EXPECT_EQ("1234", response.body);
}

UTEST(CodegenClient, NonJsonResponse400) {
  namespace operation =
      clients::userver_sample::autogen_non_json_response::post;

  int count = 0;
  utest::HttpServerMock mock(
      [&count](const utest::HttpServerMock::HttpRequest& /*request*/) {
        count++;

        return utest::HttpServerMock::HttpResponse{
            400,
            {},
            "1234",
        };
      });

  // Do not use ClientImpl in production code!
  ClientWithMock client(mock.GetBaseUrl());

  try {
    auto response = client->AutogenNonJsonResponse({"val"});
    FAIL() << "Should have thrown";
  } catch (const operation::Response400& e) {
    EXPECT_EQ("1234", e.body);
    EXPECT_EQ(e.GetStatusCode(), 400);
  } catch (const std::exception& e) {
    FAIL() << "Wrong exception: " << e.what();
  }

  EXPECT_EQ(1, count);
}

UTEST(CodegenClient, NonJsonResponseUnknown) {
  namespace operation =
      clients::userver_sample::autogen_non_json_response::post;

  int count = 0;
  utest::HttpServerMock mock(
      [&count](const utest::HttpServerMock::HttpRequest& /*request*/) {
        count++;

        return utest::HttpServerMock::HttpResponse{
            410,
            {},
            "1234",
        };
      });

  // Do not use ClientImpl in production code!
  ClientWithMock client(mock.GetBaseUrl());

  try {
    auto response = client->AutogenNonJsonResponse({"val"});
    FAIL() << "Should have thrown";
  } catch (const operation::Response400& e) {
    FAIL() << "Wrong exception (400): " << e.what();
  } catch (const operation::ExceptionWithStatusCode& e) {
    EXPECT_EQ(e.GetStatusCode(), 410);
  } catch (const std::exception& e) {
    FAIL() << "Wrong std::exception: " << e.what() << ", "
           << compiler::GetTypeName(typeid(e));
  }

  EXPECT_EQ(1, count);
}

UTEST(CodegenClient, ResponseHeadersOk) {
  int count = 0;
  utest::HttpServerMock mock(
      [&count](const utest::HttpServerMock::HttpRequest&) {
        count++;

        return utest::HttpServerMock::HttpResponse{
            200,
            clients::http::Headers{
                {"enum", "value1"},
                {"int", "444"},
                {"string", "smth"},
                {"array", "1,2,3"},
            },
            "{}",
        };
      });

  // Do not use ClientImpl in production code!
  ClientWithMock client(mock.GetBaseUrl());

  auto response = client->AutogenComplexResponseHeaders();
  EXPECT_EQ(1, count);
  EXPECT_EQ(clients::userver_sample::autogen_complex_response_headers::get::
                Enum::kValue1,
            response.enum_);
  EXPECT_EQ(444, response.int_);
  EXPECT_EQ("smth", response.string);
  EXPECT_EQ((std::vector<int>{1, 2, 3}), response.array);
}

UTEST(CodegenClient, ResponseHeadersDefaultSwagger20) {
  int count = 0;
  utest::HttpServerMock mock(
      [&count](const utest::HttpServerMock::HttpRequest&) {
        count++;

        return utest::HttpServerMock::HttpResponse{
            200,
            clients::http::Headers{
                {"enum", "value1"},
                {"array", "1,2,3"},
            },
            "{}",
        };
      });

  // Do not use ClientImpl in production code!
  ClientWithMock client(mock.GetBaseUrl());

  namespace operation =
      clients::userver_sample::autogen_complex_response_headers::get;

  // param "default" is forbidden in swagger response headers
  EXPECT_THROW(client->AutogenComplexResponseHeaders(), operation::Exception);
}

UTEST(CodegenClient, ResponseHeadersDefaultOpenapi30) {
  int count = 0;
  utest::HttpServerMock mock(
      [&count](const utest::HttpServerMock::HttpRequest&) {
        count++;

        return utest::HttpServerMock::HttpResponse{
            200,
            clients::http::Headers{
                {"enum", "value1"},
            },
            "{}",
        };
      });

  // Do not use ClientImpl in production code!
  ClientWithMock client(mock.GetBaseUrl());

  namespace operation =
      clients::userver_sample::autogen_complex_response_headers::get;

  auto response = client->AutogenComplexResponseHeadersOpenapi30();
  EXPECT_EQ(1, count);
  EXPECT_EQ(42, response.int_);
  EXPECT_EQ(std::string{"asd"}, response.string);
}

UTEST(CodegenClient, ResponseHeadersMissing) {
  int count = 0;
  utest::HttpServerMock mock(
      [&count](const utest::HttpServerMock::HttpRequest&) {
        count++;

        return utest::HttpServerMock::HttpResponse{
            200,
            clients::http::Headers{
                {"enum", "value1"},
            },
            "{}",
        };
      });

  // Do not use ClientImpl in production code!
  ClientWithMock client(mock.GetBaseUrl());

  namespace operation =
      clients::userver_sample::autogen_complex_response_headers::get;
  EXPECT_THROW(client->AutogenComplexResponseHeaders(), operation::Exception);
}

UTEST(CodegenClient, MultipleOkResponses) {
  namespace operation =
      clients::userver_sample::autogen_multiple_ok_replies::post;

  int count = 0;
  utest::HttpServerMock mock(
      [&count](const utest::HttpServerMock::HttpRequest& request) {
        count++;

        return utest::HttpServerMock::HttpResponse{
            std::stoi(request.query.at("param")),
            {},
            "{\"x\": \"sss\", \"y\": 2, \"z\": 3.3 }",
        };
      });

  // Do not use ClientImpl in production code!
  ClientWithMock client(mock.GetBaseUrl());

  {
    auto response200 = client->AutogenMultipleOkReplies({"200"});
    EXPECT_EQ(1, count);
    ASSERT_TRUE(std::get_if<operation::Response200>(&response200));
    EXPECT_EQ(operation::Response200{std::string("sss")},
              std::get<operation::Response200>(response200));
  }

  {
    auto response210 = client->AutogenMultipleOkReplies({"210"});
    EXPECT_EQ(2, count);
    ASSERT_TRUE(std::get_if<operation::Response210>(&response210));
    EXPECT_EQ(operation::Response210{2},
              std::get<operation::Response210>(response210));
  }
}

UTEST(CodegenClient, FutureTimeoutException) {
  namespace operation = clients::userver_sample::autogen_empty::get;

  utest::HttpServerMock mock(
      [](const utest::HttpServerMock::HttpRequest& /*request*/) {
        engine::InterruptibleSleepFor(std::chrono::seconds(20));

        return utest::HttpServerMock::HttpResponse{
            200,
            {},
            "{}",
        };
      });

  // Do not use ClientImpl in production code!
  ClientWithMock client(mock.GetBaseUrl());

  clients::codegen::CommandControl cc{std::chrono::milliseconds(1), 1};
  EXPECT_THROW(client->AutogenEmptyGet(cc), operation::Exception);
}

TEST(CodegenClient, ConsumesCustom) {
  clients::userver_sample::autogen_non_json_request_and_response::post::Request
      request;
  EXPECT_EQ(request.GetHeaders().at(::http::headers::kContentType),
            "text/markdown");
}

TEST(CodegenClient, ConsumesDefault) {
  clients::userver_sample::autogen_non_json_response::post::Request request;
  EXPECT_EQ(request.GetHeaders().at(::http::headers::kContentType),
            "application/json; charset=utf-8");
}

TEST(CodegenClient, OptionalArrayParameter) {
  clients::userver_sample::autogen_info::post::Request request;
  EXPECT_TRUE((std::is_same<std::optional<::std::string>,
                            decltype(request.header_value)>::value));
}

TEST(CodegenClient, ExceptionsInheritance) {
  namespace clients_empty_get = clients::userver_sample::autogen_empty::get;

  EXPECT_THROW(Throw<clients_empty_get::TimeoutException>(),
               clients::codegen::Exception)
      << "Not derived from base codegen exception";

  EXPECT_THROW(Throw<clients_empty_get::TimeoutException>(),
               clients::userver_sample::Exception)
      << "Not derived from client base exception";

  EXPECT_THROW(Throw<clients_empty_get::TimeoutException>(),
               clients_empty_get::Exception)
      << "Not derived from handle base exception";

  EXPECT_THROW(Throw<clients_empty_get::TimeoutException>(),
               clients::codegen::TimeoutException)
      << "Not derived from base codegen timeout exception";

  EXPECT_THROW(Throw<clients_empty_get::TimeoutException>(),
               clients::userver_sample::TimeoutException)
      << "Not derived from client base timeout exception";

  EXPECT_THROW(Throw<clients_empty_get::Exception>(),
               clients::codegen::Exception)
      << "Not derived from base codegen exception";
  EXPECT_THROW(Throw<clients_empty_get::Exception>(),
               clients::userver_sample::Exception)
      << "Not derived from client base exception";
}
