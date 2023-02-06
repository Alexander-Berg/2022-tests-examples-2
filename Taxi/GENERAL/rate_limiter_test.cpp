#include "rate_limiter.hpp"
#include "common.hpp"

#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

class Request {
 public:
  Request(const std::string& resource, int quota,
          std::chrono::seconds interval = std::chrono::seconds(1)) {
    request_.resource = resource;
    request_.limit = 100;
    request_.minimal_quota = 10;
    request_.requested_quota = quota;
    request_.interval = interval;
  }
  Request& Burst(int burst) {
    request_.burst = burst;
    return *this;
  }
  Request& IncreaseStep(int step) {
    request_.max_increase_step = step;
    return *this;
  }
  Request& ClientInfo(const std::optional<std::string>& client_id,
                      int avg_usage) {
    client_id_ = client_id;
    request_.client_info = {avg_usage};
    return *this;
  }
  handlers::RpsQuotasRequest Make() {
    return {{std::move(request_)}, client_id_};
  }

 private:
  std::optional<std::string> client_id_ = "test_client";
  handlers::RpsQuotaRequest request_;
};

statistics::LimiterSettings AddExtraQuotaInfo(const std::string& service = "",
                                              int max_percent = 0,
                                              int intervals_count = 0,
                                              int percentile = 100) {
  statistics::LimiterSettings limiters_settings;
  std::unordered_map<std::string, statistics::SettingForLimiter> settings;
  settings[service].extra_quota_settings.emplace(
      statistics::ExtraQuotaSettings{});
  settings[service].extra_quota_settings->intervals_count = intervals_count;
  settings[service].extra_quota_settings->maximum_percentage_of_limit =
      max_percent;
  settings[service].extra_quota_settings->percentile_of_usage_at_intervals =
      percentile;
  settings[dynamic_config::kValueDictDefaultName].extra_quota_settings =
      std::nullopt;
  limiters_settings.settings_for_limiters.emplace(std::move(settings));
  return limiters_settings;
}

UTEST(RateLimiter, BurstExpiration) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  statistics::RateLimiter rate_limiter(dynamic_config::GetDefaultSource());

  auto response = rate_limiter.GetQuotas(
      "test-service", Request("test", 150).Burst(300).Make());
  // take whole limit + 50 from burst budget
  EXPECT_EQ(response.quotas[0].assigned_quota, 150);

  // restore 50 units in common budget, burst is not restored (150)
  utils::datetime::MockSleep(std::chrono::milliseconds(500));

  response = rate_limiter.GetQuotas("test-service",
                                    Request("test", 100).Burst(300).Make());
  // take whole limit (50) + 50 from burst budget, burst budget is 100 now
  EXPECT_EQ(response.quotas[0].assigned_quota, 100);

  // restore 50 units in common budget. Burst budget expires now (0),
  // because intervals_to_burst_expire (1 second) passed
  utils::datetime::MockSleep(std::chrono::milliseconds(500));

  response = rate_limiter.GetQuotas("test-service",
                                    Request("test", 100).Burst(300).Make());
  // take whole limit (50) and there is nothing in burst buduget to take
  EXPECT_EQ(response.quotas[0].assigned_quota, 50);

  // restore full budget (100), burst budget is still expired
  utils::datetime::MockSleep(std::chrono::seconds(5));
  response = rate_limiter.GetQuotas("test-service",
                                    Request("test", 200).Burst(300).Make());
  // take whole limit (100) and there is nothing in burst buduget to take
  EXPECT_EQ(response.quotas[0].assigned_quota, 100);
}

UTEST(RateLimiter, IncreaseLimiterStart) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  statistics::RateLimiter rate_limiter(dynamic_config::GetDefaultSource());

  // smoothly increase current rps from 0 to 100 with step = 10
  auto host_usage = 0;
  for (auto i = 1; i < 11; i++) {
    auto response = rate_limiter.GetQuotas("test-service",
                                           Request("test", 200)
                                               .IncreaseStep(10)
                                               .ClientInfo("host1", host_usage)
                                               .Make());
    EXPECT_EQ(response.quotas.size(), 1);
    // limited by increase limiter
    EXPECT_EQ(response.quotas[0].assigned_quota, 10 * i);
    host_usage += 10;

    // reached increase limit for this interval, receive zero quota
    response = rate_limiter.GetQuotas("test-service",
                                      Request("test", 200)
                                          .IncreaseStep(10)
                                          .ClientInfo("host1", host_usage)
                                          .Make());
    EXPECT_EQ(response.quotas.size(), 1);
    // limited by increase limiter
    EXPECT_EQ(response.quotas[0].assigned_quota, 0);

    utils::datetime::MockSleep(std::chrono::seconds(1));
  }

  // reached resource limit, can't get more than 100
  auto response = rate_limiter.GetQuotas("test-service",
                                         Request("test", 200)
                                             .IncreaseStep(10)
                                             .ClientInfo("host1", host_usage)
                                             .Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 100);

  response = rate_limiter.GetQuotas("test-service",
                                    Request("test", 200)
                                        .IncreaseStep(10)
                                        .ClientInfo("host1", host_usage)
                                        .Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 0);
}

UTEST(RateLimiter, IncreaseLimiterStatisticsRestart) {
  // simulate case when statistics service has been restarted. There is no data
  // about current increase limit level yet, but hosts send their usage. So
  // service shall adjust it's limit to real client usage and do not cut of
  // their requests
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  statistics::RateLimiter rate_limiter(dynamic_config::GetDefaultSource());

  // Real usage on host1 is 30rps, so increase limiter adjusts it's statistics
  // to real usage: 30. Give host usage + step = 40 units
  auto response = rate_limiter.GetQuotas(
      "test-service",
      Request("test", 100).IncreaseStep(10).ClientInfo("host1", 30).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 40);

  for (const auto& host : {"host2", "host3", "host4"}) {
    // other client send their real usage: 20rps, so increase limiter
    // statistics is adjusted again
    auto response = rate_limiter.GetQuotas(
        "test-service",
        Request("test", 100).IncreaseStep(10).ClientInfo(host, 20).Make());
    // we can give quota equal to their last usage only, because increase step
    // on this interval has already been spent
    EXPECT_EQ(response.quotas[0].assigned_quota, 20);

    // can't assign more quota to the host, limited by increase limiter
    response = rate_limiter.GetQuotas(
        "test-service",
        Request("test", 100).IncreaseStep(10).ClientInfo(host, 40).Make());
    EXPECT_EQ(response.quotas[0].assigned_quota, 0);
  }

  // whole budget (100) has already been spent, send 0 for the 5th host
  response = rate_limiter.GetQuotas(
      "test-service",
      Request("test", 100).IncreaseStep(10).ClientInfo("host5", 20).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 0);
}

UTEST(RateLimiter, IncreaseLimiterTrafficStopsAndStartsAgain) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  statistics::RateLimiter rate_limiter(dynamic_config::GetDefaultSource());

  // smoothly increase usage on all hosts from 0 to 100 units
  std::unordered_map<std::string, int> host_usage;
  int step = 10;
  auto requested_quota = 25;
  for (auto i = 1; i < 11; i++) {
    auto budget = i * step;
    for (const auto& host : {"host1", "host2", "host3", "host4"}) {
      auto response = rate_limiter.GetQuotas(
          "test-service", Request("test", requested_quota)
                              .IncreaseStep(step)
                              .ClientInfo(host, host_usage[host])
                              .Make());
      auto assigned = std::min(budget, requested_quota);
      EXPECT_EQ(response.quotas[0].assigned_quota, assigned);
      budget -= assigned;
      host_usage[host] = assigned;
    }
    utils::datetime::MockSleep(std::chrono::seconds(1));
  }

  // sleep for 10 seconds shall reset inrease limiter
  utils::datetime::MockSleep(std::chrono::seconds(10));
  // traffic increase is limited once again
  auto response = rate_limiter.GetQuotas(
      "test-service",
      Request("test", 100).IncreaseStep(step).ClientInfo("host1", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 10);
  response = rate_limiter.GetQuotas(
      "test-service",
      Request("test", 100).IncreaseStep(step).ClientInfo("host2", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 0);
}

UTEST(RateLimiter, IncreaseLimiterChangeStep) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  statistics::RateLimiter rate_limiter(dynamic_config::GetDefaultSource());

  auto response = rate_limiter.GetQuotas(
      "test-service",
      Request("test", 100).IncreaseStep(10).ClientInfo("host1", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 10);
  response = rate_limiter.GetQuotas(
      "test-service",
      Request("test", 100).IncreaseStep(10).ClientInfo("host2", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 0);

  // change increase step 10 -> 20, quota can be assigned
  response = rate_limiter.GetQuotas(
      "test-service",
      Request("test", 100).IncreaseStep(20).ClientInfo("host2", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 10);

  utils::datetime::MockSleep(std::chrono::seconds(1));

  response = rate_limiter.GetQuotas(
      "test-service",
      Request("test", 10).IncreaseStep(20).ClientInfo("host1", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 10);
  // change increase step 20 -> 5. Since we gave 20 units on the prev second and
  // step is 5 now, we can assign only 15 for this interval (because host1 has
  // already taken 10 units)
  response = rate_limiter.GetQuotas(
      "test-service",
      Request("test", 100).IncreaseStep(5).ClientInfo("host2", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 15);

  utils::datetime::MockSleep(std::chrono::seconds(1));

  // Assigned 25 units on the last interval, now we can give 30
  response = rate_limiter.GetQuotas(
      "test-service",
      Request("test", 100).IncreaseStep(5).ClientInfo("host2", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 30);
}

UTEST(RateLimiter, IncreaseLimiterIntervalInBufferChange) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  statistics::LimiterSettings limiters_settings;
  limiters_settings.rate_limiter.intervals_in_increase_limiter_buffer = 10;

  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::STATISTICS_LIMITERS_SETTINGS, limiters_settings}});

  statistics::RateLimiter rate_limiter(storage.GetSource());

  auto response = rate_limiter.GetQuotas(
      "test-service",
      Request("test", 100).IncreaseStep(10).ClientInfo("host1", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 10);

  limiters_settings.rate_limiter.intervals_in_increase_limiter_buffer = 100;
  storage.Extend(
      {{taxi_config::STATISTICS_LIMITERS_SETTINGS, limiters_settings}});

  utils::datetime::MockSleep(std::chrono::seconds(20));

  // although 20 seconds have passed, usage from the first call is not erased
  // yet, because buffer was resized to store 100 intervals and old value is
  // preserved
  response = rate_limiter.GetQuotas(
      "test-service",
      Request("test", 100).IncreaseStep(10).ClientInfo("host1", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 20);
}

UTEST(RateLimiter, ExtraQuotaCalculatorBufferClearing) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  auto limiters_settings = AddExtraQuotaInfo("test-service", 80, 20);

  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::STATISTICS_LIMITERS_SETTINGS, limiters_settings}});

  statistics::RateLimiter rate_limiter(storage.GetSource());

  for (int i = 0; i < 10; ++i) {
    rate_limiter.GetQuotas("test-service",
                           Request("test", 20).ClientInfo("host1", 0).Make());
    rate_limiter.GetQuotas("test-service",
                           Request("test", 20).ClientInfo("host2", 0).Make());
    utils::datetime::MockSleep(std::chrono::seconds(1));
  }
  for (int i = 0; i < 10; ++i) {
    rate_limiter.GetQuotas("test-service",
                           Request("test", 10).ClientInfo("host3", 0).Make());
    rate_limiter.GetQuotas("test-service",
                           Request("test", 40).ClientInfo("host4", 0).Make());
    utils::datetime::MockSleep(std::chrono::seconds(1));
  }
  utils::datetime::MockSleep(std::chrono::seconds(12));
  auto response = rate_limiter.GetQuotas(
      "test-service", Request("test", 10).ClientInfo("host3", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 40);
  utils::datetime::MockSleep(std::chrono::seconds(30));
  for (int i = 0; i < 19; ++i) {
    for (int j = 1; j < 2; ++j) {
      response = rate_limiter.GetQuotas(
          "test-service",
          Request("test", 5).ClientInfo("host" + std::to_string(j), 0).Make());
      EXPECT_EQ(response.quotas[0].assigned_quota, 5);
    }
    utils::datetime::MockSleep(std::chrono::seconds(1));
  }
  response = rate_limiter.GetQuotas(
      "test-service", Request("test", 10).ClientInfo("host2", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 40);
}

UTEST(RateLimiter, ExtraQuotaCalculatorChangeIntervalsCount) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  auto limiters_settings = AddExtraQuotaInfo("test-service", 80, 4);

  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::STATISTICS_LIMITERS_SETTINGS, limiters_settings}});

  statistics::RateLimiter rate_limiter(storage.GetSource());
  for (int i = 3; i >= 1; --i) {
    for (int j = 1; j <= 2; ++j) {
      std::string clien_id = "host" + std::to_string(i);
      auto response = rate_limiter.GetQuotas(
          "test-service",
          Request("test", i * j * 5 + 10).ClientInfo(clien_id, 0).Make());
      EXPECT_EQ(response.quotas[0].assigned_quota, i * j * 5 + 10);
    }
    utils::datetime::MockSleep(std::chrono::seconds(1));
  }
  auto response = rate_limiter.GetQuotas(
      "test-service", Request("test", 10).ClientInfo("host3", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 26);

  limiters_settings = AddExtraQuotaInfo("test-service", 80, 6);

  storage.Extend(
      {{taxi_config::STATISTICS_LIMITERS_SETTINGS, limiters_settings}});

  utils::datetime::MockSleep(std::chrono::seconds(1));

  response = rate_limiter.GetQuotas(
      "test-service", Request("test", 10).ClientInfo("host3", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 10);
  utils::datetime::MockSleep(std::chrono::seconds(1));
  response = rate_limiter.GetQuotas(
      "test-service", Request("test", 10).ClientInfo("host1", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 26);

  limiters_settings = AddExtraQuotaInfo("test-service", 80, 3);

  storage.Extend(
      {{taxi_config::STATISTICS_LIMITERS_SETTINGS, limiters_settings}});

  utils::datetime::MockSleep(std::chrono::seconds(1));
  response = rate_limiter.GetQuotas(
      "test-service", Request("test", 45).ClientInfo("host1", 0).Make());
}

UTEST(RateLimiter, ExtraQuotaCalculatorChangeMaxPercentOfLimit) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  auto limiters_settings = AddExtraQuotaInfo("test-service", 80, 2);

  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::STATISTICS_LIMITERS_SETTINGS, limiters_settings}});

  statistics::RateLimiter rate_limiter(storage.GetSource());

  auto response = rate_limiter.GetQuotas(
      "test-service", Request("test", 10).ClientInfo("host1", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 10);
  utils::datetime::MockSleep(std::chrono::seconds(1));

  response = rate_limiter.GetQuotas(
      "test-service", Request("test", 20).ClientInfo("host2", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 40);
  utils::datetime::MockSleep(std::chrono::seconds(1));

  limiters_settings = AddExtraQuotaInfo("test-service", 50, 2);

  storage.Extend(
      {{taxi_config::STATISTICS_LIMITERS_SETTINGS, limiters_settings}});

  response = rate_limiter.GetQuotas(
      "test-service", Request("test", 10).ClientInfo("host1", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 25);
}

UTEST(RateLimiter, ExtraQuotaCalculatorDisabling) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  auto limiters_settings = AddExtraQuotaInfo("test-service", 80, 2);

  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::STATISTICS_LIMITERS_SETTINGS, limiters_settings}});

  statistics::RateLimiter rate_limiter(storage.GetSource());

  for (int i = 0; i < 2; ++i) {
    auto response = rate_limiter.GetQuotas(
        "test-service", Request("test", 10).ClientInfo("host1", 0).Make());
    utils::datetime::MockSleep(std::chrono::seconds(1));
  }

  storage.Extend(
      {{taxi_config::STATISTICS_LIMITERS_SETTINGS, AddExtraQuotaInfo()}});

  auto response = rate_limiter.GetQuotas(
      "test-service", Request("test", 10).ClientInfo("host1", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 10);
}

UTEST(RateLimiter, ExtraQuotaChangeIntervalLength) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  auto limiters_settings = AddExtraQuotaInfo("test-service", 80, 2);

  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::STATISTICS_LIMITERS_SETTINGS, limiters_settings}});

  statistics::RateLimiter rate_limiter(storage.GetSource());

  for (int i = 0; i < 2; ++i) {
    auto response = rate_limiter.GetQuotas(
        "test-service", Request("test", 10, std::chrono::seconds(i + 1))
                            .ClientInfo("host1", 0)
                            .Make());
    EXPECT_EQ(response.quotas[0].assigned_quota, 10);
    utils::datetime::MockSleep(std::chrono::seconds(1));
  }
}

UTEST(RateLimiter, ExtraQuotaChangePercentileOfUsage) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);
  auto storage = dynamic_config::MakeDefaultStorage({});
  statistics::RateLimiter rate_limiter(storage.GetSource());
  std::vector<std::pair<int, int>> params = {{80, 10}, {33, 35}};
  for (const auto& [percentile, expected] : params) {
    auto limiters_settings =
        AddExtraQuotaInfo("test-service", 70, 4, percentile);
    storage.Extend(
        {{taxi_config::STATISTICS_LIMITERS_SETTINGS, limiters_settings}});
    std::vector<std::pair<int, int>> requests = {{30, 20}, {40, 10}, {80, 2}};
    for (const auto& [req1, req2] : requests) {
      rate_limiter.GetQuotas(
          "test-service", Request("test", req1).ClientInfo("host1", 0).Make());
      rate_limiter.GetQuotas(
          "test-service", Request("test", req2).ClientInfo("host2", 0).Make());
      utils::datetime::MockSleep(std::chrono::seconds(1));
    }
    auto response = rate_limiter.GetQuotas(
        "test-service", Request("test", 10).ClientInfo("host2", 0).Make());
    EXPECT_EQ(response.quotas[0].assigned_quota, expected);
    utils::datetime::MockSleep(std::chrono::seconds(10));
  }
}

UTEST(RateLimiter, ExtraQuotaNotEnoughToGive) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  auto limiters_settings = AddExtraQuotaInfo("test-service", 60, 2);
  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::STATISTICS_LIMITERS_SETTINGS, limiters_settings}});

  statistics::RateLimiter rate_limiter(storage.GetSource());

  rate_limiter.GetQuotas("test-service",
                         Request("test", 20).ClientInfo("host1", 0).Make());
  rate_limiter.GetQuotas("test-service",
                         Request("test", 20).ClientInfo("host2", 0).Make());

  utils::datetime::MockSleep(std::chrono::seconds(1));

  rate_limiter.GetQuotas("test-service",
                         Request("test", 20).ClientInfo("host1", 0).Make());
  auto response = rate_limiter.GetQuotas(
      "test-service", Request("test", 5).ClientInfo("host1", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 5);

  response = rate_limiter.GetQuotas(
      "test-service", Request("test", 20).ClientInfo("host2", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 25);
  response = rate_limiter.GetQuotas(
      "test-service", Request("test", 5).ClientInfo("host2", 0).Make());
  EXPECT_EQ(response.quotas[0].assigned_quota, 5);
}

UTEST(RateLimiter, ExtraQuotaWithEmptyClients) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  auto limiters_settings = AddExtraQuotaInfo("test-service", 60, 3);
  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::STATISTICS_LIMITERS_SETTINGS, limiters_settings}});

  statistics::RateLimiter rate_limiter(storage.GetSource());
  rate_limiter.GetQuotas("test-service",
                         Request("test", 20).ClientInfo("host2", 0).Make());
  utils::datetime::MockSleep(std::chrono::seconds(1));
  rate_limiter.GetQuotas(
      "test-service", Request("test", 20).ClientInfo(std::nullopt, 0).Make());
  utils::datetime::MockSleep(std::chrono::seconds(1));
  auto response = rate_limiter.GetQuotas(
      "test-service", Request("test", 20).ClientInfo("host1", 0).Make());

  EXPECT_EQ(response.quotas[0].assigned_quota, 20);
}
