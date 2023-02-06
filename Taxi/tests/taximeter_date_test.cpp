#include <userver/utest/utest.hpp>
#include <userver/utils/underlying_value.hpp>

#include <defs/all_definitions.hpp>

const std::string kTaximeterFormat = "%Y-%m-%dT%H:%M:%E*S";

TEST(TaximeterDate, ParseV1) {
  const auto date = utils::datetime::Stringtime(
      "2020-04-14T10:02:02.123456", utils::datetime::kDefaultTimezone,
      kTaximeterFormat);
  EXPECT_EQ(utils::datetime::Timestring(date),
            "2020-04-14T10:02:02.123456+0000");
}
