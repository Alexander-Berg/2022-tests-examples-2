#include "helper/datetime.hpp"

#include <gtest/gtest.h>

TEST(Datetime, MustParsePickerFormat) {
  EXPECT_NO_THROW(helpers::datetime::Parse("2020-11-09T13:22:30"));
}

TEST(Datetime, MustParseStandardFormats) {
  EXPECT_NO_THROW(helpers::datetime::Parse("2020-11-09T13:22:30Z"));
  EXPECT_NO_THROW(helpers::datetime::Parse("2020-11-09T13:22:30-00"));
  EXPECT_NO_THROW(helpers::datetime::Parse("2020-11-09T13:22:30+03"));
  EXPECT_NO_THROW(helpers::datetime::Parse("2020-11-09T13:22:30-00:00"));
  EXPECT_NO_THROW(helpers::datetime::Parse("2020-11-09T13:22:30+03:00"));
  EXPECT_NO_THROW(helpers::datetime::Parse("2020-11-09T13:22:30-0000"));
  EXPECT_NO_THROW(helpers::datetime::Parse("2020-11-09T13:22:30+0300"));
}

TEST(Datetime, FromPickerFormat_MustProduceRfc3339StringInMoscowZone) {
  const auto tp = helpers::datetime::Parse("2020-11-09T13:22:30");
  const auto str = helpers::datetime::ToString(tp);
  ASSERT_EQ(str, "2020-11-09T13:22:30+03:00");
}

TEST(Datetime, FromStandardFormat_MustProduceRfc3339StringInMoscowZone) {
  const auto tp = helpers::datetime::Parse("2020-11-09T13:22:30+06:00");
  const auto str = helpers::datetime::ToString(tp);
  ASSERT_EQ(str, "2020-11-09T10:22:30+03:00");
}
