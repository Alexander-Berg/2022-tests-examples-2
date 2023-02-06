#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include "rate_share_statistics.hpp"

UTEST(RateShareStatistics, Sample) {
  utils::datetime::MockNowSet(
      std::chrono::system_clock::time_point{std::chrono::seconds{1}});

  models::RateShareStatistics stats;
  EXPECT_TRUE(stats.GetRateShare(0, 0).empty());

  stats.SetSamplesCount(2);
  stats.Account({{"/path1", {{"client1", 10}}}},
                {{"/path1", {{"client1", 15}}}});
  EXPECT_TRUE(stats.GetRateShare(0, 0).empty());
  stats.Account({{"/path1", {{"client1", 5}}}},
                {{"/path1", {{"client1", 10}}}});
  EXPECT_EQ(stats.GetRateShare(0, 0),
            (models::RateShare{{"/path1", {{"client1", 60}}}}));

  // first sample should be removed
  stats.Account({{"/path1", {{"client1", 5}}}},
                {{"/path1", {{"client1", 10}}}});
  EXPECT_EQ(stats.GetRateShare(0, 0),
            (models::RateShare{{"/path1", {{"client1", 50}}}}));

  // nothing should be removed
  stats.Cleenup(std::chrono::steady_clock::time_point{std::chrono::seconds{1}});
  EXPECT_EQ(stats.GetRateShare(0, 0),
            (models::RateShare{{"/path1", {{"client1", 50}}}}));

  // everything should be removed
  stats.Cleenup(std::chrono::steady_clock::time_point{std::chrono::seconds{2}});
  EXPECT_TRUE(stats.GetRateShare(0, 0).empty());

  stats.Account({{"/path1", {{"client1", 5}}}},
                {{"/path1", {{"client1", 10}}}});
  stats.Account({{"/path1", {{"client1", 5}}}},
                {{"/path1", {{"client1", 15}}}});
  EXPECT_EQ(stats.GetRateShare(0, 0),
            (models::RateShare{{"/path1", {{"client1", 40}}}}));
  stats.Account({{"/path1", {{"client1", 5}}}},
                {{"/path1", {{"client1", 10000}}}});
  EXPECT_NEAR(stats.GetRateShare(0, 0)["/path1"]["client1"], 0.1, 0.01);

  stats.Account({{"/path1", {{"client1", 5000}}}},
                {{"/path1", {{"client1", 5000}}}});
  EXPECT_NEAR(stats.GetRateShare(2, 15)["/path1"]["client1"], 40, 0.5);
  EXPECT_EQ(stats.GetRateShare(80, 0),
            (models::RateShare{{"/path1", {{"client1", 100}}}}));
}
