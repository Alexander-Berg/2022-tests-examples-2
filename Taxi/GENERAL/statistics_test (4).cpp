#include <userver/utest/utest.hpp>

#include <array>

#include <fmt/format.h>

#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <taxi_config/variables/SURGE_CALCULATOR_CANDIDATES_STATS_HOSTNAME_PATTERN.hpp>
#include <taxi_config/variables/SURGE_CALCULATOR_CANDIDATES_STATS_TARIFFS.hpp>
#include <taxi_config/variables/SURGE_CALCULATOR_CANDIDATES_STATS_TARIFF_ZONES.hpp>
#include <taxi_config/variables/SURGE_CALCULATOR_STATS_AGGREGATION_WINDOWS.hpp>

#include <resources/count_by_categories/impl/statistics_impl.hpp>

using namespace std::chrono_literals;

using clients::candidates::Counter;
using clients::candidates::count_by_categories::post::Response;
using resources::count_by_categories::impl::StatisticsImpl;

namespace {

static const auto now = utils::datetime::Stringtime("2019-01-01T12:00:00+0000");

dynamic_config::StorageMock DefaultConfig() {
  return {{taxi_config::SURGE_CALCULATOR_CANDIDATES_STATS_TARIFF_ZONES,
           {"moscow", "spb"}},
          {taxi_config::SURGE_CALCULATOR_CANDIDATES_STATS_TARIFFS,
           {"econom", "business"}},
          {taxi_config::SURGE_CALCULATOR_STATS_AGGREGATION_WINDOWS,
           {1min, 5min, 15min, 60min}},
          {taxi_config::SURGE_CALCULATOR_CANDIDATES_STATS_HOSTNAME_PATTERN,
           ".+?-(stable|pre-stable).*\\.example\\.net"}};
}

void Store(StatisticsImpl& stats, const std::string& tariff_zone,
           const std::string& tariff, const std::string& hostname, int total) {
  Response resp;
  resp.x_yataxi_server_hostname = hostname;
  resp.generic.extra[tariff].total = total;
  stats.Store(tariff_zone, resp);
}

}  // namespace

UTEST(Statistics, AverageByHostGroup) {
  utils::datetime::MockNowSet(now);
  const auto config = DefaultConfig();
  StatisticsImpl stats(config.GetSource());
  for (int ihostname = 0; ihostname < 2; ++ihostname) {
    for (int irequest = 0; irequest < 10; ++irequest) {
      Store(stats, "moscow", "econom",
            fmt::format("service-stable-{}.example.net", ihostname),
            10 * ihostname + irequest);
    }
  }
  utils::datetime::MockSleep(61s);
  auto res = stats.ToJson();
  EXPECT_EQ(95,
            res["stable"]["moscow"]["econom"]["1min"]["total"].As<int64_t>());
  EXPECT_EQ(95,
            res["stable"]["moscow"]["econom"]["5min"]["total"].As<int64_t>());
  EXPECT_EQ(95,
            res["stable"]["moscow"]["econom"]["15min"]["total"].As<int64_t>());
  EXPECT_EQ(95,
            res["stable"]["moscow"]["econom"]["60min"]["total"].As<int64_t>());
}

UTEST(Statistics, AverageByHostGroup2) {
  utils::datetime::MockNowSet(now);
  const auto config = DefaultConfig();
  StatisticsImpl stats(config.GetSource());
  Store(stats, "moscow", "econom", "service-stable-01.example.net", 10);
  Store(stats, "moscow", "business", "service-stable-01.example.net", 10);
  Store(stats, "spb", "econom", "service-stable-01.example.net", 10);
  Store(stats, "spb", "business", "service-stable-01.example.net", 10);
  Store(stats, "moscow", "econom", "service-stable-02.example.net", 10);
  Store(stats, "moscow", "business", "service-stable-02.example.net", 10);
  Store(stats, "spb", "econom", "service-stable-02.example.net", 10);
  Store(stats, "spb", "business", "service-stable-02.example.net", 10);
  utils::datetime::MockSleep(61s);
  auto res = stats.ToJson();
  EXPECT_EQ(10,
            res["stable"]["moscow"]["econom"]["1min"]["total"].As<int64_t>());
  EXPECT_EQ(10,
            res["stable"]["moscow"]["business"]["1min"]["total"].As<int64_t>());
  EXPECT_EQ(10, res["stable"]["spb"]["econom"]["1min"]["total"].As<int64_t>());
  EXPECT_EQ(10,
            res["stable"]["spb"]["business"]["1min"]["total"].As<int64_t>());
}

UTEST(Statistics, GroupByHostGroup) {
  utils::datetime::MockNowSet(now);
  const auto config = DefaultConfig();
  StatisticsImpl stats(config.GetSource());
  std::array hostnames = {"service-testing-01.example.net",
                          "service-stable-01.example.net",
                          "service-stable-02.example.net",
                          "service-stable-03.example.net",
                          "service-stable-04.example.net",
                          "service-pre-stable-01.example.net",
                          "service-pre-stable-02.example.net",
                          "service-prestable-01.example.net",
                          "010sjvjaj10sl01.foo.ba-r.example.net"};
  for (const auto& hostname : hostnames) {
    Store(stats, "moscow", "econom", hostname, 10);
  }
  utils::datetime::MockSleep(61s);
  auto res = stats.ToJson();
  EXPECT_EQ(10,
            res["stable"]["moscow"]["econom"]["1min"]["total"].As<int64_t>());
  EXPECT_EQ(
      10, res["pre-stable"]["moscow"]["econom"]["1min"]["total"].As<int64_t>());
  EXPECT_EQ(
      10,
      res["service-testing-01.example.net"]["moscow"]["econom"]["1min"]["total"]
          .As<int64_t>());
  EXPECT_EQ(10, res["service-prestable-01.example.net"]["moscow"]["econom"]
                   ["1min"]["total"]
                       .As<int64_t>());
  EXPECT_EQ(10, res["010sjvjaj10sl01.foo.ba-r.example.net"]["moscow"]["econom"]
                   ["1min"]["total"]
                       .As<int64_t>());
}
