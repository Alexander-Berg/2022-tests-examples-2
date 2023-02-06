#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include "vgw_config.hpp"

TEST(TestVgwConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& vgw_config = config.Get<vgw::config::VoiceGateway>();

  ASSERT_EQ(vgw_config.timeout_ms->count(), 5000);
  ASSERT_EQ(static_cast<int>(vgw_config.min_expiration_seconds), 300);
  ASSERT_EQ(static_cast<int>(vgw_config.new_fwd_expiration_seconds), 900);
  ASSERT_EQ(static_cast<int>(vgw_config.time_after_complete_for_driver_seconds),
            1800);
  ASSERT_EQ(
      static_cast<int>(vgw_config.time_after_complete_for_dispatcher_seconds),
      10800);
  ASSERT_EQ(vgw_config.totw_driver_voice_forwarding_disable_threshold_by_country
                .GetDefault(),
            5u);
  ASSERT_EQ(
      vgw_config.driver_voice_forwarding_disable_tariffs_classes_by_country
          .GetDefault()
          .size(),
      0u);
}
