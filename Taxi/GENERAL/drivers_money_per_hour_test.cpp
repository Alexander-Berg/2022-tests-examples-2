#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/drivers_money_per_hour.hpp>

TEST(TestDriversMoneyPerHour, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& test_config = config.Get<config::DriversMoneyPerHourConfig>();

  ASSERT_FALSE(test_config.supply_hours_enabled.Get());
  ASSERT_EQ(15,
            test_config.supply_hours_minutes_calculation_delay.Get().count());
  ASSERT_EQ(
      60, test_config.supply_hours_max_minutes_between_statuses.Get().count());
}
