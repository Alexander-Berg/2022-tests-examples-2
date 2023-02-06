#include <userver/utest/utest.hpp>

#include <models/datetime.hpp>
#include <testing/taxi_config.hpp>
#include <userver/formats/bson.hpp>

using namespace handlers;
using namespace discmod;
using namespace utils::datetime;

TEST(Datetime, ParseFromString) {
  ASSERT_EQ(DiscountTimeFromString("21:12"), (Time{21, 12}));
  ASSERT_EQ(DiscountTimeFromString("00:59"), (Time{00, 59}));
  EXPECT_THROW(DiscountTimeFromString("00:60"), std::invalid_argument);
  EXPECT_THROW(DiscountTimeFromString("24:00"), std::invalid_argument);
}

TEST(Datetime, TimeCompare) {
  ASSERT_EQ((Time{21, 12}), (Time{21, 12}));
  ASSERT_NE((Time{21, 12}), (Time{21, 10}));
  ASSERT_TRUE((Time{21, 12} > Time{21, 10}));
  ASSERT_TRUE((Time{21, 12} >= Time{21, 10}));
  ASSERT_TRUE((Time{11, 11} < Time{12, 00}));
  ASSERT_TRUE((Time{11, 11} <= Time{12, 00}));
}

TEST(Datetime, Timestring) {
  const std::string str = "2010-01-01T12:00:00";
  EXPECT_NO_THROW(DiscountStringtime(str));
  EXPECT_THROW(DiscountStringtime(str + "+0000"), DateParseError);
  EXPECT_THROW(DiscountStringtime(str + "+00:00"), DateParseError);

  EXPECT_THROW(DiscountStringtime("2010-01-01T12:60:00"), DateParseError);
  EXPECT_THROW(DiscountStringtime("2010-02-29T12:00:00"), DateParseError);
  EXPECT_NO_THROW(DiscountStringtime("2012-02-29T12:00:00.12"));

  const auto dt = DiscountStringtime(str);
  ASSERT_EQ(DiscountTimestring(dt), str);
}
