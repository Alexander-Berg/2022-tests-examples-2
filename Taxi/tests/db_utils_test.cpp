#include <gtest/gtest.h>

#include <views/db/detail/utils.hpp>

using devicenotify::views::db::detail::MakeOneLineSql;

TEST(DeviceNotifyDbUtils, OneLineSql) {
  EXPECT_EQ(MakeOneLineSql(""), "");
  EXPECT_EQ(MakeOneLineSql("1"), "1");
  EXPECT_EQ(MakeOneLineSql("\n1"), " 1");
  EXPECT_EQ(MakeOneLineSql("1\n"), "1 ");
  EXPECT_EQ(MakeOneLineSql("1\n\n"), "1  ");
  EXPECT_EQ(MakeOneLineSql("1\n2\n3"), "1 2 3");
}
