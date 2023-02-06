#include <utils/time_interval.hpp>

#include <userver/utest/utest.hpp>

namespace eats_logistics_performer_payouts::utils {

TEST(MergeTimeInterval, NonIntersectingIntoEnd) {
  using Sec = std::chrono::seconds;
  TimeIntervalList intervals{
      {Sec{0}, Sec{1}},
      {Sec{8}, Sec{9}},
  };
  const TimeIntervalList expected_intervals{
      {Sec{0}, Sec{1}},
      {Sec{8}, Sec{9}},
      {Sec{10}, Sec{12}},
  };

  MergeTimeInterval(intervals, TimeInterval{Sec{10}, Sec{12}});
  ASSERT_EQ(intervals, expected_intervals);
}

TEST(MergeTimeInterval, NonIntersectingIntoMiddle) {
  using Sec = std::chrono::seconds;
  TimeIntervalList intervals{
      {Sec{0}, Sec{1}},
      {Sec{8}, Sec{9}},
  };
  const TimeIntervalList expected_intervals{
      {Sec{0}, Sec{1}},
      {Sec{3}, Sec{5}},
      {Sec{8}, Sec{9}},
  };

  MergeTimeInterval(intervals, TimeInterval{Sec{3}, Sec{5}});
  ASSERT_EQ(intervals, expected_intervals);
}

TEST(MergeTimeInterval, IntersectingIntoMiddle) {
  using Sec = std::chrono::seconds;
  TimeIntervalList intervals{
      {Sec{0}, Sec{1}},
      {Sec{2}, Sec{4}},
      {Sec{5}, Sec{7}},
      {Sec{8}, Sec{9}},
  };
  const TimeIntervalList expected_intervals{
      {Sec{0}, Sec{1}},
      {Sec{2}, Sec{7}},
      {Sec{8}, Sec{9}},
  };

  MergeTimeInterval(intervals, TimeInterval{Sec{3}, Sec{6}});
  ASSERT_EQ(intervals, expected_intervals);
}

}  // namespace eats_logistics_performer_payouts::utils
