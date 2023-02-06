#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include "driver_polling_state_config.hpp"

TEST(TaximeterFnsSelfEmploymentMenuSettings, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& settings = config.Get<config::DriverPollingState>()
                             .taximeter_fns_self_employment_menu_settings;

  ASSERT_FALSE(settings.enable);
  ASSERT_TRUE(settings.cities.empty());
  ASSERT_TRUE(settings.countries.empty());
  ASSERT_TRUE(settings.park_ids.empty());
  ASSERT_TRUE(settings.disabled_park_ids.empty());
}

TEST(IsDriverEmploymentEnabled, EmptyLists) {
  using namespace config;

  DriverPollingState::TaximeterFnsSelfEmploymentMenuSettings settings;
  ASSERT_FALSE(
      IsDriverEmploymentEnabled(settings, "park_id", "city", "country"));

  settings.enable = true;
  ASSERT_TRUE(
      IsDriverEmploymentEnabled(settings, "park_id", "city", "country"));
}

TEST(IsDriverEmploymentEnabled, NotEmptyLists) {
  using namespace config;

  DriverPollingState::TaximeterFnsSelfEmploymentMenuSettings settings;
  settings.enable = true;
  settings.countries = std::unordered_set<std::string>{"country1"};
  settings.cities = std::unordered_set<std::string>{"city1"};
  settings.park_ids = std::unordered_set<std::string>{"park1"};
  settings.disabled_park_ids = std::unordered_set<std::string>{"disabled_park"};

  ASSERT_FALSE(IsDriverEmploymentEnabled(settings, "disabled_park", "city1",
                                         "country1"));

  ASSERT_TRUE(IsDriverEmploymentEnabled(settings, "other_park", "other_city",
                                        "country1"));

  ASSERT_TRUE(IsDriverEmploymentEnabled(settings, "other_park", "city1",
                                        "other_country"));

  ASSERT_TRUE(IsDriverEmploymentEnabled(settings, "park1", "other_city",
                                        "other_country"));

  ASSERT_FALSE(IsDriverEmploymentEnabled(settings, "other_park", "other_city",
                                         "other_country"));
}
