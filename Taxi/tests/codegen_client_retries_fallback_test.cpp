
#include <atomic>

#include <userver/utest/utest.hpp>

#include <testing/taxi_config.hpp>
#include <userver/engine/sleep.hpp>
#include <userver/utest/http_client.hpp>
#include <userver/utest/http_server_mock.hpp>

#include <tests/client_with_mock.hpp>

class HttpServerWithStatusCode {
 public:
  HttpServerWithStatusCode()
      : mock_([this](const utest::HttpServerMock::HttpRequest& /*request*/) {
          if (delay_ms_.load().count()) engine::SleepFor(delay_ms_.load());

          count_++;
          return utest::HttpServerMock::HttpResponse{
              status_code_.load(),
              {},
              "{}",
          };
        }) {}

  void SetStatusCode(int code) { status_code_ = code; }

  void SetDelay(std::chrono::milliseconds ms) { delay_ms_ = ms; }

  int GetHits() const { return count_; }

  void ResetHits() { count_ = 0; }

  auto& Server() { return mock_; }

 private:
  std::atomic_size_t count_{0};
  std::atomic_int status_code_{500};
  std::atomic<std::chrono::milliseconds> delay_ms_{
      std::chrono::milliseconds(0)};
  utest::HttpServerMock mock_;
};

struct RetriesParam {
  int status_code;
  bool fallback_enabled;
  int expected_hits;
  int expected_errors;
  int expected_success;
  bool expected_throws;
};

inline std::string PrintToString(const RetriesParam& d) {
  return std::to_string(d.status_code) + "_fallback" +
         std::to_string(d.fallback_enabled) + "_hits" +
         std::to_string(d.expected_hits) + "_errors" +
         std::to_string(d.expected_errors) + "_success" +
         std::to_string(d.expected_success) + "_throws" +
         std::to_string(d.expected_throws);
}

class CodegenClientRetriesFallback
    : public ::testing::TestWithParam<RetriesParam> {};

INSTANTIATE_UTEST_SUITE_P(
    /*no prefix*/, CodegenClientRetriesFallback,
    ::testing::ValuesIn(std::initializer_list<RetriesParam>{
        {200, true, 1, 0, 1, false},
        {400, false, 1, 0, 1, true},
        {429, false, 1, 1, 0, true},
        {500, false, 3, 1, 0, true},
        {500, true, 1, 1, 0, true},
    }),
    ::testing::PrintToStringParamName());

UTEST_P(CodegenClientRetriesFallback, Success) {
  const auto& param = GetParam();
  auto fallback = "handler.userver-sample./autogen/empty-get.fallback";

  HttpServerWithStatusCode mock;
  ClientWithMock client(mock.Server().GetBaseUrl());
  client.GetStatisticsClient().SetStrictFallbackCheck(true);

  mock.SetStatusCode(param.status_code);
  clients::codegen::CommandControl cc{std::chrono::milliseconds(1000), 3};
  client.GetStatisticsClient().MockFallback(fallback, param.fallback_enabled);

  if (param.expected_throws) {
    EXPECT_THROW(client->AutogenEmptyGet(cc), std::exception);
  } else {
    EXPECT_NO_THROW(client->AutogenEmptyGet(cc));
  }
  EXPECT_EQ(mock.GetHits(), param.expected_hits);
  EXPECT_EQ(
      client.GetStatisticsClient()
          .GetMetrics()["handler.userver-sample./autogen/empty-get.error"],
      param.expected_errors);
  EXPECT_EQ(
      client.GetStatisticsClient()
          .GetMetrics()["handler.userver-sample./autogen/empty-get.success"],
      param.expected_success);
}
