#include <gtest/gtest.h>

#include <atomic>
#include <chrono>
#include <mutex>
#include <optional>
#include <random>
#include <string>

#include <clients/billing-subventions-x/client_mock_base.hpp>
#include <userver/engine/condition_variable.hpp>
#include <userver/engine/deadline.hpp>
#include <userver/engine/sleep.hpp>
#include <userver/engine/task/task.hpp>
#include <userver/logging/log.hpp>
#include <userver/utils/async.hpp>

#include <helpers/rules_match_wrapper.hpp>
#include <models/limiter.hpp>
#include <subvention_matcher/impl/impl.hpp>
#include <subvention_matcher/types.hpp>

#include "common.hpp"
#include "rps_limiters_batch_generators.hpp"

using namespace std::chrono_literals;
using namespace subvention_matcher;
using namespace models;
namespace bsx = clients::billing_subventions_x;

namespace {
class BSXClientMock : public bsx::ClientMockBase {
 public:
  BSXClientMock(std::chrono::milliseconds wait_ms)
      : bsx::ClientMockBase(), wait_ms_(wait_ms) {}

  bsx::v2_rules_match::post::Response V2RulesMatch(
      const bsx::v2_rules_match::post::Request& /*request*/,
      const bsx::CommandControl& /*command_control*/ = {}) const override {
    while (do_wait_) {
      engine::SleepFor(2ms);
    }
    if (do_throw_) {
      throw bsx::v2_rules_match::post::Response500();
    }
    engine::InterruptibleSleepFor(wait_ms_);
    ++times_called_;
    return {};
  }

  bsx::v2_rules_match_bulk_single_ride::post::Response
  V2RulesMatchBulkSingleRide(
      const bsx::v2_rules_match_bulk_single_ride::post::Request& /*request*/,
      const bsx::CommandControl& /*command_control*/ = {}) const override {
    while (do_wait_) {
      engine::SleepFor(2ms);
    }
    if (do_throw_) {
      throw bsx::v2_rules_match_bulk_single_ride::post::Response500();
    }
    engine::InterruptibleSleepFor(wait_ms_);
    ++times_called_;
    return {};
  }

  std::chrono::milliseconds wait_ms_;

  std::atomic_bool do_throw_ = false;
  std::atomic_bool do_wait_ = true;
  mutable uint64_t times_called_ = 0;
};

struct TestResult {
  bool timeout_happened;
};

struct TestData {
  size_t exec_rate;
  size_t max_queue_size;
  size_t batch_size;
  size_t bulk_timeout_ms;
  std::optional<size_t> wait_timeout_ms;
  size_t bsx_wait_ms;

  size_t expected_successful_requests;
  size_t expected_timeouted_requests;
};

}  // namespace

const int key_points_size = 10;
const int properties_size = 2;
const int bulk_key_points_size = 11;
const int bulk_properties_size = 7;

struct RunCancelationTestsParametrized : public BaseTestWithParam<TestData> {};

UTEST_MT(BaseTest, TestTooBigForQueue, 2) {
  const auto key_points = BuildKeypoints(key_points_size);
  const auto properties = BuildProperties(properties_size);
  BSXClientMock bsx_client{10ms};
  bsx_client.do_wait_ = false;

  RulesMatchLimiter rps_limiter{"test_limiter"};

  limiter_config::RulesMatchSettings settings{
      {10,             // exec_rate
       100,            // max_queue_size
       std::nullopt,   // submit_timeout_ms
       std::nullopt},  // wait_for_timeout_ms
      {
          1,      // soft_queue_size
          1000ms  // bulk_timeout_ms
      }};
  rps_limiter.SetLimiterSettings(settings);
  helpers::RulesMatchWrapper wrapper(rps_limiter,
                                     settings.common_settings.max_queue_size);
  auto& stats = wrapper.GetRunStats();

  subvention_matcher::impl::BatchFillQueueWithMatchRules(
      key_points, properties, bsx_client, stats, wrapper, std::nullopt);

  const auto errors = wrapper.WaitAndGetErrors();
  ASSERT_EQ(errors, 0);
  ASSERT_EQ(bsx_client.times_called_,
            (key_points.size() - 1) * properties.size());
}

UTEST_MT(BaseTest, TestBulkTooBigForQueue, 2) {
  const auto key_points = BuildKeypoints(bulk_key_points_size);
  const auto properties = BuildProperties(bulk_properties_size);
  BSXClientMock bsx_client{10ms};
  bsx_client.do_wait_ = false;

  RulesMatchLimiter rps_limiter{"test_limiter"};

  limiter_config::RulesMatchSettings settings{
      {10,             // exec_rate
       100,            // max_queue_size
       std::nullopt,   // submit_timeout_ms
       std::nullopt},  // wait_for_timeout_ms
      {
          1,      // soft_queue_size
          1000ms  // bulk_timeout_ms
      }};
  rps_limiter.SetLimiterSettings(settings);
  helpers::RulesMatchWrapper wrapper(rps_limiter,
                                     settings.common_settings.max_queue_size);
  auto& stats = wrapper.GetRunStats();

  subvention_matcher::impl::BatchFillQueueWithBulkMatchRules(
      key_points, properties, bsx_client, stats, wrapper, std::nullopt);

  const auto errors = wrapper.WaitAndGetErrors();
  ASSERT_EQ(errors, 0);
  ASSERT_EQ(bsx_client.times_called_, properties.size());
}

UTEST_MT(BaseTest, TestTooBigForQueueCancel, 2) {
  const auto key_points = BuildKeypoints(key_points_size);
  const auto properties = BuildProperties(properties_size);
  using namespace std::chrono_literals;
  BSXClientMock bsx_client{10ms};
  RulesMatchLimiter rps_limiter{"test_limiter"};

  limiter_config::RulesMatchSettings settings{
      {10,             // exec_rate
       100,            // max_queue_size
       std::nullopt,   // submit_timeout_ms
       std::nullopt},  // wait_for_timeout_ms
      {
          1,   // soft_queue_size
          1ms  // bulk_timeout_ms
      }};
  rps_limiter.SetLimiterSettings(settings);

  helpers::RulesMatchWrapper wrapper(rps_limiter,
                                     settings.common_settings.max_queue_size);
  auto& stats = wrapper.GetRunStats();
  subvention_matcher::impl::BatchFillQueueWithMatchRules(
      key_points, properties, bsx_client, stats, wrapper, std::nullopt);

  helpers::RulesMatchWrapper wrapper2(rps_limiter,
                                      settings.common_settings.max_queue_size);
  auto& stats2 = wrapper2.GetRunStats();
  EXPECT_THROW(
      subvention_matcher::impl::BatchFillQueueWithMatchRules(
          key_points, properties, bsx_client, stats2, wrapper2, std::nullopt),
      models::BatchSendTimeoutException);

  bsx_client.do_wait_ = false;
  auto errors = wrapper.WaitAndGetErrors();
  ASSERT_EQ(errors, 0);

  errors = wrapper2.WaitAndGetErrors();
  ASSERT_EQ(errors, 0);

  ASSERT_EQ(bsx_client.times_called_,
            (key_points.size() - 1) * properties.size());
}

UTEST_MT(BaseTest, TestBulkTooBigForQueueCancel, 2) {
  const auto key_points = BuildKeypoints(bulk_key_points_size);
  const auto properties = BuildProperties(bulk_properties_size);
  using namespace std::chrono_literals;
  BSXClientMock bsx_client{10ms};
  RulesMatchLimiter rps_limiter{"test_limiter"};

  limiter_config::RulesMatchSettings settings{
      {4,              // exec_rate
       100,            // max_queue_size
       std::nullopt,   // submit_timeout_ms
       std::nullopt},  // wait_for_timeout_ms
      {
          1,   // soft_queue_size
          1ms  // bulk_timeout_ms
      }};
  rps_limiter.SetLimiterSettings(settings);

  helpers::RulesMatchWrapper wrapper(rps_limiter,
                                     settings.common_settings.max_queue_size);
  auto& stats = wrapper.GetRunStats();
  subvention_matcher::impl::BatchFillQueueWithBulkMatchRules(
      key_points, properties, bsx_client, stats, wrapper, std::nullopt);

  helpers::RulesMatchWrapper wrapper2(rps_limiter,
                                      settings.common_settings.max_queue_size);
  auto& stats2 = wrapper2.GetRunStats();
  EXPECT_THROW(
      subvention_matcher::impl::BatchFillQueueWithBulkMatchRules(
          key_points, properties, bsx_client, stats2, wrapper2, std::nullopt),
      models::BatchSendTimeoutException);

  bsx_client.do_wait_ = false;
  auto errors = wrapper.WaitAndGetErrors();
  ASSERT_EQ(errors, 0);

  errors = wrapper2.WaitAndGetErrors();
  ASSERT_EQ(errors, 0);

  ASSERT_EQ(bsx_client.times_called_, properties.size());
}

UTEST_MT(BaseTest, TestResultsTimeout, 2) {
  const auto key_points = BuildKeypoints(key_points_size);
  const auto properties = BuildProperties(properties_size);
  using namespace std::chrono_literals;
  BSXClientMock bsx_client{10ms};
  bsx_client.do_wait_ = true;
  RulesMatchLimiter rps_limiter{"test_limiter"};

  limiter_config::RulesMatchSettings settings{
      {10,            // exec_rate
       100,           // max_queue_size
       std::nullopt,  // submit_timeout_ms
       100ms},        // wait_for_timeout_ms
      {
          1,      // soft_queue_size
          1000ms  // bulk_timeout_ms
      }};
  rps_limiter.SetLimiterSettings(settings);

  helpers::RulesMatchWrapper wrapper(rps_limiter,
                                     settings.common_settings.max_queue_size);
  auto& stats = wrapper.GetRunStats();
  subvention_matcher::impl::BatchFillQueueWithMatchRules(
      key_points, properties, bsx_client, stats, wrapper, std::nullopt);

  auto errors = wrapper.WaitAndGetErrors();
  bsx_client.do_wait_ = false;

  ASSERT_EQ(errors, (key_points.size() - 1) * properties.size());
  ASSERT_EQ(bsx_client.times_called_, 0);
}

UTEST_MT(BaseTest, TestBulkResultsTimeout, 2) {
  const auto key_points = BuildKeypoints(bulk_key_points_size);
  const auto properties = BuildProperties(bulk_properties_size);
  using namespace std::chrono_literals;
  BSXClientMock bsx_client{10ms};
  bsx_client.do_wait_ = true;
  RulesMatchLimiter rps_limiter{"test_limiter"};

  limiter_config::RulesMatchSettings settings{
      {10,            // exec_rate
       100,           // max_queue_size
       std::nullopt,  // submit_timeout_ms
       100ms},        // wait_for_timeout_ms
      {
          1,      // soft_queue_size
          1000ms  // bulk_timeout_ms
      }};
  rps_limiter.SetLimiterSettings(settings);

  helpers::RulesMatchWrapper wrapper(rps_limiter,
                                     settings.common_settings.max_queue_size);
  auto& stats = wrapper.GetRunStats();
  subvention_matcher::impl::BatchFillQueueWithBulkMatchRules(
      key_points, properties, bsx_client, stats, wrapper, std::nullopt);

  auto errors = wrapper.WaitAndGetErrors();
  bsx_client.do_wait_ = false;

  ASSERT_EQ(errors, properties.size());
  ASSERT_EQ(bsx_client.times_called_, 0);
}

UTEST_MT(BaseTest, TestCancelAllOnError, 2) {
  const auto key_points = BuildKeypoints(key_points_size);
  const auto properties = BuildProperties(properties_size);
  BSXClientMock bsx_client{1ms};
  bsx_client.do_wait_ = false;
  bsx_client.do_throw_ = true;

  RulesMatchLimiter rps_limiter{"test_limiter"};

  limiter_config::RulesMatchSettings settings{
      {1,              // exec_rate
       100,            // max_queue_size
       std::nullopt,   // submit_timeout_ms
       std::nullopt},  // wait_for_timeout_ms
      {
          1,      // soft_queue_size
          1000ms  // bulk_timeout_ms
      }};
  rps_limiter.SetLimiterSettings(settings);
  helpers::RulesMatchWrapper wrapper(rps_limiter,
                                     settings.common_settings.max_queue_size);

  auto& stats = wrapper.GetRunStats();

  subvention_matcher::impl::BatchFillQueueWithMatchRules(
      key_points, properties, bsx_client, stats, wrapper, std::nullopt);

  wrapper.WaitAndGetErrors();
  ASSERT_EQ(bsx_client.times_called_, 0);

  ASSERT_EQ(stats.canceled_tasks, (key_points.size() - 1) * properties.size() -
                                      1);  // first throw, others cancel
}

UTEST_MT(BaseTest, TestBulkCancelAllOnError, 2) {
  const auto key_points = BuildKeypoints(bulk_key_points_size);
  const auto properties = BuildProperties(bulk_properties_size);
  BSXClientMock bsx_client{1ms};
  bsx_client.do_wait_ = false;
  bsx_client.do_throw_ = true;

  RulesMatchLimiter rps_limiter{"test_limiter"};

  limiter_config::RulesMatchSettings settings{
      {1,              // exec_rate
       100,            // max_queue_size
       std::nullopt,   // submit_timeout_ms
       std::nullopt},  // wait_for_timeout_ms
      {
          1,      // soft_queue_size
          1000ms  // bulk_timeout_ms
      }};
  rps_limiter.SetLimiterSettings(settings);
  helpers::RulesMatchWrapper wrapper(rps_limiter,
                                     settings.common_settings.max_queue_size);

  auto& stats = wrapper.GetRunStats();

  subvention_matcher::impl::BatchFillQueueWithBulkMatchRules(
      key_points, properties, bsx_client, stats, wrapper, std::nullopt);

  wrapper.WaitAndGetErrors();
  ASSERT_EQ(bsx_client.times_called_, 0);

  ASSERT_EQ(stats.canceled_tasks,
            properties.size() - 1);  // first throw, others cancel
}
