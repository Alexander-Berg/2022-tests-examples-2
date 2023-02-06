#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include "driver_check_settings.hpp"

TEST(TestDriverCheckSettings, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& driver_check_settings = config.Get<config::DriverCheck>();
  ASSERT_EQ(driver_check_settings.driver_license_blacklisted_info_url.Get(),
            "https://driver.yandex/"
            "%D0%BF%D0%BE%D1%87%D0%B5%D0%BC%D1%83-%D0%BC%D0%B5%D0%BD%D1%8F-%D0%"
            "B7%D0%B0%D0%B1%D0%BB%D0%BE%D0%BA%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%"
            "BB%D0%B8");
  ASSERT_EQ(driver_check_settings.blacklisted_support_url.Get(),
            "taximeter://screen/support");
}
