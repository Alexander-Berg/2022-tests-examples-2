
#include <atomic>

#include <testing/taxi_config.hpp>
#include <userver/engine/sleep.hpp>
#include <userver/utest/utest.hpp>

#include <experiments3/routestats_drive_hedged_request.hpp>

#include "endpoints/full/plugins/drive_order_flow/hedged_request.hpp"

#include "tests/context_mock_test.hpp"
#include "tests/endpoints/full/plugins/drive_order_flow/drive_order_flow_common_test.hpp"

namespace routestats::plugins::drive_order_flow {

namespace {

namespace drive_handler = clients::yandex_drive::offers_offer_type::post;

using DriveRequest = drive_handler::Request;
using DriveResponse = drive_handler::Response;

// actual value is ignored in this testsuite
const test::DriveRequest kRequest{};

const clients::codegen::CommandControl kCommandControl{
    std::chrono::milliseconds(50),  // timeout
    1,  // attempts (named retries, but https://t.me/c/1307265028/51224)
};

core::Experiments GetExperiments(
    int n_requests = 0, int hedged_request_offset_ms = 0,
    int timeout_ms_override = 0, int attempts_override = 0,
    const std::optional<std::string>& alias = std::nullopt) {
  core::ExpMappedData experiments{};
  using HedgedRequestExp = experiments3::RoutestatsDriveHedgedRequest;
  formats::json::ValueBuilder vb;
  vb["enabled"] = n_requests > 0;
  vb["n_requests"] = n_requests;
  vb["offset_ms"] = hedged_request_offset_ms;
  if (timeout_ms_override) {
    vb["qos_override"]["timeout"] = timeout_ms_override;
  }
  if (attempts_override) {
    vb["qos_override"]["attempts"] = attempts_override;
  }
  vb["alias"] = alias;
  experiments[HedgedRequestExp::kName] = {
      HedgedRequestExp::kName,
      vb.ExtractValue(),
      {},
  };
  return {std::move(experiments)};
}

class HedgedRequestClientWrapper {
 public:
  HedgedRequestClientWrapper()
      : client_([](const test::DriveRequest&) -> test::DriveResponse {
          throw std::runtime_error("client called before handlers were set");
        }),
        times_called_(0) {}

  const test::MockYandexDriveClient& GetClient() const { return client_; }

  void SetHandlers(std::vector<test::OffersHandler> handlers) {
    handlers_ = std::move(handlers);
    client_.SetHandler(
        [&](const test::DriveRequest& request) -> test::DriveResponse {
          size_t request_index = times_called_.fetch_add(1);
          EXPECT_LT(request_index, handlers_.size());
          return handlers_.at(request_index)(request);
        });
  }

  size_t GetTimesCalled() { return times_called_.load(); }

 private:
  test::MockYandexDriveClient client_;
  std::atomic<size_t> times_called_;
  std::vector<test::OffersHandler> handlers_;
};

}  // namespace

TEST(DriveHedgedRequest, Disabled) {
  size_t times_called = 0;
  test::MockYandexDriveClient client(
      [&times_called](const test::DriveRequest&) -> test::DriveResponse {
        ++times_called;
        throw drive_handler::Response500(clients::yandex_drive::ApiError{});
      });

  const auto experiments = GetExperiments();
  HedgedRequest hedged_request(experiments, kCommandControl, client, kRequest);
  EXPECT_THROW({ hedged_request.PerformRequest(); }, drive_handler::Exception);
  EXPECT_EQ(times_called, 1);
  const auto stats = hedged_request.TestingGetStats();
  ASSERT_TRUE(stats);
  EXPECT_EQ(stats->n_requests, 1);
  EXPECT_EQ(stats->fail_idx, 1);
  EXPECT_FALSE(stats->short_path);
  EXPECT_FALSE(stats->alias);
  ASSERT_EQ(stats->timeout.value(), kCommandControl.timeout.value());
  ASSERT_EQ(stats->attempts.value(), kCommandControl.retries.value());
}

TEST(DriveHedgedRequest, SingleRequest) {
  size_t times_called = 0;
  test::MockYandexDriveClient client(
      [&times_called](const test::DriveRequest&) -> test::DriveResponse {
        ++times_called;
        throw drive_handler::Response500(clients::yandex_drive::ApiError{});
      });

  const auto experiments =
      GetExperiments(1, /*offset_ms=*/0, /*timeout_ms_override=*/1337,
                     /*attempts_override=*/2, "some_alias");
  HedgedRequest hedged_request(experiments, kCommandControl, client, kRequest);
  EXPECT_THROW({ hedged_request.PerformRequest(); }, drive_handler::Exception);
  EXPECT_EQ(times_called, 1);
  const auto stats = hedged_request.TestingGetStats();
  ASSERT_TRUE(stats);
  EXPECT_EQ(stats->n_requests, 1);
  EXPECT_EQ(stats->fail_idx, 1);
  EXPECT_FALSE(stats->short_path);
  ASSERT_TRUE(stats->alias);
  EXPECT_EQ(stats->alias, "some_alias");
  ASSERT_EQ(stats->timeout.value(), std::chrono::milliseconds(1337));
  ASSERT_EQ(stats->attempts.value(), 2);
}

// These tests check that offset=0ms works fine

UTEST(DriveHedgedRequest, RespFirstSuccessful) {
  HedgedRequestClientWrapper client_wrapper;
  const auto experiments = GetExperiments(2);
  HedgedRequest hedged_request(experiments, kCommandControl,
                               client_wrapper.GetClient(), kRequest);
  hedged_request.TestingEnableDownstreamSignal();
  client_wrapper.SetHandlers({
      [](const test::DriveRequest&) -> test::DriveResponse {
        test::DriveResponse response;
        response.reason_code = "one_successful";
        return response;
      },
      [&hedged_request](const test::DriveRequest&) -> test::DriveResponse {
        hedged_request.TestingWaitFirstRequest();
        engine::current_task::CancellationPoint();
        EXPECT_TRUE(false) << "this task should have been cancelled";
        throw drive_handler::Response500(clients::yandex_drive::ApiError{});
      },
  });
  const auto response = hedged_request.PerformRequest();
  // maybe only one call
  EXPECT_NE(client_wrapper.GetTimesCalled(), 0);
  EXPECT_LE(client_wrapper.GetTimesCalled(), 2);
  ASSERT_TRUE(response);
  EXPECT_EQ(response->reason_code, "one_successful");
  const auto stats = hedged_request.TestingGetStats();
  ASSERT_TRUE(stats);
  EXPECT_EQ(stats->n_requests, 2);
  EXPECT_EQ(stats->fail_idx, 0);
  EXPECT_FALSE(stats->short_path);
  EXPECT_FALSE(stats->alias);
  ASSERT_EQ(stats->timeout.value(), kCommandControl.timeout.value());
  ASSERT_EQ(stats->attempts.value(), kCommandControl.retries.value());
}

UTEST(DriveHedgedRequest, RespSecondSuccessful) {
  HedgedRequestClientWrapper client_wrapper;
  const auto experiments = GetExperiments(2);
  HedgedRequest hedged_request(experiments, kCommandControl,
                               client_wrapper.GetClient(), kRequest);
  hedged_request.TestingEnableDownstreamSignal();
  client_wrapper.SetHandlers({
      [](const test::DriveRequest&) -> test::DriveResponse {
        throw drive_handler::Response500(clients::yandex_drive::ApiError{});
      },
      [&hedged_request](const test::DriveRequest&) -> test::DriveResponse {
        hedged_request.TestingWaitFirstRequest();
        test::DriveResponse response;
        response.reason_code = "one_successful";
        return response;
      },
  });
  const auto response = hedged_request.PerformRequest();
  EXPECT_EQ(client_wrapper.GetTimesCalled(), 2);
  ASSERT_TRUE(response);
  EXPECT_EQ(response->reason_code, "one_successful");
  const auto stats = hedged_request.TestingGetStats();
  ASSERT_TRUE(stats);
  EXPECT_EQ(stats->n_requests, 2);
  EXPECT_EQ(stats->fail_idx, 1);
  EXPECT_FALSE(stats->short_path);
  EXPECT_FALSE(stats->alias);
  ASSERT_EQ(stats->timeout.value(), kCommandControl.timeout.value());
  ASSERT_EQ(stats->attempts.value(), kCommandControl.retries.value());
}

UTEST(DriveHedgedRequest, RespBoth500) {
  HedgedRequestClientWrapper client_wrapper;
  const auto experiments = GetExperiments(2);
  HedgedRequest hedged_request(experiments, kCommandControl,
                               client_wrapper.GetClient(), kRequest);
  client_wrapper.SetHandlers({
      [](const test::DriveRequest&) -> test::DriveResponse {
        throw drive_handler::Response500(clients::yandex_drive::ApiError{});
      },
      [](const test::DriveRequest&) -> test::DriveResponse {
        throw drive_handler::Response500(clients::yandex_drive::ApiError{});
      },
  });
  EXPECT_THROW({ hedged_request.PerformRequest(); },
               drive_handler::Response500);
  EXPECT_EQ(client_wrapper.GetTimesCalled(), 2);
  const auto stats = hedged_request.TestingGetStats();
  ASSERT_TRUE(stats);
  EXPECT_EQ(stats->n_requests, 2);
  EXPECT_EQ(stats->fail_idx, 2);
  EXPECT_FALSE(stats->short_path);
  EXPECT_FALSE(stats->alias);
  ASSERT_EQ(stats->timeout.value(), kCommandControl.timeout.value());
  ASSERT_EQ(stats->attempts.value(), kCommandControl.retries.value());
}

// These tests check that short path works fine (first request finished befor
// offset passed)

UTEST(DriveHedgedRequest, OffsetShortPathFirstSuccessful) {
  HedgedRequestClientWrapper client_wrapper;
  const auto experiments = GetExperiments(/*n_requests=*/2, /*offset_ms=*/30);
  HedgedRequest hedged_request(experiments, kCommandControl,
                               client_wrapper.GetClient(), kRequest);
  hedged_request.TestingEnableDownstreamSignal();
  client_wrapper.SetHandlers({
      [](const test::DriveRequest&) -> test::DriveResponse {
        test::DriveResponse response;
        response.reason_code = "one_successful";
        return response;
      },
      // second request should not be started
  });
  const auto response = hedged_request.PerformRequest();
  EXPECT_EQ(client_wrapper.GetTimesCalled(), 1);
  ASSERT_TRUE(response);
  EXPECT_EQ(response->reason_code, "one_successful");
  const auto stats = hedged_request.TestingGetStats();
  ASSERT_TRUE(stats);
  EXPECT_EQ(stats->n_requests, 2);
  EXPECT_EQ(stats->fail_idx, 0);
  EXPECT_TRUE(stats->short_path);
  EXPECT_FALSE(stats->alias);
  ASSERT_EQ(stats->timeout.value(), kCommandControl.timeout.value());
  ASSERT_EQ(stats->attempts.value(), kCommandControl.retries.value());
}

UTEST(DriveHedgedRequest, OffsetShortPathSecondSuccessful) {
  HedgedRequestClientWrapper client_wrapper;
  const auto experiments = GetExperiments(/*n_requests=*/2, /*offset_ms=*/30);
  HedgedRequest hedged_request(experiments, kCommandControl,
                               client_wrapper.GetClient(), kRequest);
  hedged_request.TestingEnableDownstreamSignal();
  client_wrapper.SetHandlers({
      [](const test::DriveRequest&) -> test::DriveResponse {
        throw drive_handler::Response500(clients::yandex_drive::ApiError{});
      },
      [&hedged_request](const test::DriveRequest&) -> test::DriveResponse {
        hedged_request.TestingWaitFirstRequest();
        test::DriveResponse response;
        response.reason_code = "one_successful";
        return response;
      },
  });
  const auto response = hedged_request.PerformRequest();
  EXPECT_EQ(client_wrapper.GetTimesCalled(), 2);
  ASSERT_TRUE(response);
  EXPECT_EQ(response->reason_code, "one_successful");
  const auto stats = hedged_request.TestingGetStats();
  ASSERT_TRUE(stats);
  EXPECT_EQ(stats->n_requests, 2);
  EXPECT_EQ(stats->fail_idx, 1);
  EXPECT_TRUE(stats->short_path);
  EXPECT_FALSE(stats->alias);
  ASSERT_EQ(stats->timeout.value(), kCommandControl.timeout.value());
  ASSERT_EQ(stats->attempts.value(), kCommandControl.retries.value());
}

UTEST(DriveHedgedRequest, OffsetShortPathBoth500) {
  HedgedRequestClientWrapper client_wrapper;
  const auto experiments = GetExperiments(/*n_requests=*/2, /*offset_ms=*/30,
                                          /*timeout_ms_override=*/1337);
  HedgedRequest hedged_request(experiments, kCommandControl,
                               client_wrapper.GetClient(), kRequest);
  client_wrapper.SetHandlers({
      [](const test::DriveRequest&) -> test::DriveResponse {
        throw drive_handler::Response500(clients::yandex_drive::ApiError{});
      },
      [](const test::DriveRequest&) -> test::DriveResponse {
        throw drive_handler::Response500(clients::yandex_drive::ApiError{});
      },
  });
  EXPECT_THROW({ hedged_request.PerformRequest(); },
               drive_handler::Response500);
  EXPECT_EQ(client_wrapper.GetTimesCalled(), 2);
  const auto stats = hedged_request.TestingGetStats();
  ASSERT_TRUE(stats);
  EXPECT_EQ(stats->n_requests, 2);
  EXPECT_EQ(stats->fail_idx, 2);
  EXPECT_TRUE(stats->short_path);
  EXPECT_FALSE(stats->alias);
  ASSERT_EQ(stats->timeout.value(), std::chrono::milliseconds(1337));
  ASSERT_EQ(stats->attempts.value(), kCommandControl.retries.value());
}

// This test checks that short path falls back to long path if first request
// didn't finish early

UTEST(DriveHedgedRequest, OffsetLongPath) {
  HedgedRequestClientWrapper client_wrapper;
  const auto experiments = GetExperiments(
      /*n_requests=*/2, /*offset_ms=*/10, /*timeout_ms_override=*/0,
      /*attempts_override=*/2, "some_alias");
  HedgedRequest hedged_request(experiments, kCommandControl,
                               client_wrapper.GetClient(), kRequest);
  client_wrapper.SetHandlers({
      [](const test::DriveRequest&) -> test::DriveResponse {
        engine::SleepFor(std::chrono::milliseconds(30));
        engine::current_task::CancellationPoint();
        EXPECT_TRUE(false) << "this task should have been cancelled";
        throw drive_handler::Response500(clients::yandex_drive::ApiError{});
      },
      [](const test::DriveRequest&) -> test::DriveResponse {
        test::DriveResponse response;
        response.reason_code = "one_successful";
        return response;
      },
  });
  const auto response = hedged_request.PerformRequest();
  EXPECT_EQ(client_wrapper.GetTimesCalled(), 2);
  ASSERT_TRUE(response);
  EXPECT_EQ(response->reason_code, "one_successful");
  const auto stats = hedged_request.TestingGetStats();
  ASSERT_TRUE(stats);
  EXPECT_EQ(stats->n_requests, 2);
  EXPECT_EQ(stats->fail_idx, 0);
  EXPECT_FALSE(stats->short_path);
  ASSERT_TRUE(stats->alias);
  EXPECT_EQ(stats->alias, "some_alias");
  ASSERT_EQ(stats->timeout.value(), kCommandControl.timeout.value());
  ASSERT_EQ(stats->attempts.value(), 2);
}

}  // namespace routestats::plugins::drive_order_flow
