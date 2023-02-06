#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/ghost_city_config.hpp>

TEST(TestGhostCityConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& ghost_cities_config = config.Get<config::GhostCities>();

  ASSERT_EQ(0ull, ghost_cities_config.ghost_cities_by_zone.Get().size());
  ASSERT_FALSE(ghost_cities_config.ghost_cities_enabled.Get());
  ASSERT_FALSE(ghost_cities_config.affect_surge.Get());
  ASSERT_FALSE(ghost_cities_config.check_ghost_cities_pin_data.Get());
}

TEST(TestGhostCityConfig, Invalid) {
  const auto conf = R"({
    "moscow": {},
    "spb": {
      "SOME KEY": {}
    }
  })";

  auto docs_map = config::DocsMapForTest();
  docs_map.Override("GHOST_CITIES", mongo::fromjson(conf));
  const auto& config = config::Config(docs_map);
  const auto& ghost_cities_config = config.Get<config::GhostCities>();

  ASSERT_EQ(0ull, ghost_cities_config.ghost_cities_by_zone.Get().size());
}

TEST(TestGhostCityConfig, CityEnabling) {
  const auto conf = R"({
    "moscow": {"EXPERIMENT_NAME":"ghost_moscow"},
    "spb": {
      "ENABLED": true,
      "EXPERIMENT_NAME":"ghost_spb"
    },
    "tver": {
      "ENABLED": false,
      "EXPERIMENT_NAME":"ghost_tver"
    }
  })";

  auto docs_map = config::DocsMapForTest();
  docs_map.Override("GHOST_CITIES", mongo::fromjson(conf));
  docs_map.Override("GHOST_CITIES_ENABLED", true);
  const auto& enabled_config = config::Config(docs_map);
  const std::string tariff_zone_moscow{"moscow"};
  const std::string tariff_zone_spb{"spb"};
  const std::string tariff_zone_tver{"tver"};
  ASSERT_TRUE(boost::none == config::GetUnresolvedGhostCity(tariff_zone_moscow,
                                                            enabled_config));
  ASSERT_FALSE(boost::none ==
               config::GetUnresolvedGhostCity(tariff_zone_spb, enabled_config));
  ASSERT_TRUE(boost::none ==
              config::GetUnresolvedGhostCity(tariff_zone_tver, enabled_config));

  docs_map.Override("GHOST_CITIES_ENABLED", false);
  const auto& disabled_config = config::Config(docs_map);
  ASSERT_TRUE(boost::none == config::GetUnresolvedGhostCity(tariff_zone_moscow,
                                                            disabled_config));
  ASSERT_TRUE(boost::none ==
              config::GetUnresolvedGhostCity(tariff_zone_spb, disabled_config));
  ASSERT_TRUE(boost::none == config::GetUnresolvedGhostCity(tariff_zone_tver,
                                                            disabled_config));
}
