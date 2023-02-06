#include <gtest/gtest.h>

#include <set>

#include "models/metrics/sip_user_status_metrics.hpp"
#include "models/sip_user.hpp"

namespace callcenter_queues::unit_tests {

class SipUserStatsTests : public ::testing::Test {};

TEST_F(SipUserStatsTests, TestNull) {
  std::vector<callcenter_queues::models::sip_user::SipUserStats> stats{};
  std::set<std::string> known_queues = {};
  callcenter_queues::models::metrics::SipUserMetricsByQueue metrics{
      known_queues};
  for (const auto& stat : stats) {
    metrics.Account(stat, "_on_");
  }
  EXPECT_EQ(formats::json::ToString(metrics.ToJson().ExtractValue()), "{}");
}
/*
TEST_F(SipUserStatsTests, TestNotNull) {
  std::vector<callcenter_queues::models::sip_user::SipUserStats> stats{
      {"ru_taxi_disp", "19", 41, 0, 10, 1, 33, 0, 7},
      {"ru_taxi_disp", "16", 41, 0, 10, 4, 31, 0, 6},
      {"ru_taxi_disp", "22", 39, 0, 12, 0, 29, 0, 10},
  };
  std::set<std::string> known_queues = {};
  callcenter_queues::models::metrics::SipUserMetricsByQueue metrics{
      known_queues};
  for (const auto& stat : stats) {
    metrics.Account(stat, "_on_");
  }
  EXPECT_EQ(formats::json::ToString(metrics.ToJson().ExtractValue()),
            "{\"ru_taxi_disp_on_22\":{\"status\":{\"paused\":12,\"connected\":"
            "39},\"substatus\":{\"connected\":{\"waiting\":10,\"talking\":29,"
            "\"postcall\":0,\"busy\":0}}},\"$meta\":{\"solomon_children_"
            "labels\":\"call_queue\"},\"ru_taxi_disp_on_16\":{\"status\":{"
            "\"paused\":10,\"connected\":41},\"substatus\":{\"connected\":{"
            "\"waiting\":6,\"talking\":31,\"postcall\":4,\"busy\":0}}},\"ru_"
            "taxi_disp_on_19\":{\"status\":{\"paused\":10,\"connected\":41},"
            "\"substatus\":{\"connected\":{\"waiting\":7,\"talking\":33,"
            "\"postcall\":1,\"busy\":0}}}}");
}
*/
}  // namespace callcenter_queues::unit_tests
