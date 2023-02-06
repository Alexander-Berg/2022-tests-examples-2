#include <gtest/gtest.h>

#include <atomic>
#include <chrono>
#include <mutex>
#include <optional>
#include <random>
#include <string>

#include <clients/billing-subventions-x/client_mock_base.hpp>
#include <userver/engine/task/task.hpp>
#include <userver/logging/log.hpp>
#include <userver/utils/async.hpp>

#include <models/limiter.hpp>
#include <subvention_matcher/impl/impl.hpp>
#include <subvention_matcher/types.hpp>

#include "common.hpp"
#include "rps_limiters_batch_generators.hpp"

using namespace std::chrono_literals;
using namespace subvention_matcher;
using namespace models;
namespace bsx = clients::billing_subventions_x;

class BSXClientMock : public bsx::ClientMockBase {
 public:
  BSXClientMock(size_t wait_ms) : bsx::ClientMockBase(), wait_ms_(wait_ms) {}

  bsx::v2_rules_match::post::Response V2RulesMatch(
      const bsx::v2_rules_match::post::Request& /*request*/,
      const bsx::CommandControl& /*command_control*/ = {}) const override {
    std::this_thread::sleep_for(std::chrono::milliseconds(wait_ms_));

    return {};
  }

  size_t wait_ms_;
};

void RunRandomBulkTest(size_t batch_size, const BSXClientMock& bsx_client,
                       RulesMatchLimiter& rps_limiter) {
  int keypoint_size = batch_size % 2 == 0 ? batch_size / 2 : batch_size;
  int properties_size = batch_size % 2 == 0 ? 2 : 1;

  auto keypoints = BuildKeypoints(keypoint_size);
  auto properties = BuildProperties(properties_size);

  subvention_matcher::impl::DoMatch(keypoints, properties, bsx_client,
                                    rps_limiter, {});
}

struct TestResult {
  bool timeout_happened;
};

void RunRandomBulkRequestAndReport(size_t batch_size, BSXClientMock& bsx_client,
                                   RulesMatchLimiter& rps_limiter,
                                   std::vector<TestResult>& results,
                                   std::mutex& results_lock) {
  bool timeout_happened = false;
  try {
    RunRandomBulkTest(batch_size, bsx_client, rps_limiter);
  } catch (models::BatchSendTimeoutException&) {
    LOG_DEBUG() << "timeout happened!";
    timeout_happened = true;
  }

  TestResult result{timeout_happened};
  std::lock_guard results_guard_lock(results_lock);
  results.push_back(result);
}

struct TestData {
  std::uint32_t exec_rate;
  std::uint32_t max_queue_size;
  size_t batch_size;
  std::chrono::milliseconds bulk_timeout_ms;
  size_t bsx_wait_ms;

  size_t expected_successful_requests;
  size_t expected_timeouted_requests;
};

struct RunBulkTestsParametrized : public BaseTestWithParam<TestData> {};

TEST_P(RunBulkTestsParametrized, Test) {
  constexpr int kThreadCount = 2;
  constexpr int kCoroCount = 2;

  RunInCoro(
      [] {
        const auto [exec_rate, max_queue_size, batch_size, bulk_timeout_ms,
                    bsx_wait_ms, expected_successful_requests,
                    expected_timeouted_requests] = GetParam();
        BSXClientMock bsx_client{bsx_wait_ms};
        RulesMatchLimiter rps_limiter{"test_limiter"};

        limiter_config::RulesMatchSettings settings{
            {exec_rate,       // exec_rate
             max_queue_size,  // max_queue_size
             std::nullopt,    // submit_timeout_ms
             std::nullopt},   // wait_for_timeout_ms
            {
                max_queue_size,  // soft_max_queue_size
                bulk_timeout_ms  // bulk_timeout_ms
            }};
        rps_limiter.SetLimiterSettings(settings);

        std::vector<TestResult> results;
        std::mutex results_lock;

        const auto run_bulk_and_report = [&bsx_client, &rps_limiter, &results,
                                          &results_lock,
                                          batch_size = batch_size]() {
          RunRandomBulkRequestAndReport(batch_size, bsx_client, rps_limiter,
                                        results, results_lock);
        };

        engine::Task coros[kCoroCount];
        for (size_t i = 0; i < kCoroCount; ++i) {
          coros[i] =
              utils::Async("coro_" + std::to_string(i), run_bulk_and_report);
        }

        for (size_t i = 0; i < kCoroCount; ++i) {
          coros[i].Wait();
        }

        size_t successful_requests = 0;
        size_t timeouted_requests = 0;

        for (const auto& result : results) {
          if (!result.timeout_happened) {
            ++successful_requests;
          } else {
            ++timeouted_requests;
          }
        }

        ASSERT_EQ(successful_requests, expected_successful_requests);
        ASSERT_EQ(timeouted_requests, expected_timeouted_requests);
      },
      kThreadCount);
}

INSTANTIATE_TEST_SUITE_P(RunBulkTestsParametrized, RunBulkTestsParametrized,
                         ::testing::ValuesIn({TestData{
                             1,    // exec_rate
                             6,    // queue size
                             3,    // batch size
                             5ms,  // bulk_timeout ms
                             50,   // bsx_wait_ms
                             2,    // expected successes
                             0     // expected bulk timeouts
                         }}));
