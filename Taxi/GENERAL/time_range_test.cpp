#include "time_range.hpp"

#include <userver/utest/utest.hpp>

TEST(TimeRange, Includes) {
  using models::TimeRange;
  using TimePoint = TimeRange::TimePoint;
  using Duration = TimePoint::duration;

  TimePoint tp1(Duration(2));
  TimePoint tp2(Duration(4));
  TimeRange r1 = {tp1, tp2};

  // check the inclusion of the border of range
  EXPECT_TRUE(r1.Includes(tp1));
  EXPECT_TRUE(r1.Includes(tp2));

  // check the middle of range
  TimePoint tp3(Duration(3));
  EXPECT_TRUE(r1.Includes(tp3));

  // check the out of range
  TimePoint tp4(Duration(5));
  TimePoint tp5(Duration(0));
  EXPECT_FALSE(r1.Includes(tp4));
  EXPECT_FALSE(r1.Includes(tp5));
}

TEST(TimeRange, Intersects) {
  using models::Intersects;
  using models::TimeRange;
  using TimePoint = TimeRange::TimePoint;
  using Duration = TimePoint::duration;

  TimePoint tp0(Duration(0));
  TimePoint tp2(Duration(2));
  TimePoint tp3(Duration(3));
  TimePoint tp4(Duration(4));
  TimePoint tp5(Duration(5));

  TimeRange r = {tp2, tp4};

  // check self intersections
  EXPECT_TRUE(Intersects({tp2, tp4}, {tp2, tp2}));
  EXPECT_TRUE(Intersects({tp2, tp2}, {tp2, tp4}));

  EXPECT_TRUE(Intersects({tp2, tp4}, {tp4, tp4}));
  EXPECT_TRUE(Intersects({tp4, tp4}, {tp2, tp4}));

  EXPECT_TRUE(Intersects({tp2, tp4}, {tp2, tp4}));
  EXPECT_TRUE(Intersects(r, r));

  // check border intersections
  EXPECT_TRUE(Intersects({tp2, tp4}, {tp4, tp5}));
  EXPECT_TRUE(Intersects({tp4, tp5}, {tp2, tp4}));

  EXPECT_TRUE(Intersects({tp0, tp2}, {tp2, tp4}));
  EXPECT_TRUE(Intersects({tp2, tp4}, {tp0, tp2}));

  EXPECT_TRUE(Intersects({tp2, tp3}, {tp2, tp4}));
  EXPECT_TRUE(Intersects({tp2, tp4}, {tp2, tp3}));

  EXPECT_TRUE(Intersects({tp3, tp4}, {tp2, tp4}));
  EXPECT_TRUE(Intersects({tp2, tp4}, {tp3, tp4}));

  // check out of intersection
  EXPECT_FALSE(Intersects({tp0, tp2}, {tp3, tp4}));
  EXPECT_FALSE(Intersects({tp3, tp4}, {tp0, tp2}));
}

TEST(TimeRange, GetIntersection) {
  using models::GetIntersection;
  using models::TimeRange;
  using TimePoint = TimeRange::TimePoint;
  using Duration = TimePoint::duration;

  TimePoint tp0(Duration(0));
  TimePoint tp2(Duration(2));
  TimePoint tp3(Duration(3));
  TimePoint tp4(Duration(4));
  TimePoint tp5(Duration(5));

  TimeRange r = {tp2, tp4};

  // check self intersections
  EXPECT_TRUE(GetIntersection({tp2, tp4}, {tp2, tp2}).has_value());
  EXPECT_TRUE(GetIntersection({tp2, tp2}, {tp2, tp4}).has_value());
  EXPECT_EQ(*GetIntersection({tp2, tp4}, {tp2, tp2}), TimeRange(tp2, tp2));
  EXPECT_EQ(*GetIntersection({tp2, tp2}, {tp2, tp4}), TimeRange(tp2, tp2));

  EXPECT_TRUE(GetIntersection({tp2, tp4}, {tp4, tp4}).has_value());
  EXPECT_TRUE(GetIntersection({tp4, tp4}, {tp2, tp4}).has_value());
  EXPECT_EQ(*GetIntersection({tp2, tp4}, {tp4, tp4}), TimeRange(tp4, tp4));
  EXPECT_EQ(*GetIntersection({tp4, tp4}, {tp2, tp4}), TimeRange(tp4, tp4));

  EXPECT_TRUE(GetIntersection({tp2, tp4}, {tp2, tp4}).has_value());
  EXPECT_EQ(*GetIntersection({tp2, tp4}, {tp2, tp4}), TimeRange(tp2, tp4));

  EXPECT_TRUE(GetIntersection(r, r).has_value());
  EXPECT_EQ(*GetIntersection(r, r), r);

  // check border intersections
  EXPECT_TRUE(GetIntersection({tp2, tp4}, {tp4, tp5}).has_value());
  EXPECT_TRUE(GetIntersection({tp4, tp5}, {tp2, tp4}).has_value());
  EXPECT_EQ(*GetIntersection({tp2, tp4}, {tp4, tp5}), TimeRange(tp4, tp4));
  EXPECT_EQ(*GetIntersection({tp4, tp5}, {tp2, tp4}), TimeRange(tp4, tp4));

  EXPECT_TRUE(GetIntersection({tp2, tp4}, {tp0, tp2}).has_value());
  EXPECT_TRUE(GetIntersection({tp0, tp2}, {tp2, tp4}).has_value());
  EXPECT_EQ(*GetIntersection({tp2, tp4}, {tp0, tp2}), TimeRange(tp2, tp2));
  EXPECT_EQ(*GetIntersection({tp0, tp2}, {tp2, tp4}), TimeRange(tp2, tp2));

  EXPECT_TRUE(GetIntersection({tp2, tp4}, {tp2, tp3}).has_value());
  EXPECT_TRUE(GetIntersection({tp2, tp3}, {tp2, tp4}).has_value());
  EXPECT_EQ(*GetIntersection({tp2, tp4}, {tp2, tp3}), TimeRange(tp2, tp3));
  EXPECT_EQ(*GetIntersection({tp2, tp3}, {tp2, tp4}), TimeRange(tp2, tp3));

  EXPECT_TRUE(GetIntersection({tp2, tp4}, {tp3, tp4}).has_value());
  EXPECT_TRUE(GetIntersection({tp3, tp4}, {tp2, tp4}).has_value());
  EXPECT_EQ(*GetIntersection({tp2, tp4}, {tp3, tp4}), TimeRange(tp3, tp4));
  EXPECT_EQ(*GetIntersection({tp3, tp4}, {tp2, tp4}), TimeRange(tp3, tp4));

  // check out of intersection
  EXPECT_FALSE(GetIntersection({tp0, tp2}, {tp3, tp4}).has_value());
  EXPECT_FALSE(GetIntersection({tp3, tp4}, {tp0, tp2}).has_value());
}

TEST(TimeRange, DayIterator) {
  using models::DayIterator;
  using models::TimeRange;
  using TimePoint = TimeRange::TimePoint;
  using Duration = TimePoint::duration;

  const Duration kDurationStepUnit{1};

  TimePoint day0{utils::Days{0}};
  TimePoint day1{utils::Days{1}};
  TimePoint day2{utils::Days{2}};
  TimePoint end_day0{day1 - kDurationStepUnit};
  TimePoint end_day1{day2 - kDurationStepUnit};
  TimePoint end_day2{utils::Days{3} - kDurationStepUnit};

  {
    models::DayIterator iter{{day0, day0}};
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day0, day0), *iter);
    ++iter;
    EXPECT_TRUE(iter.IsEnd());
  }
  {
    models::DayIterator iter{{day1, day1}};
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day1, day1), *iter);
    ++iter;
    EXPECT_TRUE(iter.IsEnd());
  }
  {
    models::DayIterator iter{{day1, day2}};
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day1, end_day1), *iter);
    ++iter;
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day2, day2), *iter);
    ++iter;
    EXPECT_TRUE(iter.IsEnd());
  }
  {
    models::DayIterator iter{{day0, day2}};
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day0, end_day0), *iter);
    ++iter;
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day1, end_day1), *iter);
    ++iter;
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day2, day2), *iter);
    ++iter;
    EXPECT_TRUE(iter.IsEnd());
  }
  {
    models::DayIterator iter{{day0, end_day2}};
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day0, end_day0), *iter);
    ++iter;
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day1, end_day1), *iter);
    ++iter;
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day2, end_day2), *iter);
    ++iter;
    EXPECT_TRUE(iter.IsEnd());
  }
  {
    models::DayIterator iter{{end_day0, end_day2}};
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(end_day0, end_day0), *iter);
    ++iter;
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day1, end_day1), *iter);
    ++iter;
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day2, end_day2), *iter);
    ++iter;
    EXPECT_TRUE(iter.IsEnd());
  }
}

TEST(TimeRange, DayReverseIterator) {
  using models::DayReverseIterator;
  using models::TimeRange;
  using TimePoint = TimeRange::TimePoint;
  using Duration = TimePoint::duration;

  const Duration kDurationStepUnit{1};

  TimePoint day0{utils::Days{0}};
  TimePoint day1{utils::Days{1}};
  TimePoint day2{utils::Days{2}};
  TimePoint end_day0{day1 - kDurationStepUnit};
  TimePoint end_day1{day2 - kDurationStepUnit};
  TimePoint end_day2{utils::Days{3} - kDurationStepUnit};

  {
    models::DayReverseIterator iter{{day0, day0}};
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day0, day0), *iter);
    ++iter;
    EXPECT_TRUE(iter.IsEnd());
  }
  {
    models::DayReverseIterator iter{{day1, day1}};
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day1, day1), *iter);
    ++iter;
    EXPECT_TRUE(iter.IsEnd());
  }
  {
    models::DayReverseIterator iter{{day1, day2}};
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day2, day2), *iter);
    ++iter;
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day1, end_day1), *iter);
    ++iter;
    EXPECT_TRUE(iter.IsEnd());
  }
  {
    models::DayReverseIterator iter{{day0, day2}};
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day2, day2), *iter);
    ++iter;
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day1, end_day1), *iter);
    ++iter;
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day0, end_day0), *iter);
    ++iter;
    EXPECT_TRUE(iter.IsEnd());
  }
  {
    models::DayReverseIterator iter{{day0, end_day2}};
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day2, end_day2), *iter);
    ++iter;
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day1, end_day1), *iter);
    ++iter;
    EXPECT_FALSE(iter.IsEnd());
    EXPECT_EQ(TimeRange(day0, end_day0), *iter);
    ++iter;
    EXPECT_TRUE(iter.IsEnd());
  }
}
