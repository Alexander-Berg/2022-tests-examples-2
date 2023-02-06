#include <gtest/gtest.h>

#include <userver/utils/datetime.hpp>

#include <common/types.hpp>
#include <common/utils/time.hpp>

namespace tu = billing_time_events::utils;

namespace {
using TimePoint = billing_time_events::types::TimePoint;
using TimeRange = billing_time_events::types::TimeRange;
using TimeRanges = billing_time_events::types::TimeRanges;
using CivilDstTransition = billing_time_events::types::CivilDstTransition;
using CivilTimePoint = billing_time_events::types::CivilTimePoint;
using Minutes = std::chrono::minutes;
using Hours = std::chrono::hours;

constexpr auto kEpoch = TimePoint{};
}  // namespace

TEST(SpanTest, AllTimeIfNoIntervals) {
  ASSERT_EQ(tu::Span({}), TimeRange(TimePoint::max(), TimePoint::min()));
}

TEST(SpanTest, TheSameIntervalIfOneInterval) {
  TimeRange tr{TimePoint{Minutes{6}}, TimePoint{Minutes{28}}};
  ASSERT_EQ(tu::Span({tr}), tr);
}

TEST(SpanTest, TwoIntervalsInAscOrder) {
  TimeRange tr1{TimePoint{Minutes{6}}, TimePoint{Minutes{28}}};
  TimeRange tr2{TimePoint{Minutes{496}}, TimePoint{Minutes{8128}}};
  TimeRange expected{tr1.lower(), tr2.upper()};
  ASSERT_EQ(tu::Span({tr1, tr2}), expected);
}

TEST(SpanTest, TwoIntervalsInDescOrder) {
  TimeRange tr1{TimePoint{Minutes{496}}, TimePoint{Minutes{8128}}};
  TimeRange tr2{TimePoint{Minutes{6}}, TimePoint{Minutes{28}}};
  TimeRange expected{tr2.lower(), tr1.upper()};
  ASSERT_EQ(tu::Span({tr1, tr2}), expected);
}

TEST(SpanTest, TwoOverlappingIntervals) {
  TimeRange tr1{TimePoint{Minutes{6}}, TimePoint{Minutes{8128}}};
  TimeRange tr2{TimePoint{Minutes{28}}, TimePoint{Minutes{496}}};
  TimeRange expected{tr1};
  ASSERT_EQ(tu::Span({tr1, tr2}), expected);
}

TEST(SpanTest, SkipInvalidInterval) {
  TimeRange tr1{TimePoint{Minutes{8126}}, TimePoint{Minutes{496}}};
  TimeRange tr2{TimePoint{Minutes{6}}, TimePoint{Minutes{28}}};
  TimeRange expected{tr2};
  ASSERT_EQ(tu::Span({tr1, tr2}), expected);
}

TEST(IntersectsTest, FalseIfEmpty) {
  TimeRanges intervals{};
  ASSERT_FALSE(tu::Intersects(intervals));
}

TEST(IntersectsTest, FalseIfOnly) {
  TimeRanges intervals{{TimePoint{Minutes{6}}, TimePoint{Minutes{28}}}};
  ASSERT_FALSE(tu::Intersects(intervals));
}

TEST(IntersectsTest, FalseIfNoIntersection) {
  TimeRanges intervals{{TimePoint{Minutes{6}}, TimePoint{Minutes{28}}},
                       {TimePoint{Minutes{496}}, TimePoint{Minutes{8128}}}};
  ASSERT_FALSE(tu::Intersects(intervals));
}

TEST(IntersectsTest, FalseIfOnlyTouching) {
  TimeRanges intervals{{TimePoint{Minutes{6}}, TimePoint{Minutes{28}}},
                       {TimePoint{Minutes{28}}, TimePoint{Minutes{496}}}};
  ASSERT_FALSE(tu::Intersects(intervals));
}

TEST(IntersectsTest, TrueIfEqual) {
  TimeRanges intervals{{TimePoint{Minutes{6}}, TimePoint{Minutes{28}}},
                       {TimePoint{Minutes{6}}, TimePoint{Minutes{28}}}};
  ASSERT_TRUE(tu::Intersects(intervals));
}

TEST(IntersectsTest, TrueIfOneContainsAnother) {
  TimeRanges intervals{{TimePoint{Minutes{6}}, TimePoint{Minutes{8128}}},
                       {TimePoint{Minutes{28}}, TimePoint{Minutes{496}}}};
  ASSERT_TRUE(tu::Intersects(intervals));
}

TEST(RangesWithRangesIntersectionTest, BothEmpty) {
  using namespace billing_time_events;
  TimeRanges a{};
  TimeRanges b{};

  auto c = a & b;
  ASSERT_TRUE(c.empty());
}

TEST(RangesWithRangesIntersectionTest, OneEmpty) {
  using namespace billing_time_events;
  TimeRanges a{{kEpoch, kEpoch + Minutes{2}},
               {kEpoch + Minutes{2}, kEpoch + Minutes{4}}};
  TimeRanges b{};
  auto c = a & b;
  ASSERT_TRUE(c.empty());
}

TEST(RangesWithRangesIntersectionTest, Equal) {
  using namespace billing_time_events;
  TimeRanges a{{kEpoch, kEpoch + Minutes{2}},
               {kEpoch + Minutes{2}, kEpoch + Minutes{4}}};
  TimeRanges b = a;
  auto c = a & b;
  ASSERT_TRUE(c == a);
}

TEST(RangesWithRangesIntersectionTest, IntersectBoth) {
  using namespace billing_time_events;
  TimeRanges a{{kEpoch, kEpoch + Minutes{2}},
               {kEpoch + Minutes{2}, kEpoch + Minutes{4}}};
  TimeRanges b{{kEpoch + Minutes{1}, kEpoch + Minutes{3}}};
  auto c = a & b;
  ASSERT_EQ(c.size(), 2);
  TimeRange expected0{kEpoch + Minutes{1}, kEpoch + Minutes{2}};
  EXPECT_EQ(c[0], expected0);
  TimeRange expected1{kEpoch + Minutes{2}, kEpoch + Minutes{3}};
  EXPECT_EQ(c[1], expected1);
}

TEST(RangesWithRangeIntersectionTest, NoIntersections) {
  using namespace billing_time_events;
  TimeRanges a{{kEpoch, kEpoch + Minutes{2}},
               {kEpoch + Minutes{2}, kEpoch + Minutes{4}}};
  TimeRange b{kEpoch + Minutes{5}, kEpoch + Minutes{6}};
  auto c = a & b;
  ASSERT_TRUE(c.empty());
}

TEST(RangesWithRangeIntersectionTest, RangeOverlapRanges) {
  using namespace billing_time_events;
  TimeRanges a{{kEpoch, kEpoch + Minutes{2}},
               {kEpoch + Minutes{2}, kEpoch + Minutes{4}}};
  TimeRange b{kEpoch, kEpoch + Minutes{6}};
  auto c = a & b;
  ASSERT_EQ(c, a);
}

TEST(RangesWithRangeIntersectionTest, IntersectBoth) {
  using namespace billing_time_events;
  TimeRanges a{{kEpoch, kEpoch + Minutes{2}},
               {kEpoch + Minutes{2}, kEpoch + Minutes{4}}};
  TimeRange b{kEpoch + Minutes{1}, kEpoch + Minutes{3}};
  auto c = a & b;
  ASSERT_EQ(c.size(), 2);
  TimeRange expected0{kEpoch + Minutes{1}, kEpoch + Minutes{2}};
  EXPECT_EQ(c[0], expected0);
  TimeRange expected1{kEpoch + Minutes{2}, kEpoch + Minutes{3}};
  EXPECT_EQ(c[1], expected1);
}

TEST(SplitAtEveryNthMinuteTest, NoSplitWhenEmptyRange) {
  const TimePoint tp{Minutes{6}};
  auto actual_intervals = tu::SplitAtEveryNthMinute({tp, tp}, Minutes{1});
  ASSERT_EQ(actual_intervals.size(), 1);
  EXPECT_EQ(actual_intervals[0], TimeRange(tp, tp));
}

TEST(SplitAtEveryNthMinuteTest, NoSplitWhenNthMinuteIsZero) {
  const TimePoint tp1{Minutes{6}};
  const TimePoint tp2{Minutes{28}};
  auto actual_intervals = tu::SplitAtEveryNthMinute({tp1, tp2}, Minutes{0});
  ASSERT_EQ(actual_intervals.size(), 1);
  EXPECT_EQ(actual_intervals[0], TimeRange(tp1, tp2));
}

TEST(SplitAtEveryNthMinuteTest, WhenIntervalStartAtNthMinute) {
  const TimePoint tp1{Minutes{0}};
  const TimePoint tp2{Minutes{28}};
  auto actual_intervals = tu::SplitAtEveryNthMinute({tp1, tp2}, Minutes{20});
  const TimePoint new_tp{Minutes{20}};
  ASSERT_EQ(actual_intervals.size(), 2);
  EXPECT_EQ(actual_intervals[0], TimeRange(tp1, new_tp));
  EXPECT_EQ(actual_intervals[1], TimeRange(new_tp, tp2));
}

TEST(SplitAtEveryNthMinuteTest, WhenIntervalEndAtNthMinute) {
  const TimePoint tp1{Minutes{6}};
  const TimePoint tp2{Minutes{28}};
  auto actual_intervals = tu::SplitAtEveryNthMinute({tp1, tp2}, Minutes{20});
  const TimePoint new_tp{Minutes{20}};
  ASSERT_EQ(actual_intervals.size(), 2);
  EXPECT_EQ(actual_intervals[0], TimeRange(tp1, new_tp));
  EXPECT_EQ(actual_intervals[1], TimeRange(new_tp, tp2));
}

TEST(SplitAtEveryNthMinuteTest, WhenDayChange) {
  const TimePoint tp1{Hours{23}};
  const TimePoint tp2{Hours{25}};
  auto actual_intervals = tu::SplitAtEveryNthMinute({tp1, tp2}, Minutes{60});
  ASSERT_EQ(actual_intervals.size(), 2);
  const TimePoint new_tp{Hours{24}};
  EXPECT_EQ(actual_intervals[0], TimeRange(tp1, new_tp));
  EXPECT_EQ(actual_intervals[1], TimeRange(new_tp, tp2));
}

TEST(FindDstTransition, NoTransition) {
  using ::utils::datetime::Stringtime;
  auto since = Stringtime("2021-10-01T00:00:00Z");
  auto till = Stringtime("2021-10-30T00:00:00Z");
  const auto transition = tu::FindDstTransition({since, till}, "Israel");
  EXPECT_FALSE(transition.has_value());

  since = Stringtime("2021-10-01T00:00:00Z");
  till = Stringtime("2021-11-01T00:00:00Z");
  EXPECT_FALSE(
      tu::FindDstTransition({since, till}, "Europe/Moscow").has_value());
}

TEST(FindDstTransition, WinterTimeTransition) {
  using ::utils::datetime::Stringtime;
  auto since = Stringtime("2021-10-30T00:00:00Z");
  auto till = Stringtime("2021-11-01T00:00:00Z");
  auto actual = tu::FindDstTransition({since, till}, "Israel");

  ASSERT_TRUE(actual.has_value());
  CivilTimePoint expected_from{2021, 10, 31, 2};
  EXPECT_EQ(actual->from, expected_from);
  CivilTimePoint expected_to{2021, 10, 31, 1};
  EXPECT_EQ(actual->to, expected_to);
}

TEST(FindDstTransition, SummerTimeTransition) {
  using ::utils::datetime::Stringtime;
  auto since = Stringtime("2021-03-25T00:00:00Z");
  auto till = Stringtime("2021-03-27T00:00:00Z");
  auto actual = tu::FindDstTransition({since, till}, "Israel");

  ASSERT_TRUE(actual.has_value());
  CivilTimePoint expected_from{2021, 03, 26, 2};
  EXPECT_EQ(actual->from, expected_from);
  CivilTimePoint expected_to{2021, 03, 26, 3};
  EXPECT_EQ(actual->to, expected_to);
}
