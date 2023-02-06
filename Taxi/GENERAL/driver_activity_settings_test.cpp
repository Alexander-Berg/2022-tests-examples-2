#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/driver_activity_settings.hpp>

namespace {

const std::unordered_map<std::string,
                         std::unordered_map<std::string, std::string>>
    kExpectedHistoryConfig{
        {
            "order",
            std::unordered_map<std::string, std::string>{
                {"auto_reorder", "driveractivity.cancel_ride"},
                {"park_cancel", "driveractivity.cancel_ride"},
                {"user_cancel", "driveractivity.cancel_ride"},
                {"park_fail", "driveractivity.cancel_ride"},
                {"complete", "driveractivity.complete_ride"},
                {"reject_manual", "driveractivity.pass_ride"},
                {"reject_auto_cancel", "driveractivity.pass_ride"},
                {"reject_missing_tariff", "driveractivity.pass_ride"},
                {"offer_timeout", "driveractivity.pass_ride"},
                {"seen_timeout", "driveractivity.pass_ride"},
                {"reject_bad_position", "driveractivity.pass_ride"},
                {"reject_wrong_way", "driveractivity.pass_ride"},
                {"reject_seen_impossible", "driveractivity.pass_ride"},
            },
        },
    };

}

TEST(TestDriverActivitySettings, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& driver_activity_settings = config.Get<config::Activity>();
  ASSERT_EQ(driver_activity_settings.driver_activity_track_zoom,
            (std::uint8_t)13);
  ASSERT_EQ(driver_activity_settings.driver_activity_required_track_size,
            (std::uint16_t)20);
  ASSERT_EQ(driver_activity_settings.fetch_by_unique_driver_id, false);

  const auto& activity_history =
      driver_activity_settings.driver_events_to_show_in_activity_history
          .GetMap();

  ASSERT_EQ(activity_history.size(), static_cast<size_t>(1));
  for (const auto& [event_type, event_mappings] : kExpectedHistoryConfig) {
    ASSERT_TRUE(activity_history.find(event_type) != activity_history.end());

    const auto& mappings = activity_history.at(event_type).GetMap();
    for (const auto& [event_desc_type, tanker_key] : event_mappings) {
      ASSERT_TRUE(mappings.find(event_desc_type) != mappings.end());
      ASSERT_TRUE(mappings.at(event_desc_type) == tanker_key);
    }
  }
}
