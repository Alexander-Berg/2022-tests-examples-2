#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/taximeter_polling_power_policy_delays.hpp>

TEST(TaximeterPollingPowerPolicyDelays, Parse) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& taximeter_polling_delays =
      config.Get<config::TaximeterPollingPowerPolicyDelays>();
  const auto& ps_delays = taximeter_polling_delays.Get("/driver/polling/state");
  ASSERT_EQ(300, ps_delays.full);
  ASSERT_EQ(1200, ps_delays.extra.at("powersaving"));
  ASSERT_EQ(1200, ps_delays.extra.at("background"));
  ASSERT_EQ(1800, ps_delays.extra.at("idle"));

  const auto& sh_delays =
      taximeter_polling_delays.Get("/driver/polling/shmorder");
  ASSERT_EQ(600, sh_delays.full);
  ASSERT_EQ(1200, sh_delays.extra.at("powersaving"));
  ASSERT_EQ(1200, sh_delays.extra.at("background"));
  ASSERT_EQ(1800, sh_delays.extra.at("idle"));
}
