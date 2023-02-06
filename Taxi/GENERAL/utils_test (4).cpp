#include <eats-places-availability/utils/utils.hpp>

#include <gtest/gtest.h>

namespace eats_places_availability {

std::ostream& operator<<(std::ostream& os, const TimeInterval& ti) {
  os << "[" << ti.start.time_since_epoch().count() << "; "
     << ti.end.time_since_epoch().count() << "]";

  return os;
}

std::ostream& operator<<(std::ostream& os, const Schedule& schedule) {
  os << "Schedule{";
  for (size_t i = 0; i < schedule.size(); ++i) {
    if (i != 0) {
      os << " ";
    }

    os << schedule[i];
  }
  os << "}";
  return os;
}

}  // namespace eats_places_availability

namespace eats_places_availability::utils {

namespace {

const std::string kRFC3339 = "%Y-%m-%dT%H:%M:%S%Ez";

std::string FormatTime(const std::chrono::system_clock::time_point& time,
                       const cctz::time_zone& tz) {
  return cctz::format(kRFC3339, time, tz);
}

std::chrono::system_clock::time_point CreateTime(
    int y, int m = 1, int d = 1, int hh = 0, int mm = 0, int ss = 0,
    const cctz::time_zone& tz = cctz::utc_time_zone()) {
  return cctz::convert(cctz::civil_second(y, m, d, hh, mm, ss), tz);
}

}  // namespace

TEST(Ceil, Simple) {
  const auto tz = cctz::utc_time_zone();
  {
    const auto actual = CeilToMinutes(CreateTime(2021, 4, 18, 20, 20), 15, tz);
    ASSERT_EQ("2021-04-18T20:30:00+00:00", FormatTime(actual, tz));
  }
  {
    const auto actual = CeilToMinutes(CreateTime(2021, 4, 18, 20, 16), 15, tz);
    ASSERT_EQ("2021-04-18T20:30:00+00:00", FormatTime(actual, tz));
  }
  {
    const auto actual = CeilToMinutes(CreateTime(2021, 4, 18, 20, 59), 15, tz);
    ASSERT_EQ("2021-04-18T21:00:00+00:00", FormatTime(actual, tz));
  }
  {
    const auto actual = CeilToMinutes(CreateTime(2021, 4, 18, 20, 0), 30, tz);
    ASSERT_EQ("2021-04-18T20:00:00+00:00", FormatTime(actual, tz));
  }
  {
    const auto actual =
        CeilToMinutes(CreateTime(2021, 4, 18, 20, 0, 1), 30, tz);
    ASSERT_EQ("2021-04-18T20:30:00+00:00", FormatTime(actual, tz));
  }
  {
    const auto actual =
        CeilToMinutes(CreateTime(2021, 4, 18, 20, 9, 59), 10, tz);
    ASSERT_EQ("2021-04-18T20:10:00+00:00", FormatTime(actual, tz));
  }
}

TEST(Ceil, TimeZones) {
  {
    const auto tz = cctz::fixed_time_zone(std::chrono::minutes(13));
    const auto actual = CeilToMinutes(CreateTime(2021, 4, 18, 20, 20), 15, tz);
    ASSERT_EQ("2021-04-18T20:45:00+00:13", FormatTime(actual, tz));
  }
  {
    const auto tz = cctz::fixed_time_zone(std::chrono::minutes(-8));
    const auto actual = CeilToMinutes(CreateTime(2021, 4, 18, 20, 16), 15, tz);
    ASSERT_EQ("2021-04-18T20:15:00-00:08", FormatTime(actual, tz));
  }
  {
    const auto tz = cctz::fixed_time_zone(std::chrono::minutes(59));
    const auto actual = CeilToMinutes(CreateTime(2021, 4, 18, 20, 59), 15, tz);
    ASSERT_EQ("2021-04-18T22:00:00+00:59", FormatTime(actual, tz));
  }
  {
    const auto tz = cctz::fixed_time_zone(std::chrono::minutes(1));
    const auto actual = CeilToMinutes(CreateTime(2021, 4, 18, 20, 0), 30, tz);
    ASSERT_EQ("2021-04-18T20:30:00+00:01", FormatTime(actual, tz));
  }
  {
    const auto tz = cctz::fixed_time_zone(std::chrono::minutes(30));
    const auto actual =
        CeilToMinutes(CreateTime(2021, 4, 18, 20, 0, 1), 30, tz);
    ASSERT_EQ("2021-04-18T21:00:00+00:30", FormatTime(actual, tz));
  }
  {
    const auto tz = cctz::fixed_time_zone(std::chrono::minutes(10));
    const auto actual =
        CeilToMinutes(CreateTime(2021, 4, 18, 20, 9, 59), 10, tz);
    ASSERT_EQ("2021-04-18T20:20:00+00:10", FormatTime(actual, tz));
  }
}

TEST(Floor, Simple) {
  const auto tz = cctz::utc_time_zone();
  {
    const auto actual = FloorToMinutes(CreateTime(2021, 4, 18, 20, 20), 15, tz);
    ASSERT_EQ("2021-04-18T20:15:00+00:00", FormatTime(actual, tz));
  }
  {
    const auto actual = FloorToMinutes(CreateTime(2021, 4, 18, 20, 16), 15, tz);
    ASSERT_EQ("2021-04-18T20:15:00+00:00", FormatTime(actual, tz));
  }
  {
    const auto actual = FloorToMinutes(CreateTime(2021, 4, 18, 20, 59), 15, tz);
    ASSERT_EQ("2021-04-18T20:45:00+00:00", FormatTime(actual, tz));
  }
  {
    const auto actual = FloorToMinutes(CreateTime(2021, 4, 18, 20, 0), 30, tz);
    ASSERT_EQ("2021-04-18T20:00:00+00:00", FormatTime(actual, tz));
  }
  {
    const auto actual =
        FloorToMinutes(CreateTime(2021, 4, 18, 20, 0, 1), 30, tz);
    ASSERT_EQ("2021-04-18T20:00:00+00:00", FormatTime(actual, tz));
  }
  {
    const auto actual =
        FloorToMinutes(CreateTime(2021, 4, 18, 20, 10, 59), 10, tz);
    ASSERT_EQ("2021-04-18T20:10:00+00:00", FormatTime(actual, tz));
  }
}

TEST(Floor, TimeZones) {
  {
    const auto tz = cctz::fixed_time_zone(std::chrono::minutes(13));
    const auto actual = FloorToMinutes(CreateTime(2021, 4, 18, 20, 20), 15, tz);
    ASSERT_EQ("2021-04-18T20:30:00+00:13", FormatTime(actual, tz));
  }
  {
    const auto tz = cctz::fixed_time_zone(std::chrono::minutes(-8));
    const auto actual = FloorToMinutes(CreateTime(2021, 4, 18, 20, 16), 15, tz);
    ASSERT_EQ("2021-04-18T20:00:00-00:08", FormatTime(actual, tz));
  }
  {
    const auto tz = cctz::fixed_time_zone(std::chrono::minutes(59));
    const auto actual = FloorToMinutes(CreateTime(2021, 4, 18, 20, 59), 15, tz);
    ASSERT_EQ("2021-04-18T21:45:00+00:59", FormatTime(actual, tz));
  }
  {
    const auto tz = cctz::fixed_time_zone(std::chrono::minutes(1));
    const auto actual = FloorToMinutes(CreateTime(2021, 4, 18, 20, 0), 30, tz);
    ASSERT_EQ("2021-04-18T20:00:00+00:01", FormatTime(actual, tz));
  }
  {
    const auto tz = cctz::fixed_time_zone(std::chrono::minutes(30));
    const auto actual =
        FloorToMinutes(CreateTime(2021, 4, 18, 20, 0, 1), 30, tz);
    ASSERT_EQ("2021-04-18T20:30:00+00:30", FormatTime(actual, tz));
  }
  {
    const auto tz = cctz::fixed_time_zone(std::chrono::minutes(10));
    const auto actual =
        FloorToMinutes(CreateTime(2021, 4, 18, 20, 9, 59), 10, tz);
    ASSERT_EQ("2021-04-18T20:10:00+00:10", FormatTime(actual, tz));
  }
}

TEST(Merge, All) {
  using namespace std::literals;
  using Time = std::chrono::system_clock::time_point;

  {
    // lhs     |-------|
    // rhs |-------|
    // res     |---|
    Schedule lhs{{Time{9ms}, Time{15ms}}};
    Schedule rhs{{Time{5ms}, Time{10ms}}};
    auto result = Merge(lhs, rhs);
    Schedule expected{{Time{9ms}, Time{10ms}}};
    EXPECT_EQ(result, expected) << "Merge(" << lhs << ", " << rhs << ") = ("
                                << result << " != " << expected << ")";
  }

  {
    // lhs |-------|
    // rhs             |-------|
    // res
    Schedule lhs{{Time{90ms}, Time{150ms}}};
    Schedule rhs{{Time{5ms}, Time{10ms}}};
    auto result = Merge(lhs, rhs);
    Schedule expected{};
    EXPECT_EQ(result, expected) << "Merge(" << lhs << ", " << rhs << ") = ("
                                << result << " != " << expected << ")";
  }
  {
    // lhs |-------|
    // rhs         |-------|
    // res
    Schedule lhs{{Time{0ms}, Time{5ms}}};
    Schedule rhs{{Time{5ms}, Time{10ms}}};
    auto result = Merge(lhs, rhs);
    Schedule expected{};
    EXPECT_EQ(result, expected) << "Merge(" << lhs << ", " << rhs << ") = ("
                                << result << " != " << expected << ")";
  }
  {
    // lhs |-------|
    // rhs
    // res
    Schedule lhs{{Time{0ms}, Time{10ms}}};
    Schedule rhs{};
    auto result = Merge(lhs, rhs);
    Schedule expected{};
    EXPECT_EQ(result, expected) << "Merge(" << lhs << ", " << rhs << ") = ("
                                << result << " != " << expected << ")";
  }
  {
    // lhs |-------|
    // rhs |-------|
    // res |-------|
    Schedule lhs{{Time{0ms}, Time{10ms}}};
    Schedule rhs{{Time{0ms}, Time{10ms}}};
    auto result = Merge(lhs, rhs);
    Schedule expected{{Time{0ms}, Time{10ms}}};
    EXPECT_EQ(result, expected) << "Merge(" << lhs << ", " << rhs << ") = ("
                                << result << " != " << expected << ")";
  }
  {
    // lhs |--------|
    // rhs    |---|
    // res    |---|
    Schedule lhs{{Time{0ms}, Time{10ms}}};
    Schedule rhs{{Time{4ms}, Time{5ms}}};
    auto result = Merge(lhs, rhs);
    Schedule expected{{Time{4ms}, Time{5ms}}};
    EXPECT_EQ(result, expected) << "Merge(" << lhs << ", " << rhs << ") = ("
                                << result << " != " << expected << ")";
  }
  {
    // lhs |--------|    |------|
    // rhs     |-----------|
    // res     |---|    |--|
    Schedule lhs{{Time{0ms}, Time{5ms}}, {Time{7ms}, Time{15ms}}};
    Schedule rhs{{Time{3ms}, Time{9ms}}};
    auto result = Merge(lhs, rhs);
    Schedule expected{{Time{3ms}, Time{5ms}}, {Time{7ms}, Time{9ms}}};
    EXPECT_EQ(result, expected) << "Merge(" << lhs << ", " << rhs << ") = ("
                                << result << " != " << expected << ")";
  }

  {
    // lhs     |----|    |---|
    // rhs  |------------------|
    // res     |----|    |---|
    Schedule lhs{{Time{2ms}, Time{5ms}}, {Time{7ms}, Time{15ms}}};
    Schedule rhs{{Time{0ms}, Time{20ms}}};
    auto result = Merge(lhs, rhs);
    Schedule expected{{Time{2ms}, Time{5ms}}, {Time{7ms}, Time{15ms}}};
    EXPECT_EQ(result, expected) << "Merge(" << lhs << ", " << rhs << ") = ("
                                << result << " != " << expected << ")";
  }
  {
    // lhs |--------|    |------|
    // rhs     |-----------|  |----|
    // res     |---|    |--|  |-|
    Schedule lhs{{Time{0ms}, Time{5ms}}, {Time{7ms}, Time{15ms}}};
    Schedule rhs{{Time{3ms}, Time{9ms}}, {Time{13ms}, Time{20ms}}};
    auto result = Merge(lhs, rhs);
    Schedule expected{{Time{3ms}, Time{5ms}},
                      {Time{7ms}, Time{9ms}},
                      {Time{13ms}, Time{15ms}}};
    EXPECT_EQ(result, expected) << "Merge(" << lhs << ", " << rhs << ") = ("
                                << result << " != " << expected << ")";
  }
}

TEST(Cut, All) {
  using namespace std::literals;
  using Time = std::chrono::system_clock::time_point;

  {
    // lhs     |-------|
    // rhs |-------|
    // res     |---|
    Schedule lhs{{Time{9ms}, Time{15ms}}};
    TimeInterval rhs{Time{5ms}, Time{10ms}};
    auto result = Cut(lhs, rhs);
    Schedule expected{{Time{9ms}, Time{10ms}}};
    EXPECT_EQ(result, expected) << "Cut(" << lhs << ", " << rhs << ") = ("
                                << result << " != " << expected << ")";
  }

  {
    // lhs |-------|
    // rhs             |-------|
    // res
    Schedule lhs{{Time{90ms}, Time{150ms}}};
    TimeInterval rhs{Time{5ms}, Time{10ms}};
    auto result = Cut(lhs, rhs);
    Schedule expected{};
    EXPECT_EQ(result, expected) << "Cut(" << lhs << ", " << rhs << ") = ("
                                << result << " != " << expected << ")";
  }
  {
    // lhs |-------|
    // rhs         |-------|
    // res
    Schedule lhs{{Time{0ms}, Time{5ms}}};
    TimeInterval rhs{Time{5ms}, Time{10ms}};
    auto result = Cut(lhs, rhs);
    Schedule expected{};
    EXPECT_EQ(result, expected) << "Cut(" << lhs << ", " << rhs << ") = ("
                                << result << " != " << expected << ")";
  }
  {
    // lhs |-------|
    // rhs
    // res
    Schedule lhs{{Time{0ms}, Time{10ms}}};
    TimeInterval rhs{};
    auto result = Cut(lhs, rhs);
    Schedule expected{};
    EXPECT_EQ(result, expected) << "Cut(" << lhs << ", " << rhs << ") = ("
                                << result << " != " << expected << ")";
  }
  {
    // lhs |-------|
    // rhs |-------|
    // res |-------|
    Schedule lhs{{Time{0ms}, Time{10ms}}};
    TimeInterval rhs{Time{0ms}, Time{10ms}};
    auto result = Cut(lhs, rhs);
    Schedule expected{{Time{0ms}, Time{10ms}}};
    EXPECT_EQ(result, expected) << "Cut(" << lhs << ", " << rhs << ") = ("
                                << result << " != " << expected << ")";
  }
  {
    // lhs |--------|
    // rhs    |---|
    // res    |---|
    Schedule lhs{{Time{0ms}, Time{10ms}}};
    TimeInterval rhs{Time{4ms}, Time{5ms}};
    auto result = Cut(lhs, rhs);
    Schedule expected{{Time{4ms}, Time{5ms}}};
    EXPECT_EQ(result, expected) << "Cut(" << lhs << ", " << rhs << ") = ("
                                << result << " != " << expected << ")";
  }
  {
    // lhs |--------|    |------|
    // rhs     |-----------|
    // res     |---|    |--|
    Schedule lhs{{Time{0ms}, Time{5ms}}, {Time{7ms}, Time{15ms}}};
    TimeInterval rhs{Time{3ms}, Time{9ms}};
    auto result = Cut(lhs, rhs);
    Schedule expected{{Time{3ms}, Time{5ms}}, {Time{7ms}, Time{9ms}}};
    EXPECT_EQ(result, expected) << "Cut(" << lhs << ", " << rhs << ") = ("
                                << result << " != " << expected << ")";
  }

  {
    // lhs     |----|    |---|
    // rhs  |------------------|
    // res     |----|    |---|
    Schedule lhs{{Time{2ms}, Time{5ms}}, {Time{7ms}, Time{15ms}}};
    TimeInterval rhs{Time{0ms}, Time{20ms}};
    auto result = Cut(lhs, rhs);
    Schedule expected{{Time{2ms}, Time{5ms}}, {Time{7ms}, Time{15ms}}};
    EXPECT_EQ(result, expected) << "Cut(" << lhs << ", " << rhs << ") = ("
                                << result << " != " << expected << ")";
  }
}

}  // namespace eats_places_availability::utils
