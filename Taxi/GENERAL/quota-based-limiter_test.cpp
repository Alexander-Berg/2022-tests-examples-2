#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <statistics-rps-limiter/quota-based-limiter.hpp>

#include <clients/statistics/client_mock_base.hpp>
#include <userver/engine/condition_variable.hpp>
#include <userver/engine/mutex.hpp>
#include <userver/engine/sleep.hpp>
#include <userver/utils/async.hpp>

#include <deque>
#include <functional>
#include <iostream>

using namespace clients::statistics;
using namespace statistics_rps_limiter;
using namespace statistics_rps_limiter::quota_based_limiter;

using ResourceRequests = std::deque<clients::statistics::RpsQuotaRequest>;
using QuotaRequests = std::unordered_map<std::string, ResourceRequests>;

const auto kRequestTimeout = std::chrono::milliseconds(100);
const auto kClientId = "test_client_id";

std::pair<std::string, clients::statistics::RpsQuotaRequest> MakeRequest(
    const std::string& resource, int quota, int burst = 100,
    std::chrono::seconds interval = std::chrono::seconds(1), int limit = 100,
    int minimal_quota = 10,
    std::optional<int> max_increase_step = std::nullopt) {
  return {resource,
          {resource, limit, minimal_quota, quota, burst, interval,
           max_increase_step, clients::statistics::ClientInfo{0}}};
}

namespace clients::statistics {
// overwrite generated method to avoid avg_usage comparison
bool operator==(const std::optional<clients::statistics::ClientInfo>& lhs,
                const std::optional<clients::statistics::ClientInfo>& rhs) {
  return lhs.has_value() == rhs.has_value();
}
}  // namespace clients::statistics

namespace std {
std::ostream& operator<<(std::ostream& os,
                         const clients::statistics::RpsQuotaRequest& r) {
  return os << "resource: " << r.resource << ", limit: " << r.limit
            << ", minimal quota: " << r.minimal_quota << ", requested quota "
            << r.requested_quota << ", burst: " << r.burst
            << ", interval: " << r.interval.count()
            << (r.max_increase_step ? ", max increase step: " +
                                          std::to_string(*r.max_increase_step)
                                    : "")
            << (r.client_info
                    ? fmt::format(", avg usage: {}", r.client_info->avg_usage)
                    : "");
}
}  // namespace std

class MockStatisticsClient : public clients::statistics::ClientMockBase {
 public:
  ~MockStatisticsClient() {
    if (!quota_requests_.empty()) {
      EXPECT_EQ(quota_requests_, QuotaRequests{});
    }
  }

  v1_rps_quotas::post::Response V1RpsQuotas(
      const v1_rps_quotas::post::Request& request,
      const CommandControl&) const override {
    if (delay_response_) {
      std::unique_lock<engine::Mutex> lock(request_mutex_);
      if (!response_cond_var_.WaitFor(lock, request_timeout_,
                                      [this] { return response_flag_; })) {
        throw std::runtime_error(
            "Response delay shall be manually terminated by "
            "EndResponseDelay()");
      }
      response_flag_ = false;
    }

    if (on_request_callback_) {
      (*on_request_callback_)();
      on_request_callback_.reset();
    }

    EXPECT_TRUE(request.body.client_id);
    EXPECT_EQ(*request.body.client_id, kClientId);

    RpsQuotasResponse response;
    {
      std::unique_lock<engine::Mutex> lock(mutex_);
      for (const auto& req : request.body.requests) {
        auto budget = budgets_.find(req.resource);
        // use explicitly set budget if it exists
        if (budget != budgets_.end()) {
          auto quota = std::min(budget->second, req.requested_quota);
          if (extra_quota_percent_) {
            quota =
                std::max(quota, budget->second * (*extra_quota_percent_) / 100);
          }
          budget->second -= quota;
          response.quotas.push_back({req.resource, quota});
        } else {
          // mirror incoming quota request if budget is not set
          response.quotas.push_back({req.resource, req.requested_quota});
        }
        quota_requests_[req.resource].push_back(req);
      }
    }
    cond_var_.NotifyOne();

    if (statistics_is_down_) {
      throw std::runtime_error("simulate statistics service failure");
    }

    return v1_rps_quotas::post::Response{response};
  }

  void SetBudget(const std::string& resource, int budget) {
    budgets_[resource] = budget;
  }

  void SetExtraQuota(int extra_quota_) {
    extra_quota_percent_.emplace(extra_quota_);
  }

  void DelayResponses(bool flag) { delay_response_ = flag; }

  void SetServerFailure(bool flag) { statistics_is_down_ = flag; }

  void SetRequestTimeout(std::chrono::milliseconds ms) {
    request_timeout_ = ms;
  }

  void EndResponseDelay() {
    {
      std::unique_lock<engine::Mutex> lock(request_mutex_);
      response_flag_ = true;
    }
    response_cond_var_.NotifyAll();
  }

  void WaitForCall(
      const std::unordered_map<
          std::string, clients::statistics::RpsQuotaRequest>& requests) const {
    std::unique_lock<engine::Mutex> lock(mutex_);
    for (const auto& [resource, request] : requests) {
      if (quota_requests_.empty()) {
        if (!cond_var_.WaitFor(lock, std::chrono::seconds(1),
                               [this] { return !quota_requests_.empty(); })) {
          throw std::runtime_error("No request for quotas");
        }
      }
      auto req_it = quota_requests_.find(resource);
      if (req_it == quota_requests_.end()) {
        throw std::runtime_error("No request for resource " + resource);
      }

      EXPECT_TRUE(!req_it->second.empty());
      EXPECT_EQ(request, req_it->second.front());
      req_it->second.pop_front();
      if (req_it->second.empty()) {
        quota_requests_.erase(resource);
      }
    }
  }

  void WaitForCall(int quota, int burst = 100,
                   std::chrono::seconds interval = std::chrono::seconds(1),
                   int limit = 100, int minimal_quota = 10,
                   std::optional<int> max_increase_step = std::nullopt) {
    WaitForCall({MakeRequest("test", quota, burst, interval, limit,
                             minimal_quota, max_increase_step)});
  }

  void CheckNoCall() const {
    engine::SleepFor(std::chrono::milliseconds(10));
    std::unique_lock<engine::Mutex> lock(mutex_);
    EXPECT_EQ(quota_requests_, QuotaRequests{});
  }

  void DropAllRequests() const {
    std::unique_lock<engine::Mutex> lock(mutex_);
    quota_requests_.clear();
  }

  void SetOnRequestCallback(std::function<void()> callback) {
    on_request_callback_ = callback;
  }

 private:
  mutable QuotaRequests quota_requests_;
  mutable engine::Mutex mutex_;
  mutable engine::ConditionVariable cond_var_;
  mutable std::unordered_map<std::string, int> budgets_;
  std::optional<std::chrono::milliseconds> sleep_time_;
  std::optional<int> extra_quota_percent_ = std::nullopt;
  mutable bool delay_response_ = false;
  mutable bool response_flag_ = false;
  mutable bool statistics_is_down_ = false;
  mutable std::optional<std::function<void()>> on_request_callback_;
  mutable std::chrono::milliseconds request_timeout_ = kRequestTimeout;
  mutable engine::Mutex request_mutex_;
  mutable engine::ConditionVariable response_cond_var_;
};

StaticConfig MakeConfig() {
  StaticConfig config;
  config.service = "test-service";
  config.client_id = kClientId;
  return config;
}

RuntimeConfig MakeRuntimeConfig() {
  RuntimeConfig config;
  config.counter_intervals = kDefaultCounterIntervals;
  config.fallback_quota_min_events = 30;
  config.fallback_quota_multiplier = 1.5;
  config.fallback_quota_supplement = 5;
  config.concurrent_refresh_attempts = 3;
  config.disable_limiting = false;
  config.minimal_quota = 10;
  config.reject_time = std::chrono::milliseconds(850);
  config.fallback_reject_time = std::chrono::milliseconds(1000);
  config.wait_request_duration = std::chrono::milliseconds(200);
  return config;
}

QuotaBasedRpsLimiter CreateLimiter(const MockStatisticsClient& client) {
  return {client, engine::current_task::GetTaskProcessor(), MakeConfig(),
          MakeRuntimeConfig()};
}

UTEST(QuotaBasedRpsLimiter, GetPermissionForRequests) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  limiter.UpdateRpsLimit("test", {100});
  EXPECT_EQ(limiter.AcquireQuota("test", 50), 50);
  // local quota is empty, request it
  statistics.WaitForCall(50);
  // it's empty again. Since whole quota has been spent,
  // request new one in background
  statistics.WaitForCall(50);

  utils::datetime::MockNowSet(now + std::chrono::seconds(1));

  EXPECT_EQ(limiter.AcquireQuota("test", 50), 50);
  // request in background
  statistics.WaitForCall(50);

  utils::datetime::MockNowSet(now + std::chrono::seconds(2));

  EXPECT_EQ(limiter.AcquireQuota("test", 30), 30);
  statistics.CheckNoCall();

  // not enough quota, return the rest of it and request new one
  EXPECT_EQ(limiter.AcquireQuota("test", 50), 20);
  // average rps for 3 seconds
  statistics.WaitForCall(60);

  // enough to give 50, no request will be made
  EXPECT_EQ(limiter.AcquireQuota("test", 50), 50);
  statistics.CheckNoCall();
}

UTEST(QuotaBasedRpsLimiter, ReturnUnusedRequests) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  limiter.UpdateRpsLimit("test", {100});
  EXPECT_EQ(limiter.AcquireQuota("test", 50), 50);
  // initial quota + background request
  statistics.WaitForCall(50);
  statistics.WaitForCall(50);

  utils::datetime::MockNowSet(now + std::chrono::seconds(1));

  EXPECT_EQ(limiter.AcquireQuota("test", 30), 30);
  limiter.ReturnQuota("test", 10);
  statistics.CheckNoCall();
  EXPECT_EQ(limiter.AcquireQuota("test", 30), 30);
  // We've returned back 10 requests, they are not still accounted
  // in rps counter
  statistics.WaitForCall(50);

  limiter.ReturnQuota("test", 1000);
  // You can't get more than a limit
  EXPECT_EQ(limiter.AcquireQuota("test", 200), 100);
  // we still have 100 units in local budget
  EXPECT_EQ(limiter.AcquireQuota("test", 200), 100);
  statistics.WaitForCall(100);

  limiter.ReturnQuota("non_existing_resource", 228);
  EXPECT_EQ(limiter.AcquireQuota("non_existing_resource", 100500,
                                 statistics_rps_limiter::RpsLimiter::kAllow),
            100500);
}

UTEST(QuotaBasedRpsLimiter, BurstAndIntervalSettings) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  statistics_rps_limiter::RpsLimiter::LimitData limit;
  limit.limit = 100;
  limit.burst = 150;
  limit.interval = std::chrono::seconds(10);
  limiter.UpdateRpsLimit("test", std::move(limit));
  EXPECT_TRUE(limiter.CheckCanSendRequest("test"));
  statistics.WaitForCall(1, 150, std::chrono::seconds(10));
  // background call
  statistics.WaitForCall(1, 150, std::chrono::seconds(10));

  auto limiter2 = CreateLimiter(statistics);
  // wrong settings: burst < limit
  statistics_rps_limiter::RpsLimiter::LimitData limit2;
  limit2.limit = 120;
  limit2.burst = 50;
  limiter2.UpdateRpsLimit("test", std::move(limit2));
  EXPECT_TRUE(limiter2.CheckCanSendRequest("test"));
  // burst is set equal to limit, interval is set default
  statistics.WaitForCall(1, 120, std::chrono::seconds(1), 120);
  // background call
  statistics.WaitForCall(1, 120, std::chrono::seconds(1), 120);

  // wrong settings: interval = 0
  statistics_rps_limiter::RpsLimiter::LimitData limit3;
  limit3.limit = 120;
  limit3.interval = std::chrono::seconds(0);
  EXPECT_THROW(limiter2.UpdateRpsLimit("test", std::move(limit3)),
               statistics_rps_limiter::BadLimitSettings);
}

UTEST(QuotaBasedRpsLimiter, IntervalIndependentQuotaRequest) {
  for (auto i : {1, 5, 10}) {
    auto interval = std::chrono::seconds(i);
    auto now = std::chrono::system_clock::now();
    utils::datetime::MockNowSet(now);

    MockStatisticsClient statistics;
    statistics.SetBudget("test", 0);
    auto limiter = CreateLimiter(statistics);

    statistics_rps_limiter::RpsLimiter::LimitData limit;
    limit.limit = 200;
    limit.interval = interval;
    limiter.UpdateRpsLimit("test", std::move(limit));

    EXPECT_FALSE(limiter.AcquireQuota("test", 199));
    statistics.DropAllRequests();

    utils::datetime::MockSleep(std::chrono::seconds(9));

    EXPECT_FALSE(limiter.CheckCanSendRequest("test"));
    // Interval doesn't affect quota size that we request from server.
    // Since requests are made every second, desired quota is average rps
    statistics.WaitForCall(200 / 10, 200, interval, 200);
  }
}

UTEST(QuotaBasedRpsLimiter, IntervalIndependentSleepTime) {
  for (auto i : {1, 5, 10}) {
    auto interval = std::chrono::seconds(i);
    auto now = std::chrono::system_clock::now();
    utils::datetime::MockNowSet(now);

    MockStatisticsClient statistics;
    statistics.SetBudget("test", 3);
    auto limiter = CreateLimiter(statistics);

    statistics_rps_limiter::RpsLimiter::LimitData limit;
    limit.limit = 200;
    limit.interval = interval;
    limiter.UpdateRpsLimit("test", std::move(limit));

    // gets quota = 3
    EXPECT_TRUE(limiter.CheckCanSendRequest("test"));
    statistics.WaitForCall(1, 200, interval, 200);
    // background call
    statistics.WaitForCall(1, 200, interval, 200);

    EXPECT_TRUE(limiter.CheckCanSendRequest("test"));
    // gets quota = 1, no budget left
    statistics.WaitForCall(2, 200, interval, 200);
    EXPECT_TRUE(limiter.CheckCanSendRequest("test"));
    // gets quota = 0, shall reject now
    statistics.WaitForCall(3, 200, interval, 200);
    statistics.CheckNoCall();

    statistics.SetBudget("test", 3);

    utils::datetime::MockSleep(std::chrono::milliseconds(500));
    // still is not allowed to request quota
    EXPECT_FALSE(limiter.CheckCanSendRequest("test"));
    statistics.CheckNoCall();

    utils::datetime::MockSleep(std::chrono::milliseconds(850));
    // reject time has passed, successfully request and use quota
    EXPECT_TRUE(limiter.CheckCanSendRequest("test"));
    statistics.DropAllRequests();
  }
}

UTEST(QuotaBasedRpsLimiter, CounterResize) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  MockStatisticsClient statistics;
  statistics.SetBudget("test", 0);
  auto limiter = CreateLimiter(statistics);

  statistics_rps_limiter::RpsLimiter::LimitData limit;
  limit.limit = 2000;
  limiter.UpdateRpsLimit("test", std::move(limit));

  EXPECT_FALSE(limiter.AcquireQuota("test", 2000));
  statistics.DropAllRequests();

  statistics_rps_limiter::RpsLimiter::LimitData limit2;
  limit2.limit = 100;
  limit2.interval = std::chrono::seconds(200);
  limiter.UpdateRpsLimit("test", std::move(limit2));
  EXPECT_FALSE(limiter.CheckCanSendRequest("test"));

  // we have set new interval - 200 seconds, counter is resized
  utils::datetime::MockSleep(std::chrono::seconds(150));
  EXPECT_FALSE(limiter.CheckCanSendRequest("test"));
  // events from previous calls are preserved although 150 seconds have passed
  // ceil(2002 requests / 151 seconds) = 14 avg rps
  statistics.WaitForCall(14, 100, std::chrono::seconds(200));
}

UTEST(QuotaBasedRpsLimiter, NoRequestsToNonusedQuota) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  statistics_rps_limiter::RpsLimiter::LimitData limit1;
  limit1.limit = 100;
  limiter.UpdateRpsLimit("test1", std::move(limit1));
  statistics_rps_limiter::RpsLimiter::LimitData limit2;
  limit2.limit = 100;
  limiter.UpdateRpsLimit("test2", std::move(limit2));

  EXPECT_TRUE(limiter.CheckCanSendRequest("test1"));
  // initial request + background
  statistics.WaitForCall({MakeRequest("test1", 1)});
  statistics.WaitForCall({MakeRequest("test1", 1)});

  statistics.CheckNoCall();

  EXPECT_TRUE(limiter.CheckCanSendRequest("test2"));
  // initial request + background
  statistics.WaitForCall({MakeRequest("test2", 1)});
  statistics.WaitForCall({MakeRequest("test2", 1)});

  statistics.CheckNoCall();

  EXPECT_TRUE(limiter.CheckCanSendRequest("test1"));
  statistics.WaitForCall({MakeRequest("test1", 2)});
  // quota for test2 resource shall not be refreshed,
  // since last received quota remains untouched
  statistics.CheckNoCall();
}

UTEST(QuotaBasedRpsLimiter, MaxIncreaseStep) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  auto wait_for_call = [&statistics](int quota, int max_increase_step) {
    statistics.WaitForCall(quota, 100, std::chrono::seconds{1}, 100, 10,
                           max_increase_step);
  };

  {
    statistics_rps_limiter::RpsLimiter::LimitData limit_data;
    limit_data.limit = 100;
    limit_data.max_increase_step = 10;
    limiter.UpdateRpsLimit("test", std::move(limit_data));
  }
  EXPECT_EQ(limiter.AcquireQuota("test", 50), 50);
  wait_for_call(50, 10);
  wait_for_call(50, 10);
  {
    statistics_rps_limiter::RpsLimiter::LimitData limit_data;
    limit_data.limit = 100;
    limit_data.max_increase_step = 13;
    limiter.UpdateRpsLimit("test", std::move(limit_data));
  }
  utils::datetime::MockNowSet(now + std::chrono::seconds(1));
  EXPECT_EQ(limiter.AcquireQuota("test", 50), 50);
  wait_for_call(50, 13);
}

UTEST(QuotaBasedRpsLimiter, BulkAssign) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  limiter.UpdateRpsLimit("limit1", {0});
  EXPECT_EQ(limiter.AcquireQuota("limit1", 50), 0);
  // no limit, allow
  EXPECT_EQ(limiter.AcquireQuota("limit2", 50), 50);

  {
    using LimitData = statistics_rps_limiter::RpsLimiter::LimitData;
    std::unordered_map<std::string, LimitData> limits_map;
    limits_map.emplace("limit2", LimitData{0});
    limiter.AssignLimits(std::move(limits_map));
  }

  EXPECT_EQ(limiter.AcquireQuota("limit1", 50), 50);
  EXPECT_EQ(limiter.AcquireQuota("limit2", 50), 0);
  statistics.DropAllRequests();
}

UTEST(QuotaBasedRpsLimiter, BulkAssignTemplate) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  using LimitData = statistics_rps_limiter::RpsLimiter::LimitData;
  LimitData limit{0};
  limit.is_regex = true;

  limiter.UpdateRpsLimit(R"(/handler1/\w+)", std::move(limit));
  EXPECT_EQ(limiter.AcquireQuota("/handler1/test", 50), 0);
  // no limit, allow
  EXPECT_EQ(limiter.AcquireQuota("/handler2/test", 50), 50);

  {
    limit = LimitData{0};
    limit.is_regex = true;
    std::unordered_map<std::string, LimitData> rules_map;
    rules_map.emplace(R"(/handler2/\w+)", std::move(limit));
    // implicitly erase rule1
    limiter.AssignLimits(std::move(rules_map));
  }

  EXPECT_EQ(limiter.AcquireQuota("/handler1/test_test", 50), 50);
  EXPECT_EQ(limiter.AcquireQuota("/handler2/test_test", 50), 0);
  statistics.DropAllRequests();
}

UTEST(QuotaBasedRpsLimiter, SeveralRequestsWaitForQuotaRefresh) {
  auto now = std::chrono::system_clock::now();
  // throw away milliseconds to simplify desired quota calculation
  now = std::chrono::floor<std::chrono::seconds>(now);
  utils::datetime::MockNowSet(now);

  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  statistics_rps_limiter::RpsLimiter::LimitData limit;
  limit.limit = 100;
  limiter.UpdateRpsLimit("test", std::move(limit));
  statistics.SetBudget("test", 100);
  statistics.SetRequestTimeout(std::chrono::seconds(10000));

  EXPECT_EQ(limiter.AcquireQuota("test", 10), 10);
  // wait for initial + background requests
  // Limiter has 10 units in local budget now
  statistics.WaitForCall({MakeRequest("test", 10)});
  statistics.WaitForCall({MakeRequest("test", 10)});

  statistics.DelayResponses(true);

  // Test checks that client sends more requests if refreshed quota value is
  // too small for all waiting consumers

  auto result1 = ::utils::Async(
      "acquire_quota1", [&limiter] { return limiter.AcquireQuota("test", 5); });

  auto result2 = ::utils::Async(
      "acquire_quota2", [&limiter] { return limiter.AcquireQuota("test", 5); });

  // 1st `AcquireQuota` call takes 5 units.
  // Second call take the rest 5 units and launches
  // background request (since budget on the client side is empty now).
  // Background request hangs forever, because DelayResponses is set
  EXPECT_EQ(result1.Get(), 5);
  EXPECT_EQ(result2.Get(), 5);

  // 3rd call tries to take 5 units too, but sees that budget is
  // empty and request has already been sent to the service. 3rd call waits
  // for wait_request_duration and sees that still there is no quota to fulfill
  // request. 3rd call executes one more request to the service and takes quota
  // needed.
  EXPECT_EQ(limiter.AcquireQuota("test", 5), 5);

  // turn of DelayResponses, so request from 3rd call can is handled
  statistics.DelayResponses(false);
  // advance time so logic can realize that timeout for other request is over
  utils::datetime::MockNowSet(now + std::chrono::milliseconds(250));

  statistics.WaitForCall({MakeRequest("test", 25)});
}

UTEST(QuotaBasedRpsLimiter, CheckAllowStatisticsAfterReturnQuota) {
  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  statistics_rps_limiter::RpsLimiter::LimitData limit;
  limit.limit = 100;
  limiter.UpdateRpsLimit("test", std::move(limit));
  statistics.SetBudget("test", 100);

  EXPECT_EQ(limiter.AcquireQuota("test", 10), 10);
  statistics.WaitForCall({MakeRequest("test", 10)});
  limiter.ReturnQuota("test", 5);

  // background request for 10 units
  statistics.WaitForCall({MakeRequest("test", 10)});

  auto stats = limiter.GetStatistics();
  EXPECT_EQ(stats.quota_requests_failed, 0);
  EXPECT_EQ(stats.resource_stats["test"].rejected, 0);
  EXPECT_EQ(stats.resource_stats["test"].allowed, 5);
  // 10 + background request for additional 10
  EXPECT_EQ(stats.resource_stats["test"].quota_assigned, 20);
  EXPECT_EQ(stats.resource_stats["test"].limit, 100);
  EXPECT_EQ(stats.resource_stats["test"].interval, std::chrono::seconds(1));

  statistics.CheckNoCall();
}

UTEST(QuotaBasedRpsLimiter, CheckAllowStatisticsAfterReturnQuota2) {
  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  statistics_rps_limiter::RpsLimiter::LimitData limit;
  limit.limit = 10;
  limiter.UpdateRpsLimit("test", std::move(limit));
  statistics.SetBudget("test", 100);

  // make request object for easy comparing
  auto request = MakeRequest("test", 10, 10, std::chrono::seconds(1), 10);

  EXPECT_EQ(limiter.AcquireQuota("test", 10), 10);
  statistics.WaitForCall({request});
  // background request for 10 units
  statistics.WaitForCall({request});

  // Now local budget has 10 units and we return 10 back
  limiter.ReturnQuota("test", 10);

  auto stats = limiter.GetStatistics();
  EXPECT_EQ(stats.quota_requests_failed, 0);
  EXPECT_EQ(stats.resource_stats["test"].rejected, 0);
  EXPECT_EQ(stats.resource_stats["test"].allowed, 0);
  // 10 + background request for additional 10
  EXPECT_EQ(stats.resource_stats["test"].quota_assigned, 20);
  EXPECT_EQ(stats.resource_stats["test"].limit, 10);
  EXPECT_EQ(stats.resource_stats["test"].interval, std::chrono::seconds(1));

  // we can't get more than a limit
  EXPECT_EQ(limiter.AcquireQuota("test", 20), 10);
  // no background requests, since we still have 10 units in local budget
  statistics.CheckNoCall();

  // Return whole value back again
  limiter.ReturnQuota("test", 10);

  stats = limiter.GetStatistics();
  EXPECT_EQ(stats.quota_requests_failed, 0);
  EXPECT_EQ(stats.resource_stats["test"].rejected, 0);
  EXPECT_EQ(stats.resource_stats["test"].allowed, 0);
  EXPECT_EQ(stats.resource_stats["test"].quota_assigned, 20);
  EXPECT_EQ(stats.resource_stats["test"].limit, 10);
  EXPECT_EQ(stats.resource_stats["test"].interval, std::chrono::seconds(1));

  statistics.CheckNoCall();
}

UTEST(QuotaBasedRpsLimiter, CheckAssignedStatisticsAfterReturnQuota) {
  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  statistics_rps_limiter::RpsLimiter::LimitData limit;
  limit.limit = 10;
  limiter.UpdateRpsLimit("test", std::move(limit));
  statistics.SetBudget("test", 7);

  statistics.DelayResponses(true);

  auto result = ::utils::Async(
      "acquire_quota", [&limiter] { return limiter.AcquireQuota("test", 10); });
  // allow to fulfill initial request
  statistics.EndResponseDelay();
  EXPECT_EQ(result.Get(), 7);
  statistics.WaitForCall(
      {MakeRequest("test", 10, 10, std::chrono::seconds(1), 10)});
  statistics.SetBudget("test", 10);
  // return 10 quota units
  limiter.ReturnQuota("test", 20);
  // serve background quota request
  statistics.EndResponseDelay();
  statistics.WaitForCall(
      {MakeRequest("test", 10, 10, std::chrono::seconds(1), 10)});

  auto stats = limiter.GetStatistics();
  EXPECT_EQ(stats.quota_requests_failed, 0);
  EXPECT_EQ(stats.resource_stats["test"].rejected, 0);
  EXPECT_EQ(stats.resource_stats["test"].allowed, 7);
  EXPECT_EQ(stats.resource_stats["test"].quota_assigned, 17);
  EXPECT_EQ(stats.resource_stats["test"].limit, 10);
  EXPECT_EQ(stats.resource_stats["test"].interval, std::chrono::seconds(1));
}

UTEST(QuotaBasedRpsLimiter, CheckRejectStatistics) {
  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  statistics_rps_limiter::RpsLimiter::LimitData limit;
  limit.limit = 100;

  limiter.UpdateRpsLimit("test", std::move(limit));
  statistics.SetBudget("test", 0);

  EXPECT_FALSE(limiter.CheckCanSendRequest("test"));
  statistics.WaitForCall({MakeRequest("test", 1)});

  auto stats = limiter.GetStatistics();
  EXPECT_EQ(stats.quota_requests_failed, 0);
  EXPECT_EQ(stats.resource_stats["test"].rejected, 1);
  EXPECT_EQ(stats.resource_stats["test"].allowed, 0);
  EXPECT_EQ(stats.resource_stats["test"].quota_assigned, 0);
  EXPECT_EQ(stats.resource_stats["test"].limit, 100);
  EXPECT_EQ(stats.resource_stats["test"].interval, std::chrono::seconds(1));

  statistics.DropAllRequests();
}

UTEST(QuotaBasedRpsLimiter, CheckRejectStatistics2) {
  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  statistics_rps_limiter::RpsLimiter::LimitData limit;
  limit.limit = 100;

  limiter.UpdateRpsLimit("test", std::move(limit));
  statistics.SetBudget("test", 1);

  // Delay background quota request after initial request
  statistics.SetOnRequestCallback(
      [&statistics] { statistics.DelayResponses(true); });

  EXPECT_TRUE(limiter.CheckCanSendRequest("test"));
  statistics.WaitForCall({MakeRequest("test", 1)});

  // Check if we can send request second time. Function call sees that
  // quota has already been requested and waits for a background request result
  // After that we end response delay and background requests assigns quota = 0
  // to the resource (because budget is empty)
  auto request = ::utils::Async(
      "request", [&limiter] { return limiter.CheckCanSendRequest("test"); });
  ::utils::Async("delay", [&statistics] {
    statistics.EndResponseDelay();
  }).Get();
  EXPECT_FALSE(request.Get());

  auto stats = limiter.GetStatistics();
  EXPECT_EQ(stats.quota_requests_failed, 0);
  EXPECT_EQ(stats.resource_stats["test"].rejected, 1);
  EXPECT_EQ(stats.resource_stats["test"].allowed, 1);
  EXPECT_EQ(stats.resource_stats["test"].quota_assigned, 1);
  EXPECT_EQ(stats.resource_stats["test"].limit, 100);
  EXPECT_EQ(stats.resource_stats["test"].interval, std::chrono::seconds(1));

  statistics.DropAllRequests();
}

UTEST(QuotaBasedRpsLimiter, FallbackQuotaNotEnoughEvents) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  for (const auto& interval_value : {1, 10}) {
    MockStatisticsClient statistics;
    auto limiter = CreateLimiter(statistics);

    const auto interval = std::chrono::seconds(interval_value);
    const auto limit = 100;
    statistics_rps_limiter::RpsLimiter::LimitData data;
    data.limit = limit;
    data.interval = interval;
    limiter.UpdateRpsLimit("test", std::move(data));

    statistics.SetBudget("test", 50);
    EXPECT_EQ(limiter.AcquireQuota("test", 200), 50);
    statistics.WaitForCall(100, limit, interval, limit);
    statistics.WaitForCall(100, limit, interval, limit);

    utils::datetime::MockSleep(std::chrono::seconds(1));

    statistics.SetBudget("test", 40);
    EXPECT_EQ(limiter.AcquireQuota("test", 200), 40);
    statistics.WaitForCall(100, limit, interval, limit);
    // background request, since there is no quota left again
    statistics.WaitForCall(100, limit, interval, limit);

    utils::datetime::MockSleep(std::chrono::seconds(1));

    statistics.SetServerFailure(true);
    // since there is not enough events, fallback quota is calculated
    // using formula:
    // usage: [0, 40, 50], zero is skipped
    // avg * multiplier (1.5) + supplement (5) = 45 * 1.5 + 5 = 78
    EXPECT_EQ(limiter.AcquireQuota("test", 200), 73);
    statistics.WaitForCall(100, limit, interval, limit);
    statistics.WaitForCall(100, limit, interval, limit);
    statistics.CheckNoCall();
  }
}

UTEST(QuotaBasedRpsLimiter, FallbackQuotaCalculation) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  for (const auto& interval_value : {1, 10}) {
    MockStatisticsClient statistics;
    auto runtime_config = MakeRuntimeConfig();
    auto limiter = CreateLimiter(statistics);

    const auto interval = std::chrono::seconds(interval_value);
    const auto limit = 100;
    statistics_rps_limiter::RpsLimiter::LimitData data;
    data.limit = limit;
    data.interval = interval;
    limiter.UpdateRpsLimit("test", std::move(data));

    statistics.SetBudget("test", 50);
    EXPECT_EQ(limiter.AcquireQuota("test", 200), 50);
    statistics.WaitForCall(100, limit, interval, limit);
    statistics.WaitForCall(100, limit, interval, limit);

    for (int i = 0; i < runtime_config.fallback_quota_min_events; ++i) {
      utils::datetime::MockSleep(std::chrono::seconds(1));

      statistics.SetBudget("test", 50);
      EXPECT_EQ(limiter.AcquireQuota("test", 200), 50);
      statistics.WaitForCall(100, limit, interval, limit);
      // background request, since there is no quota left again
      statistics.WaitForCall(100, limit, interval, limit);
    }

    utils::datetime::MockSleep(std::chrono::seconds(1));

    statistics.SetServerFailure(true);
    // we have more than fallback_quota_min_events, quota is
    // calculated using formula:
    // usage: [0, 50, ... , 50]
    // M[x] + 3σ
    EXPECT_EQ(limiter.AcquireQuota("test", 200), 75);
    statistics.WaitForCall(100, limit, interval, limit);
    statistics.WaitForCall(100, limit, interval, limit);

    utils::datetime::MockSleep(std::chrono::seconds(1));
    // take quota again, server is still down. Quota is calculated
    // this way now:
    // usage: [0, 48, 50, ... , 50], zero is skipped
    // ceil(avg * multiplier (1.5) + supplement (5)) = 50 * 1.5 + 5 = 78
    EXPECT_EQ(limiter.AcquireQuota("test", 200), 80);
    statistics.WaitForCall(100, limit, interval, limit);
    statistics.WaitForCall(100, limit, interval, limit);

    // If quota was spent earlier than 1 second passes, request is rejected
    utils::datetime::MockSleep(std::chrono::milliseconds(500));
    EXPECT_EQ(limiter.AcquireQuota("test", 200), 0);
    statistics.CheckNoCall();
  }
}

UTEST(QuotaBasedRpsLimiter, ExplicitlySetMinimalQuota) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  statistics_rps_limiter::RpsLimiter::LimitData data;
  data.limit = 100;
  data.minimal_quota = 20;
  limiter.UpdateRpsLimit("test", std::move(data));

  EXPECT_TRUE(limiter.CheckCanSendRequest("test"));
  auto request = MakeRequest("test", 1);
  request.second.minimal_quota = 20;
  // initial request + background
  statistics.WaitForCall({request});
  statistics.WaitForCall({request});

  auto new_config = MakeRuntimeConfig();
  new_config.minimal_quota = 50;
  limiter.UpdateRuntimeConfig(new_config);

  // Check that runtime config update doesn't overwrite explicitly
  // set minimal quota
  EXPECT_TRUE(limiter.CheckCanSendRequest("test"));
  request = MakeRequest("test", 2);
  request.second.minimal_quota = 20;
  statistics.WaitForCall({request});

  statistics_rps_limiter::RpsLimiter::LimitData data2;
  data2.limit = 100;
  data2.minimal_quota = 30;
  limiter.UpdateRpsLimit("test", std::move(data2));

  EXPECT_TRUE(limiter.CheckCanSendRequest("test"));
  request = MakeRequest("test", 3);
  request.second.minimal_quota = 30;
  statistics.WaitForCall({request});
}

UTEST(QuotaBasedRpsLimiter, DeleteRpsLimit) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);
  statistics.SetBudget("test", 0);

  limiter.UpdateRpsLimit("test", {100});
  EXPECT_FALSE(limiter.CheckCanSendRequest("test"));
  statistics.WaitForCall(1);

  limiter.DeleteRpsLimit("test");
  // no limit, allow request
  EXPECT_TRUE(limiter.CheckCanSendRequest("test"));
  statistics.CheckNoCall();
}

UTEST(QuotaBasedRpsLimiter, RegexResources) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  const std::string regex_handler(R"(/regexp/handler/\w+)");
  statistics.SetBudget(regex_handler, 4);

  statistics_rps_limiter::RpsLimiter::LimitData limit{100};
  limit.is_regex = true;
  limiter.UpdateRpsLimit(regex_handler, std::move(limit));

  EXPECT_TRUE(limiter.CheckCanSendRequest("/regexp/handler/test1"));
  statistics.WaitForCall({MakeRequest(regex_handler, 1)});
  statistics.WaitForCall({MakeRequest(regex_handler, 1)});

  EXPECT_TRUE(limiter.CheckCanSendRequest("/regexp/handler/test2"));
  statistics.WaitForCall({MakeRequest(regex_handler, 2)});

  EXPECT_TRUE(limiter.CheckCanSendRequest("/regexp/handler/test3"));
  // run out of budget, no more requests
  statistics.WaitForCall({MakeRequest(regex_handler, 3)});
  // use last quota unit
  EXPECT_TRUE(limiter.CheckCanSendRequest("/regexp/handler/test4"));
  EXPECT_FALSE(limiter.CheckCanSendRequest("/regexp/handler/test5"));
  statistics.CheckNoCall();

  // no effect, still rejecting
  limiter.DeleteRpsLimit("/regexp/handler/test_test");
  EXPECT_FALSE(limiter.CheckCanSendRequest("/regexp/handler/test_test"));

  // delete pattern and now request is allowed, since there is no limit
  limiter.DeleteRpsLimit(regex_handler);
  EXPECT_TRUE(limiter.CheckCanSendRequest("/regexp/handler/test_test"));
}

UTEST(QuotaBasedRpsLimiter, IncorrectRegex) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  const std::string regex_handler(R"(/regexp/handler/\w+{}\\[])");

  statistics_rps_limiter::RpsLimiter::LimitData limit{100};
  limit.is_regex = true;
  EXPECT_THROW(limiter.UpdateRpsLimit(regex_handler, std::move(limit)),
               statistics_rps_limiter::BadLimitSettings);
}

UTEST(QuotaBasedRpsLimiter, RegexPriorities) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  const std::string regex_handler1(R"(/regexp/handler(/\w+)+)");
  const std::string regex_handler2(R"(/regexp/handler/specific(/\w+)+)");
  statistics.SetBudget(regex_handler1, 100);
  statistics.SetBudget(regex_handler2, 0);

  statistics_rps_limiter::RpsLimiter::LimitData limit1{100};
  limit1.is_regex = true;
  limit1.priority = 1;

  statistics_rps_limiter::RpsLimiter::LimitData limit2{100};
  limit2.is_regex = true;
  limit2.priority = 2;

  limiter.UpdateRpsLimit(regex_handler1, std::move(limit1));
  limiter.UpdateRpsLimit(regex_handler2, std::move(limit2));

  EXPECT_FALSE(limiter.CheckCanSendRequest("/regexp/handler/specific/test"));
  statistics.DropAllRequests();
}

UTEST(QuotaBasedRpsLimiter, AcquireWithStatus) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  const std::string kSimpleHandler = "/simple/handler";
  const std::string kRegexHandler(R"(/regexp/handler(/\w+)+)");
  statistics.SetBudget(kSimpleHandler, 100);
  statistics.SetBudget(kRegexHandler, 100);

  Labels labels1 = {{"label1", "value1"}};
  Labels labels2 = {{"label2", "value2"}};

  statistics_rps_limiter::RpsLimiter::LimitData limit1{100};
  limit1.is_regex = false;
  limit1.labels = labels1;

  statistics_rps_limiter::RpsLimiter::LimitData limit2{100};
  limit2.is_regex = true;
  limit2.labels = labels2;

  limiter.UpdateRpsLimit(kSimpleHandler, std::move(limit1));
  limiter.UpdateRpsLimit(kRegexHandler, std::move(limit2));

  auto result = limiter.AcquireQuotaWithStatus("/simple/handler", 10);
  EXPECT_EQ(result.status, LimitAcquisitionStatus::kAcquired);
  EXPECT_EQ(result.matched_resource, kSimpleHandler);
  EXPECT_EQ(result.is_regexp, false);
  EXPECT_EQ(result.quota, 10);
  EXPECT_EQ(result.labels, labels1);

  result = limiter.AcquireQuotaWithStatus("/regexp/handler/test", 10);
  EXPECT_EQ(result.status, LimitAcquisitionStatus::kAcquired);
  EXPECT_EQ(result.matched_resource, kRegexHandler);
  EXPECT_EQ(result.is_regexp, true);
  EXPECT_EQ(result.quota, 10);
  EXPECT_EQ(result.labels, labels2);

  result = limiter.AcquireQuotaWithStatus("/does-not-exist/", 10);
  EXPECT_EQ(result.status, LimitAcquisitionStatus::kNotFound);
  EXPECT_FALSE(result.matched_resource);
  EXPECT_EQ(result.is_regexp, false);
  EXPECT_EQ(result.quota, 10);
  EXPECT_EQ(result.labels, Labels());

  statistics.DropAllRequests();
}

UTEST(QuotaBasedRpsLimiter, RegexpFlagChange) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  const std::string kHandler = "/simple/handler";
  statistics.SetBudget(kHandler, 100);

  statistics_rps_limiter::RpsLimiter::LimitData limit1{100};
  limit1.is_regex = true;
  limiter.UpdateRpsLimit(kHandler, std::move(limit1));

  auto result = limiter.AcquireQuotaWithStatus("/simple/handler", 10);
  EXPECT_EQ(result.status, LimitAcquisitionStatus::kAcquired);
  EXPECT_EQ(result.matched_resource, kHandler);
  EXPECT_EQ(result.is_regexp, true);
  EXPECT_EQ(result.quota, 10);

  // change regex flag for the limit, now it's simple resource with high
  // priority
  statistics_rps_limiter::RpsLimiter::LimitData limit2{100};
  limit2.is_regex = false;
  limiter.UpdateRpsLimit(kHandler, std::move(limit2));

  statistics_rps_limiter::RpsLimiter::LimitData limit3{100};
  limit3.is_regex = true;
  limiter.UpdateRpsLimit(R"((/\w+)+)", std::move(limit3));

  result = limiter.AcquireQuotaWithStatus("/simple/handler", 10);
  EXPECT_EQ(result.status, LimitAcquisitionStatus::kAcquired);
  EXPECT_EQ(result.matched_resource, kHandler);
  EXPECT_EQ(result.is_regexp, false);
  EXPECT_EQ(result.quota, 10);

  statistics.DropAllRequests();
}

UTEST(QuotaBasedRpsLimiter, MaxRequestDesiredQuotaPolicy) {
  std::vector<std::pair<RuntimeConfig, int>> cases;
  // standard logic: request avg quota = (10 + 5 + 3 + 2) / 4 = 5
  auto runtime_config1 = MakeRuntimeConfig();
  runtime_config1.limiter_settings.request_quota_based_on_max_requests = false;
  cases.push_back({runtime_config1, 5});

  // max request logic: desired quota is max rps (10)
  auto runtime_config2 = MakeRuntimeConfig();
  runtime_config2.limiter_settings.request_quota_based_on_max_requests = true;
  cases.push_back({runtime_config2, 10});

  auto runtime_config3 = MakeRuntimeConfig();
  runtime_config3.limiter_settings.request_quota_based_on_max_requests = false;
  runtime_config3.resource_settings["test"]
      .request_quota_based_on_max_requests = true;
  cases.push_back({runtime_config3, 10});

  for (const auto& [runtime_config, expected_quota] : cases) {
    auto now = std::chrono::system_clock::now();
    utils::datetime::MockNowSet(now);

    MockStatisticsClient statistics;
    auto limiter = CreateLimiter(statistics);
    limiter.UpdateRuntimeConfig(runtime_config);

    limiter.UpdateRpsLimit("test", {100});
    EXPECT_TRUE(limiter.AcquireQuota("test", 10));
    statistics.WaitForCall(10);
    statistics.WaitForCall(10);

    utils::datetime::MockNowSet(now + std::chrono::seconds(1));
    EXPECT_TRUE(limiter.AcquireQuota("test", 5));
    statistics.CheckNoCall();
    utils::datetime::MockNowSet(now + std::chrono::seconds(2));
    EXPECT_TRUE(limiter.AcquireQuota("test", 3));
    statistics.CheckNoCall();
    utils::datetime::MockNowSet(now + std::chrono::seconds(3));
    EXPECT_TRUE(limiter.AcquireQuota("test", 2));
    statistics.WaitForCall(expected_quota);
  }
}

UTEST(QuotaBasedRpsLimiter, ChangedThresholdToRequestQuota) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);
  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);
  auto new_config = MakeRuntimeConfig();
  new_config.threshold_percent_for_quota_request = 10;
  limiter.UpdateRuntimeConfig(new_config);
  limiter.UpdateRpsLimit("test", {100});
  EXPECT_EQ(limiter.AcquireQuota("test", 60), 60);
  statistics.WaitForCall(60);
  statistics.WaitForCall(60);
  utils::datetime::MockNowSet(now + std::chrono::seconds(1));
  EXPECT_EQ(limiter.AcquireQuota("test", 56), 56);
  // there will be quotas for 4 requests
  // desired quota is 58 and 4 < 58 * 0.1
  // new quota will be requested 58 - 4
  statistics.WaitForCall(54);

  utils::datetime::MockNowSet(now + std::chrono::seconds(2));
  new_config.threshold_percent_for_quota_request = 50;
  limiter.UpdateRuntimeConfig(new_config);
  EXPECT_EQ(limiter.AcquireQuota("test", 34), 34);
  statistics.WaitForCall(26);

  utils::datetime::MockNowSet(now + std::chrono::seconds(3));
  EXPECT_EQ(limiter.AcquireQuota("test", 10), 10);
  statistics.CheckNoCall();

  new_config.threshold_percent_for_quota_request = std::nullopt;
  limiter.UpdateRuntimeConfig(new_config);
  utils::datetime::MockNowSet(now + std::chrono::seconds(4));
  EXPECT_EQ(limiter.AcquireQuota("test", 38), 38);
  statistics.CheckNoCall();
}

UTEST(QuotaBasedRpsLimiter, CheckAssignedStatisticsWithExtraQuota) {
  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  statistics_rps_limiter::RpsLimiter::LimitData limit;
  limit.limit = 100;
  limiter.UpdateRpsLimit("test", std::move(limit));
  statistics.SetExtraQuota(90);
  statistics.SetBudget("test", 100);

  statistics.DelayResponses(true);

  auto result = ::utils::Async(
      "acquire_quota", [&limiter] { return limiter.AcquireQuota("test", 20); });
  // allow to fulfill initial request
  statistics.EndResponseDelay();
  EXPECT_EQ(result.Get(), 20);
  statistics.WaitForCall(
      {MakeRequest("test", 20, 100, std::chrono::seconds(1), 100)});

  statistics.DelayResponses(true);

  statistics.SetBudget("test", 100);

  result = ::utils::Async(
      "acquire_quota", [&limiter] { return limiter.AcquireQuota("test", 80); });
  // allow to fulfill initial request
  statistics.EndResponseDelay();
  EXPECT_EQ(result.Get(), 70);
  statistics.WaitForCall(
      {MakeRequest("test", 100, 100, std::chrono::seconds(1), 100)});

  auto stats = limiter.GetStatistics();
  EXPECT_EQ(stats.quota_requests_failed, 0);
  EXPECT_EQ(stats.resource_stats["test"].rejected, 0);
  EXPECT_EQ(stats.resource_stats["test"].allowed, 90);
  EXPECT_EQ(stats.resource_stats["test"].quota_assigned, 190);
  EXPECT_EQ(stats.resource_stats["test"].extra_quota_assigned, 70);
  EXPECT_EQ(stats.resource_stats["test"].limit, 100);
  EXPECT_EQ(stats.resource_stats["test"].interval, std::chrono::seconds(1));
}

UTEST(QuotaBasedRpsLimiter, DisableAllLimits) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  MockStatisticsClient statistics;
  auto limiter = CreateLimiter(statistics);

  limiter.UpdateRpsLimit("test", {100});
  EXPECT_EQ(limiter.AcquireQuota("test", 150), 100);
  statistics.WaitForCall(100);
  statistics.WaitForCall(100);

  auto new_config = MakeRuntimeConfig();
  new_config.disable_limiting = true;
  limiter.UpdateRuntimeConfig(new_config);

  EXPECT_EQ(limiter.AcquireQuota("test", 150), 150);
  statistics.CheckNoCall();

  EXPECT_EQ(limiter.AcquireQuota("non_existing_resource", 150), 150);
  statistics.CheckNoCall();

  new_config.disable_limiting = false;
  limiter.UpdateRuntimeConfig(new_config);

  EXPECT_EQ(limiter.AcquireQuota("test", 50), 50);
  statistics.CheckNoCall();

  new_config.disable_limiting = true;
  limiter.UpdateRuntimeConfig(new_config);

  limiter.UpdateRpsLimit("test", {200});
  limiter.DeleteRpsLimit("test");
  limiter.ReturnQuota("test", 100);
  limiter.AccountExtraQuotaUsed("test", 20);

  new_config.disable_limiting = false;
  limiter.UpdateRuntimeConfig(new_config);

  EXPECT_EQ(limiter.AcquireQuota("test", 60), 50);
  statistics.WaitForCall(100);
}
