#include <gtest/gtest.h>

#include <userver/utils/datetime.hpp>

#include "chain_busy_driver.hpp"

TEST(ChainBusyDriver, Correction) {
  const auto now = utils::datetime::Now();
  const auto future = now + std::chrono::seconds{60};
  const auto past = now - std::chrono::seconds{60};
  candidates::models::ChainSettings settings;
  settings.pax_exchange_time = 120;

  models::ChainBusyDriver chain;
  chain.left_time = 100;
  chain.left_dist = 200;
  EXPECT_EQ(chain.GetCorrectedLeftTime(future), 100);
  EXPECT_EQ(chain.GetCorrectedLeftDistance(future), 200);
  EXPECT_EQ(models::chain::GetCorrectedRouteTime(std::chrono::seconds{5}, chain,
                                                 settings, future)
                .count(),
            225);
  EXPECT_EQ(models::chain::GetCorrectedRouteDistance(5, chain, future), 205);

  chain.timestamp = now;
  EXPECT_EQ(chain.GetCorrectedLeftTime(future), 40);
  EXPECT_EQ(chain.GetCorrectedLeftDistance(future), 80);
  EXPECT_EQ(models::chain::GetCorrectedRouteTime(std::chrono::seconds{5}, chain,
                                                 settings, future)
                .count(),
            165);
  EXPECT_EQ(models::chain::GetCorrectedRouteDistance(5, chain, future), 85);

  EXPECT_EQ(chain.GetCorrectedLeftTime(past), 100);
  EXPECT_EQ(chain.GetCorrectedLeftDistance(past), 200);
  EXPECT_EQ(models::chain::GetCorrectedRouteTime(std::chrono::seconds{5}, chain,
                                                 settings, past)
                .count(),
            225);
  EXPECT_EQ(models::chain::GetCorrectedRouteDistance(5, chain, past), 205);
}
