#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/driver_protocol_config.hpp>

TEST(TestDriverProtocolConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::DriverProtocol& driver_protocol_config =
      config.Get<config::DriverProtocol>();
  ASSERT_EQ(driver_protocol_config.driver_check_enabled, true);
  ASSERT_EQ(
      driver_protocol_config.driver_weariness_status_free_no_wove_time.Get()
          .count(),
      10u);
  ASSERT_EQ(driver_protocol_config.driver_check_config_3_0_enabled, false);
  ASSERT_EQ(driver_protocol_config.driver_weariness_work_rest_enabled, false);
  ASSERT_EQ(
      driver_protocol_config.driver_weariness_work_rest_time.Get().count(),
      480u);
  ASSERT_EQ(driver_protocol_config.driver_time_format_by_locale[boost::none],
            "%Y-%m-%d %H:%M");
  ASSERT_EQ(
      driver_protocol_config.client_geo_sharing_max_accuracy.GetMap().size(),
      1u);
  ASSERT_EQ(driver_protocol_config.client_geo_sharing_max_accuracy.GetDefault(),
            999999u);
  ASSERT_EQ(
      driver_protocol_config.client_geo_sharing_location_ttl_seconds.Get(),
      120);
  ASSERT_EQ(driver_protocol_config.info_bulk_threads.Get(), 5u);
  ASSERT_EQ(driver_protocol_config.info_bulk_request_max_driver.Get(), 100u);
  ASSERT_EQ(driver_protocol_config.supported_daily_guarantee_tags.Get().size(),
            1u);
  ASSERT_EQ(driver_protocol_config.supported_daily_guarantee_tags.Get().count(
                "steps"),
            1u);
  ASSERT_EQ(driver_protocol_config
                .min_taximeter_version_support_all_daily_guarantee.major,
            9u);
  ASSERT_EQ(driver_protocol_config
                .min_taximeter_version_support_all_daily_guarantee.minor,
            77u);
  ASSERT_EQ(
      driver_protocol_config.taximeter_news_read_max_number_days.Get().count(),
      30u);
}
