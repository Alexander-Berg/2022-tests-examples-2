#include "driver_status_interval_merger.hpp"

#include <gtest/gtest.h>

namespace helpers {
namespace driver_weariness {

namespace {

auto end_time = utils::TimePoint(utils::TimePoint(std::chrono::minutes(25)));
auto start_time = utils::TimePoint();
auto max_interval_time = std::chrono::minutes(5);
auto no_move_time = std::chrono::minutes(15);

using tracker_internal::DStatus;
using tracker_internal::TaximeterStatus;

}  // namespace

TEST(DriverStatusIntervalMergerTest, TestAddInterval) {
  DriverStatusIntervalMerger intervalMerger(start_time, end_time,
                                            max_interval_time, no_move_time);

  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(1)),
      utils::TimePoint(std::chrono::seconds(5)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  EXPECT_EQ(intervalMerger.IntersectIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.NotCalculatedIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.IntervalCount(), 1u);
  EXPECT_EQ(intervalMerger.AllMergedIntervalCount(), 1u);

  const auto& intervals = intervalMerger.GetIntervals();

  EXPECT_EQ(intervals[0].is_work, false);
  EXPECT_EQ(intervals[0].driver_status.status,
            TaximeterStatus::StatusInt::BUSY);
  EXPECT_EQ(
      intervals[0].start_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(1)).time_since_epoch().count());
  EXPECT_EQ(
      intervals[0].end_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(5)).time_since_epoch().count());
}

TEST(DriverStatusIntervalMergerTest, TestAddTwoIntervals) {
  DriverStatusIntervalMerger intervalMerger(start_time, end_time,
                                            max_interval_time, no_move_time);

  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(1)),
      utils::TimePoint(std::chrono::seconds(5)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(6)),
      utils::TimePoint(std::chrono::seconds(7)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none));
  EXPECT_EQ(intervalMerger.IntersectIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.NotCalculatedIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.IntervalCount(), 2u);
  EXPECT_EQ(intervalMerger.AllMergedIntervalCount(), 2u);

  const auto& intervals = intervalMerger.GetIntervals();
  auto& interval = intervals[0];

  EXPECT_EQ(interval.is_work, false);
  EXPECT_EQ(interval.driver_status.status, TaximeterStatus::StatusInt::BUSY);
  EXPECT_EQ(
      interval.start_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(1)).time_since_epoch().count());
  EXPECT_EQ(
      interval.end_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(5)).time_since_epoch().count());

  auto& next_interval = intervals[1];
  EXPECT_EQ(next_interval.is_work, true);
  EXPECT_EQ(next_interval.driver_status.status,
            TaximeterStatus::StatusInt::FREE);
  EXPECT_EQ(
      next_interval.start_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(6)).time_since_epoch().count());
  EXPECT_EQ(
      next_interval.end_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(7)).time_since_epoch().count());
}

TEST(DriverStatusIntervalMergerTest, TestMergeTwoIntervals) {
  DriverStatusIntervalMerger intervalMerger(start_time, end_time,
                                            max_interval_time, no_move_time);

  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(1)),
      utils::TimePoint(std::chrono::seconds(5)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(5)),
      utils::TimePoint(std::chrono::seconds(6)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  EXPECT_EQ(intervalMerger.IntersectIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.NotCalculatedIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.IntervalCount(), 1u);
  EXPECT_EQ(intervalMerger.AllMergedIntervalCount(), 1u);

  const auto& intervals = intervalMerger.GetIntervals();

  EXPECT_EQ(intervals[0].is_work, false);
  EXPECT_EQ(intervals[0].driver_status.status,
            TaximeterStatus::StatusInt::BUSY);
  EXPECT_EQ(
      intervals[0].start_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(1)).time_since_epoch().count());
  EXPECT_EQ(
      intervals[0].end_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(6)).time_since_epoch().count());
}

TEST(DriverStatusIntervalMergerTest, TestMergeTwoIntervals_2) {
  DriverStatusIntervalMerger intervalMerger(start_time, end_time,
                                            max_interval_time, no_move_time);

  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(5)),
      utils::TimePoint(std::chrono::seconds(6)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(1)),
      utils::TimePoint(std::chrono::seconds(5)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  EXPECT_EQ(intervalMerger.IntersectIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.NotCalculatedIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.IntervalCount(), 1u);
  EXPECT_EQ(intervalMerger.AllMergedIntervalCount(), 1u);

  const auto& intervals = intervalMerger.GetIntervals();

  EXPECT_EQ(intervals[0].is_work, false);
  EXPECT_EQ(intervals[0].driver_status.status,
            TaximeterStatus::StatusInt::BUSY);
  EXPECT_EQ(
      intervals[0].start_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(1)).time_since_epoch().count());
  EXPECT_EQ(
      intervals[0].end_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(6)).time_since_epoch().count());
}

TEST(DriverStatusIntervalMergerTest, TestMergeThreeIntervals) {
  DriverStatusIntervalMerger intervalMerger(start_time, end_time,
                                            max_interval_time, no_move_time);

  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(6)),
      utils::TimePoint(std::chrono::seconds(7)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(1)),
      utils::TimePoint(std::chrono::seconds(5)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(5)),
      utils::TimePoint(std::chrono::seconds(6)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));

  EXPECT_EQ(intervalMerger.IntersectIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.NotCalculatedIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.IntervalCount(), 1u);
  EXPECT_EQ(intervalMerger.AllMergedIntervalCount(), 1u);

  const auto& intervals = intervalMerger.GetIntervals();

  EXPECT_EQ(intervals[0].is_work, false);
  EXPECT_EQ(intervals[0].driver_status.status,
            TaximeterStatus::StatusInt::BUSY);
  EXPECT_EQ(
      intervals[0].start_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(1)).time_since_epoch().count());
  EXPECT_EQ(
      intervals[0].end_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(7)).time_since_epoch().count());
}

TEST(DriverStatusIntervalMergerTest, TestBeginIntersection) {
  DriverStatusIntervalMerger intervalMerger(start_time, end_time,
                                            max_interval_time, no_move_time);

  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(7)),
      utils::TimePoint(std::chrono::seconds(8)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(1)),
      utils::TimePoint(std::chrono::seconds(5)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  // This interval intersect with last one added.
  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(4)),
      utils::TimePoint(std::chrono::seconds(6)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));

  EXPECT_EQ(intervalMerger.IntersectIntervalCount(), 1u);
  EXPECT_EQ(intervalMerger.NotCalculatedIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.IntervalCount(), 2u);
  EXPECT_EQ(intervalMerger.AllMergedIntervalCount(), 2u);

  const auto& intersect_intervals = intervalMerger.GetIntersectIntervals();
  const auto& interval = intersect_intervals[0];

  // check intersected interval
  EXPECT_EQ(interval.is_work, false);
  EXPECT_EQ(interval.driver_status.status, TaximeterStatus::StatusInt::BUSY);
  EXPECT_EQ(
      interval.start_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(4)).time_since_epoch().count());
  EXPECT_EQ(
      interval.end_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(6)).time_since_epoch().count());
}

TEST(DriverStatusIntervalMergerTest, TestEndIntersection) {
  DriverStatusIntervalMerger intervalMerger(start_time, end_time,
                                            max_interval_time, no_move_time);

  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(1)),
      utils::TimePoint(std::chrono::seconds(5)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(7)),
      utils::TimePoint(std::chrono::seconds(8)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  // This interval intersect with last one added.
  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(6)),
      utils::TimePoint(std::chrono::seconds(8)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));

  EXPECT_EQ(intervalMerger.IntersectIntervalCount(), 1u);
  EXPECT_EQ(intervalMerger.NotCalculatedIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.IntervalCount(), 2u);
  EXPECT_EQ(intervalMerger.AllMergedIntervalCount(), 2u);

  const auto& intersect_intervals = intervalMerger.GetIntersectIntervals();
  const auto& interval = intersect_intervals[0];

  // check intersected interval
  EXPECT_EQ(interval.is_work, false);
  EXPECT_EQ(interval.driver_status.status, TaximeterStatus::StatusInt::BUSY);
  EXPECT_EQ(
      interval.start_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(6)).time_since_epoch().count());
  EXPECT_EQ(
      interval.end_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(8)).time_since_epoch().count());
}

TEST(DriverStatusIntervalMergerTest, TestTwoIntervalsIntersection) {
  DriverStatusIntervalMerger intervalMerger(start_time, end_time,
                                            max_interval_time, no_move_time);

  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(1)),
      utils::TimePoint(std::chrono::seconds(5)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(7)),
      utils::TimePoint(std::chrono::seconds(8)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  // This interval intersect with two intervals.
  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(4)),
      utils::TimePoint(std::chrono::seconds(8)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));

  EXPECT_EQ(intervalMerger.IntersectIntervalCount(), 1u);
  EXPECT_EQ(intervalMerger.NotCalculatedIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.IntervalCount(), 2u);
  EXPECT_EQ(intervalMerger.AllMergedIntervalCount(), 2u);

  const auto& intersect_intervals = intervalMerger.GetIntersectIntervals();
  const auto& interval = intersect_intervals[0];

  // check intersected interval
  EXPECT_EQ(interval.is_work, false);
  EXPECT_EQ(interval.driver_status.status, TaximeterStatus::StatusInt::BUSY);
  EXPECT_EQ(
      interval.start_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(4)).time_since_epoch().count());
  EXPECT_EQ(
      interval.end_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(8)).time_since_epoch().count());
}

TEST(DriverStatusIntervalMergerTest, TestAddNotCalculatedInterval) {
  DriverStatusIntervalMerger intervalMerger(start_time, end_time,
                                            max_interval_time, no_move_time);

  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(1)),
      utils::TimePoint(std::chrono::seconds(5)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(7)),
      utils::TimePoint(std::chrono::seconds(8)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  // This interval is not calculated.
  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::minutes(1)),
      utils::TimePoint(std::chrono::minutes(2) + max_interval_time),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));

  EXPECT_EQ(intervalMerger.IntersectIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.NotCalculatedIntervalCount(), 1u);
  EXPECT_EQ(intervalMerger.IntervalCount(), 2u);
  EXPECT_EQ(intervalMerger.AllMergedIntervalCount(), 2u);

  const auto& not_calc_intervals = intervalMerger.GetNotCalculatedIntervals();
  const auto& interval = not_calc_intervals[0];

  // check intersected interval
  EXPECT_EQ(interval.is_work, false);
  EXPECT_EQ(interval.driver_status.status, TaximeterStatus::StatusInt::BUSY);
  EXPECT_EQ(
      interval.start_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(1)).time_since_epoch().count());
  EXPECT_EQ(interval.end_time.time_since_epoch().count(),
            utils::TimePoint(std::chrono::minutes(2) + max_interval_time)
                .time_since_epoch()
                .count());
}

TEST(DriverStatusIntervalMergerTest, TestNotMergeDifferentIntervals) {
  DriverStatusIntervalMerger intervalMerger(start_time, end_time,
                                            max_interval_time, no_move_time);

  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(1)),
      utils::TimePoint(std::chrono::seconds(5)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(5)),
      utils::TimePoint(std::chrono::seconds(7)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none));

  EXPECT_EQ(intervalMerger.IntersectIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.NotCalculatedIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.IntervalCount(), 2u);
  EXPECT_EQ(intervalMerger.AllMergedIntervalCount(), 1u);

  const auto& intervals = intervalMerger.GetIntervals();
  const auto& interval = intervals[0];

  // first interval
  EXPECT_EQ(interval.is_work, false);
  EXPECT_EQ(interval.driver_status.status, TaximeterStatus::StatusInt::BUSY);
  EXPECT_EQ(
      interval.start_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(1)).time_since_epoch().count());
  EXPECT_EQ(
      interval.end_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(5)).time_since_epoch().count());

  // second interval, not merged because another status.
  const auto& work_interval = intervals[1];
  EXPECT_EQ(work_interval.is_work, true);
  EXPECT_EQ(work_interval.driver_status.status,
            TaximeterStatus::StatusInt::FREE);
  EXPECT_EQ(
      work_interval.start_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(5)).time_since_epoch().count());
  EXPECT_EQ(
      work_interval.end_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(7)).time_since_epoch().count());
}

TEST(DriverStatusIntervalMergerTest, TestNotMergeDifferentIntervals_2) {
  DriverStatusIntervalMerger intervalMerger(start_time, end_time,
                                            max_interval_time, no_move_time);

  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(1)),
      utils::TimePoint(std::chrono::seconds(5)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(7)),
      utils::TimePoint(std::chrono::seconds(8)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none));
  intervalMerger.AddInterval(
      utils::TimePoint(std::chrono::seconds(5)),
      utils::TimePoint(std::chrono::seconds(7)),
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none));

  EXPECT_EQ(intervalMerger.IntersectIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.NotCalculatedIntervalCount(), 0u);
  EXPECT_EQ(intervalMerger.IntervalCount(), 3u);
  EXPECT_EQ(intervalMerger.AllMergedIntervalCount(), 1u);

  const auto& intervals = intervalMerger.GetIntervals();
  const auto& interval = intervals[0];

  // first interval
  EXPECT_EQ(interval.is_work, false);
  EXPECT_EQ(interval.driver_status.status, TaximeterStatus::StatusInt::BUSY);
  EXPECT_EQ(
      interval.start_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(1)).time_since_epoch().count());
  EXPECT_EQ(
      interval.end_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(5)).time_since_epoch().count());

  // second interval, not merged because another status.
  const auto& work_interval = intervals[1];
  EXPECT_EQ(work_interval.is_work, true);
  EXPECT_EQ(work_interval.driver_status.status,
            TaximeterStatus::StatusInt::FREE);
  EXPECT_EQ(
      work_interval.start_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(5)).time_since_epoch().count());
  EXPECT_EQ(
      work_interval.end_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(7)).time_since_epoch().count());

  // third interval, not merged because another status.
  const auto& busy_interval = intervals[2];
  EXPECT_EQ(busy_interval.is_work, false);
  EXPECT_EQ(busy_interval.driver_status.status,
            TaximeterStatus::StatusInt::BUSY);
  EXPECT_EQ(
      busy_interval.start_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(7)).time_since_epoch().count());
  EXPECT_EQ(
      busy_interval.end_time.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(8)).time_since_epoch().count());
}

}  // namespace driver_weariness
}  // namespace helpers
