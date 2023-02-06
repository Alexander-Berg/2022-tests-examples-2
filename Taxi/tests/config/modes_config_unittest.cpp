#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/modes_config.hpp>
#include <utils/jsonfixtures.hpp>

TEST(TestModes, StandardParsingConfig) {
  const auto& zone_modes_parse_bson =
      JSONFixtures::GetFixtureBSON("zone_modes_parse.json");
  config::ValueDict<std::string> map_styles({});
  const auto modes =
      config::ParseModes(zone_modes_parse_bson["MODES"], map_styles);

  ASSERT_EQ(modes.size(), 2u);

  const auto& mode_default = modes[0];
  ASSERT_EQ(mode_default.mode, "default");
  ASSERT_EQ(mode_default.title.get(), "tanker.default_title");

  const auto& mode_sdc = modes[1];
  ASSERT_EQ(mode_sdc.mode, "sdc");
  ASSERT_EQ(mode_sdc.title.get(), "tanker.sdc_title");
}
