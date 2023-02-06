#include <gtest/gtest.h>

#include <utils/time.hpp>

namespace hejmdal {

TEST(TestTime, TestParseDurationPostfix) {
  EXPECT_EQ(time::ParseDuration("1s"), time::Seconds{1});
  EXPECT_EQ(time::ParseDuration("1m"), time::Minutes{1});
  EXPECT_EQ(time::ParseDuration("1h"), time::Hours{1});
  EXPECT_EQ(time::ParseDuration("1d"), time::Hours{24});
  EXPECT_EQ(time::ParseDuration("1w"), time::Weeks{1});
  EXPECT_EQ(time::ParseDuration("1W"), time::Hours{24 * 7});
}

TEST(TestTime, TestParseDurationComposite) {
  auto d = time::ParseDuration("1d7h15m");
  EXPECT_EQ(d, time::Days{1} + time::Hours{7} + time::Minutes{15});
  d = time::ParseDuration("365d");
  EXPECT_EQ(d, time::Days{365});
  d = time::ParseDuration("1d 7h 31m");
  EXPECT_EQ(d, time::Days{1} + time::Hours{7} + time::Minutes{31});
}

TEST(TestTime, TestParseDurationErrors) {
  EXPECT_ANY_THROW(time::ParseDuration("1y"));
  EXPECT_ANY_THROW(time::ParseDuration("1"));
  EXPECT_ANY_THROW(time::ParseDuration("dd"));
  EXPECT_ANY_THROW(time::ParseDuration(""));
  EXPECT_ANY_THROW(time::ParseDuration("hello"));
  EXPECT_ANY_THROW(time::ParseDuration("-2d"));
  EXPECT_ANY_THROW(time::ParseDuration("d21m"));
  EXPECT_ANY_THROW(time::ParseDuration("3d23"));
  EXPECT_ANY_THROW(time::ParseDuration("3 d"));
}

TEST(TestTime, TestDurationToString) {
  EXPECT_EQ(time::DurationToString(time::Seconds{1}), "1s");
  EXPECT_EQ(time::DurationToString(time::Minutes{2}), "2m");
  EXPECT_EQ(time::DurationToString(time::Hours{3}), "3h");
  EXPECT_EQ(time::DurationToString(time::Days{4}), "4d");
  EXPECT_EQ(time::DurationToString(time::Weeks{5}), "5w");
  EXPECT_EQ(time::DurationToString(time::Days{1} + time::Hours{7} +
                                   time::Minutes{15}),
            "1d7h15m");
  EXPECT_EQ(time::DurationToString(
                time::Days{1} + time::Hours{7} + time::Minutes{15}, ":"),
            "1d:7h:15m");
  EXPECT_EQ(time::DurationToString(
                time::Days{1} + time::Minutes{7} + time::Seconds{15}, ", "),
            "1d, 7m, 15s");
  EXPECT_EQ(time::DurationToString(time::Minutes{7}, ", "), "7m");
}

}  // namespace hejmdal
