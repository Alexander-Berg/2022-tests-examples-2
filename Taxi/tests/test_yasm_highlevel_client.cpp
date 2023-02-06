#include <gtest/gtest.h>

#include <clients/yasm/yasm_highlevel_client.hpp>

#include <set>

namespace hejmdal {

bool Contains(const std::initializer_list<std::string>& list,
              const std::string& val) {
  for (const auto& list_val : list) {
    if (list_val == val) return true;
  }
  return false;
}

bool ContainsSameValues(const std::set<clients::models::YasmSignal>& signals,
                        const std::initializer_list<std::string>& str_signals) {
  for (const auto& signal : signals) {
    if (!Contains(str_signals, std::string(signal))) return false;
  }
  return true;
}

class TestYasmClient : public clients::YasmClient {
 public:
  clients::YasmRequestsInfo GetSignals(
      std::vector<clients::models::YasmLowLevelRequestPtr>& requests,
      const bool get_latest_data) const override {
    EXPECT_FALSE(get_latest_data);
    requests_ = requests;
    for (auto& req : requests) {
      for (const auto& signal : req->signals) {  // Init empty signals
        req->response.values[signal];
      }
      auto step = time::Seconds(static_cast<int>(req->period));
      auto current = req->interval.GetStart();
      std::size_t counter = 0;
      while (current <= req->interval.GetEnd()) {
        req->response.timeline.push_back(current);
        for (const auto& signal : req->signals) {
          req->response.values[signal].push_back(counter);
        }
        counter++;
        current += step;
      }
    }
    return {requests.size(), 0};
  }

  const std::vector<clients::models::YasmLowLevelRequestPtr>& GetRequests() {
    return requests_;
  }

  bool FindRequest(std::string host, int period, time::TimeRange interval,
                   std::initializer_list<std::string> signals) {
    for (const auto& req : requests_) {
      if (std::string(req->host) != host) continue;
      if ((int)req->period != period) continue;
      if (req->interval != interval) continue;
      if (req->signals.size() != signals.size()) continue;
      if (ContainsSameValues(req->signals, signals)) return true;
    }
    return false;
  }

 private:
  mutable std::vector<clients::models::YasmLowLevelRequestPtr> requests_;
};

static time::Seconds sec = time::Seconds(1);

TEST(TestYasmHighLevelClient, MainTest) {
  auto now = time::Now();

  std::vector<clients::models::YasmSignalRequestPtr> requests;

  auto range1 = time::TimeRange{now, now + 16 * sec};
  auto range2 = time::TimeRange{now, now + 33 * sec};

  requests.push_back(std::make_shared<clients::models::YasmSignalRequest>(
      models::HostName("host1"), clients::models::YasmSignal("signal1"),
      clients::models::YasmSignalPeriod::k5Sec, range1));
  requests.push_back(std::make_shared<clients::models::YasmSignalRequest>(
      models::HostName("host1"), clients::models::YasmSignal("signal1"),
      clients::models::YasmSignalPeriod::k5Sec, range2));
  requests.push_back(std::make_shared<clients::models::YasmSignalRequest>(
      models::HostName("host1"), clients::models::YasmSignal("signal1"),
      clients::models::YasmSignalPeriod::k5Min, range1));
  requests.push_back(std::make_shared<clients::models::YasmSignalRequest>(
      models::HostName("host1"), clients::models::YasmSignal("signal2"),
      clients::models::YasmSignalPeriod::k5Sec, range2));

  requests.push_back(std::make_shared<clients::models::YasmSignalRequest>(
      models::HostName("host2"), clients::models::YasmSignal("signal1"),
      clients::models::YasmSignalPeriod::k5Sec, range2));
  requests.push_back(std::make_shared<clients::models::YasmSignalRequest>(
      models::HostName("host2"), clients::models::YasmSignal("signal1"),
      clients::models::YasmSignalPeriod::k5Sec, range2));

  auto lowlevel_client = std::make_shared<TestYasmClient>();
  auto client = clients::YasmHighLevelClient(lowlevel_client, 1000,
                                             time::Milliseconds(10));

  client.FetchSignalsData(requests);

  {  // Check response timeseries
    for (const auto& req : requests) {
      auto secs =
          time::As<time::Seconds>(req->time_interval.GetDuration()).count();
      auto size = std::floor(secs / (int)req->period) + 1;
      EXPECT_EQ(req->response_time_series.size(), size);
      double counter = 0.;
      auto time = req->time_interval.GetStart();
      for (const auto& sv : req->response_time_series) {
        EXPECT_DOUBLE_EQ(sv.GetValue(), counter);
        EXPECT_EQ(sv.GetTime(), time);
        counter += 1.;
        time += time::Seconds((int)req->period);
      }
    }
  }
  {  // Check lowlevel requests
    const auto& llrequests = lowlevel_client->GetRequests();
    ASSERT_EQ(llrequests.size(), 3);

    EXPECT_TRUE(lowlevel_client->FindRequest("host2", 5, range2, {"signal1"}));
    EXPECT_TRUE(
        lowlevel_client->FindRequest("host1", 300, range1, {"signal1"}));
    EXPECT_TRUE(lowlevel_client->FindRequest("host1", 5, range2,
                                             {"signal1", "signal2"}));
  }
}

TEST(TestYasmHighLevelClient, UnmergeableRequestIntervals) {
  auto now = time::Now();

  std::vector<clients::models::YasmSignalRequestPtr> requests;

  auto range1 = time::TimeRange{now, now + 16 * sec};
  auto range2 = time::TimeRange{now + 14300 * sec, now + 14501 * sec};

  requests.push_back(std::make_shared<clients::models::YasmSignalRequest>(
      models::HostName("host1"), clients::models::YasmSignal("signal1"),
      clients::models::YasmSignalPeriod::k5Sec, range1));
  requests.push_back(std::make_shared<clients::models::YasmSignalRequest>(
      models::HostName("host1"), clients::models::YasmSignal("signal2"),
      clients::models::YasmSignalPeriod::k5Sec, range2));

  auto lowlevel_client = std::make_shared<TestYasmClient>();
  auto client = clients::YasmHighLevelClient(lowlevel_client, 1000,
                                             time::Milliseconds(10));

  client.FetchSignalsData(requests);

  {  // Check response timeseries
    for (const auto& req : requests) {
      auto secs =
          time::As<time::Seconds>(req->time_interval.GetDuration()).count();
      auto size = std::floor(secs / (int)req->period) + 1;
      EXPECT_EQ(req->response_time_series.size(), size);
      double counter = 0.;
      auto time = req->time_interval.GetStart();
      for (const auto& sv : req->response_time_series) {
        EXPECT_DOUBLE_EQ(sv.GetValue(), counter);
        EXPECT_EQ(sv.GetTime(), time);
        counter += 1.;
        time += time::Seconds((int)req->period);
      }
    }
  }
  {  // Check lowlevel requests
    const auto& llrequests = lowlevel_client->GetRequests();
    ASSERT_EQ(llrequests.size(), 2);

    EXPECT_TRUE(lowlevel_client->FindRequest("host1", 5, range1, {"signal1"}));
    EXPECT_TRUE(lowlevel_client->FindRequest("host1", 5, range2, {"signal2"}));
  }
}

TEST(TestYasmHighLevelClient, ValidationTest) {
  auto now = time::Now();
  auto lowlevel_client = std::make_shared<TestYasmClient>();
  auto client = clients::YasmHighLevelClient(lowlevel_client, 1000,
                                             time::Milliseconds(10));

  {
    std::vector<clients::models::YasmSignalRequestPtr> requests;
    auto big_range = time::TimeRange{now, now + 14400 * sec};
    requests.push_back(std::make_shared<clients::models::YasmSignalRequest>(
        models::HostName("host1"), clients::models::YasmSignal("signal1"),
        clients::models::YasmSignalPeriod::k5Sec, big_range));
    client.FetchSignalsData(requests);
    EXPECT_EQ(lowlevel_client->GetRequests().size(), 1);
  }
  {
    std::vector<clients::models::YasmSignalRequestPtr> requests;
    auto too_big_range = time::TimeRange{now, now + 14401 * sec};
    requests.push_back(std::make_shared<clients::models::YasmSignalRequest>(
        models::HostName("host1"), clients::models::YasmSignal("signal1"),
        clients::models::YasmSignalPeriod::k5Sec, too_big_range));
    client.FetchSignalsData(requests);
    EXPECT_EQ(lowlevel_client->GetRequests().size(), 0);
  }
  {
    std::vector<clients::models::YasmSignalRequestPtr> requests;
    auto big_range = time::TimeRange{now, now + 864000 * sec};
    requests.push_back(std::make_shared<clients::models::YasmSignalRequest>(
        models::HostName("host1"), clients::models::YasmSignal("signal1"),
        clients::models::YasmSignalPeriod::k5Min, big_range));
    client.FetchSignalsData(requests);
    EXPECT_EQ(lowlevel_client->GetRequests().size(), 1);
  }
  {
    std::vector<clients::models::YasmSignalRequestPtr> requests;
    auto too_big_range = time::TimeRange{now, now + 864001 * sec};
    requests.push_back(std::make_shared<clients::models::YasmSignalRequest>(
        models::HostName("host1"), clients::models::YasmSignal("signal1"),
        clients::models::YasmSignalPeriod::k5Sec, too_big_range));
    client.FetchSignalsData(requests);
    EXPECT_EQ(lowlevel_client->GetRequests().size(), 0);
  }
}

}  // namespace hejmdal
