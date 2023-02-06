#include <gtest/gtest.h>

#include <models/status_history.hpp>
#include <utils/driver_weariness/work_interval_merger.hpp>

namespace work_interval_merger_test {

namespace {

using tracker_internal::DStatus;
using tracker_internal::TaximeterStatus;

const auto now = utils::TimePoint(utils::TimePoint(std::chrono::minutes(26)));
const auto check_period = std::chrono::minutes(25);
const auto start_timepoint = now - check_period;
const auto max_work_time = std::chrono::minutes(20);
const auto max_work_time_seconds =
    std::chrono::duration_cast<std::chrono::seconds>(max_work_time);
const auto max_interval_time = std::chrono::minutes(5);
const auto status_free_no_move_time = std::chrono::minutes(5);
const auto driver_status_free =
    models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::FREE,
                         DStatus::Name::FREE, false, false, boost::none);
const auto min_block_time = std::chrono::minutes(5);

}  // namespace

TEST(WorkIntervalMerger, test_simple_calc) {
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(20)),
                              utils::TimePoint(std::chrono::minutes(22)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (2 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1140);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(23)),
                              utils::TimePoint(std::chrono::minutes(24)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (3 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1140);
  EXPECT_EQ(work_int_merger.IntervalCount(), 2u);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(25)),
                              utils::TimePoint(std::chrono::minutes(26)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (4 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1140);
  EXPECT_EQ(work_int_merger.IntervalCount(), 3u);
}

TEST(WorkIntervalMerger, test_merge_two_interval_at_end) {
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(20)),
                              utils::TimePoint(std::chrono::minutes(24)),
                              driver_status_free);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(23)),
                              utils::TimePoint(std::chrono::minutes(25)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (5 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1140);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);
}

TEST(WorkIntervalMerger, test_merge_two_interval_at_begin) {
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(23)),
                              utils::TimePoint(std::chrono::minutes(25)),
                              driver_status_free);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(20)),
                              utils::TimePoint(std::chrono::minutes(24)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (5 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1140);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);
}

TEST(WorkIntervalMerger, test_double_add_interval) {
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(20)),
                              utils::TimePoint(std::chrono::minutes(25)),
                              driver_status_free);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(20)),
                              utils::TimePoint(std::chrono::minutes(25)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (5 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1140);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);
}

TEST(WorkIntervalMerger, test_merge_one_point) {
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(20)),
                              utils::TimePoint(std::chrono::minutes(22)),
                              driver_status_free);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(22)),
                              utils::TimePoint(std::chrono::minutes(25)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (5 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1140);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);
}

TEST(WorkIntervalMerger, test_merge_three_to_one_one_point) {
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(20)),
                              utils::TimePoint(std::chrono::minutes(22)),
                              driver_status_free);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(23)),
                              utils::TimePoint(std::chrono::minutes(25)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (4 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1140);
  EXPECT_EQ(work_int_merger.IntervalCount(), 2u);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(22)),
                              utils::TimePoint(std::chrono::minutes(23)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (5 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1140);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);
}

TEST(WorkIntervalMerger, test_merge_three_to_one) {
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(20)),
                              utils::TimePoint(std::chrono::minutes(22)),
                              driver_status_free);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(23)),
                              utils::TimePoint(std::chrono::minutes(25)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (4 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1140);
  EXPECT_EQ(work_int_merger.IntervalCount(), 2u);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(21)),
                              utils::TimePoint(std::chrono::minutes(24)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (5 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1140);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);
}

TEST(WorkIntervalMerger, test_merge_three_to_one_one_point_on_bound) {
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(20)),
                              utils::TimePoint(std::chrono::minutes(22)),
                              driver_status_free);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(23)),
                              utils::TimePoint(std::chrono::minutes(25)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (4 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1140);
  EXPECT_EQ(work_int_merger.IntervalCount(), 2u);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(21)),
                              utils::TimePoint(std::chrono::minutes(25)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (5 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1140);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);
}

TEST(WorkIntervalMerger, test_merge_big_after_small) {
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(22)),
                              utils::TimePoint(std::chrono::minutes(24)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (2 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1260);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(20)),
                              utils::TimePoint(std::chrono::minutes(25)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (5 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1140);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);
}

TEST(WorkIntervalMerger, test_merge_small_after_big) {
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(20)),
                              utils::TimePoint(std::chrono::minutes(25)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (5 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1140);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(22)),
                              utils::TimePoint(std::chrono::minutes(24)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (5 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1140);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);
}

TEST(WorkIntervalMerger, test_merge_big_after_smalls) {
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(21)),
                              utils::TimePoint(std::chrono::minutes(22)),
                              driver_status_free);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(23)),
                              utils::TimePoint(std::chrono::minutes(24)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (2 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1200);
  EXPECT_EQ(work_int_merger.IntervalCount(), 2u);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(20)),
                              utils::TimePoint(std::chrono::minutes(25)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (5 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1140);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);
}

TEST(WorkIntervalMerger, test_merge_three_to_one_with_inside_small) {
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(19)),
                              utils::TimePoint(std::chrono::minutes(21)),
                              driver_status_free);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(22)),
                              utils::TimePoint(std::chrono::minutes(23)),
                              driver_status_free);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(24)),
                              utils::TimePoint(std::chrono::minutes(26)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (5 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1080);
  EXPECT_EQ(work_int_merger.IntervalCount(), 3u);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(20)),
                              utils::TimePoint(std::chrono::minutes(25)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (7 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1080);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);
}

TEST(WorkIntervalMerger, test_add_only_work_intervals) {
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  const auto driver_status_busy =
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, boost::none);
  const auto driver_status_off =
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::OFF,
                           DStatus::Name::VERYBUSY, false, false, boost::none);
  const auto driver_status_unknown = models::DriverStatus(
      utils::TimePoint(), TaximeterStatus::StatusInt::UNKNOWN_STATUS,
      DStatus::Name::VERYBUSY, false, false, boost::none);
  const auto driver_status_free_tired =
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, true, false, boost::none);
  const auto driver_status_order_busy_tired = models::DriverStatus(
      utils::TimePoint(), TaximeterStatus::StatusInt::ORDER_BUSY,
      DStatus::Name::VERYBUSY, true, false, boost::none);
  const auto driver_status_order_free_tired = models::DriverStatus(
      utils::TimePoint(), TaximeterStatus::StatusInt::ORDER_FREE,
      DStatus::Name::VERYBUSY, true, false, boost::none);
  const auto driver_status_free =
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none);
  const auto driver_status_order_busy = models::DriverStatus(
      utils::TimePoint(), TaximeterStatus::StatusInt::ORDER_BUSY,
      DStatus::Name::VERYBUSY, false, false, boost::none);
  const auto driver_status_order_free = models::DriverStatus(
      utils::TimePoint(), TaximeterStatus::StatusInt::ORDER_FREE,
      DStatus::Name::VERYBUSY, false, false, boost::none);

  const auto driver_status_free_not_active_reposition =
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::VERYBUSY, false, false, false);
  const auto driver_status_free_but_busy =
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::VERYBUSY, false, false, boost::none);
  const auto driver_status_busy_active_reposition =
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::VERYBUSY, false, false, true);
  const auto driver_status_free_active_reposition =
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::VERYBUSY, false, false, true);
  const auto driver_status_unknown_active_reposition = models::DriverStatus(
      utils::TimePoint(), TaximeterStatus::StatusInt::UNKNOWN_STATUS,
      DStatus::Name::VERYBUSY, false, false, true);

  // not working intervals
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(7)),
                              utils::TimePoint(std::chrono::minutes(8)),
                              driver_status_free_not_active_reposition);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(8)),
                              utils::TimePoint(std::chrono::minutes(9)),
                              driver_status_unknown_active_reposition);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(9)),
                              utils::TimePoint(std::chrono::minutes(10)),
                              driver_status_free_but_busy);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(10)),
                              utils::TimePoint(std::chrono::minutes(11)),
                              driver_status_busy);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(12)),
                              utils::TimePoint(std::chrono::minutes(13)),
                              driver_status_off);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(14)),
                              utils::TimePoint(std::chrono::minutes(15)),
                              driver_status_unknown);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(16)),
                              utils::TimePoint(std::chrono::minutes(17)),
                              driver_status_free_tired);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count());
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 0);
  EXPECT_EQ(work_int_merger.IntervalCount(), 0u);

  // working intervals
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(16)),
                              utils::TimePoint(std::chrono::minutes(17)),
                              driver_status_order_busy_tired);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(18)),
                              utils::TimePoint(std::chrono::minutes(19)),
                              driver_status_order_free_tired);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(20)),
                              utils::TimePoint(std::chrono::minutes(21)),
                              driver_status_free);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(22)),
                              utils::TimePoint(std::chrono::minutes(23)),
                              driver_status_order_busy);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(24)),
                              utils::TimePoint(std::chrono::minutes(25)),
                              driver_status_order_free);
  work_int_merger.AddInterval(
      utils::TimePoint(std::chrono::minutes(25)),
      utils::TimePoint(std::chrono::minutes(25) + std::chrono::seconds(30)),
      driver_status_busy_active_reposition);
  work_int_merger.AddInterval(
      utils::TimePoint(std::chrono::minutes(25) + std::chrono::seconds(30)),
      utils::TimePoint(std::chrono::minutes(26)),
      driver_status_free_active_reposition);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (6 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 900);
  EXPECT_EQ(work_int_merger.IntervalCount(), 5u);
}

TEST(WorkIntervalMerger, test_zero_interval) {
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(10)),
                              utils::TimePoint(std::chrono::minutes(10)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count());
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 0);
  EXPECT_EQ(work_int_merger.IntervalCount(), 0u);
}

TEST(WorkIntervalMerger, test_time_to_start_bound_between_interval_max_time) {
  auto small_max_work_time = std::chrono::minutes(5);
  auto small_min_block_time = std::chrono::minutes(2);
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, small_max_work_time, max_interval_time,
          small_min_block_time, status_free_no_move_time, boost::none);

  // not working time between 1 minute and 2 minute.
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(2)),
                              utils::TimePoint(std::chrono::minutes(7)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(), 0);
  // 1 minute interval to work start and 2 minutes min block time.
  EXPECT_EQ(work_int_merger.GetBlockTime().count(), 180);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);
}

TEST(WorkIntervalMerger,
     test_time_to_start_bound_between_interval_more_than_max_time) {
  auto small_max_work_time = std::chrono::minutes(5);
  auto small_min_block_time = std::chrono::minutes(2);
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, small_max_work_time, max_interval_time,
          small_min_block_time, status_free_no_move_time, boost::none);

  // not working time between 1 minute and 2 minute.
  // max work time exceed max by 3 minutes
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(2)),
                              utils::TimePoint(std::chrono::minutes(5)),
                              driver_status_free);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(5)),
                              utils::TimePoint(std::chrono::minutes(10)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(), 0);

  // 1 minute interval to work start + 2 minutes min block time + 3 minutes
  // overlimit max work time
  EXPECT_EQ(work_int_merger.GetBlockTime().count(), 360);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);
}

TEST(WorkIntervalMerger,
     test_time_to_start_when_min_block_time_equal_max_work_time) {
  auto small_max_work_time = std::chrono::minutes(5);
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, small_max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  // not working time between 1 minute and 2 minute.
  // max work time exceed max by 3 minutes
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(2)),
                              utils::TimePoint(std::chrono::minutes(5)),
                              driver_status_free);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(5)),
                              utils::TimePoint(std::chrono::minutes(10)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(), 0);

  // overlimit 3 minutes + min block time 5 minutes = 8 minutes.
  EXPECT_EQ(work_int_merger.GetBlockTime().count(), 480);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);
}

TEST(WorkIntervalMerger, test_time_to_start_interval_at_bound_max_time) {
  auto small_max_work_time = std::chrono::minutes(5);
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, small_max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  // work interval at bound
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(1)),
                              utils::TimePoint(std::chrono::minutes(6)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(), 0);

  // 5 minutes min block time + 0 minutes, because no bound to start work in
  // interval
  EXPECT_EQ(work_int_merger.GetBlockTime().count(), 300);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);
}

TEST(WorkIntervalMerger,
     test_time_to_start_interval_at_bound_more_than_max_time) {
  auto small_max_work_time = std::chrono::minutes(5);
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, small_max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  // work interval at bound, but work time exceed max work time by 4 minutes
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(1)),
                              utils::TimePoint(std::chrono::minutes(5)),
                              driver_status_free);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(5)),
                              utils::TimePoint(std::chrono::minutes(10)),
                              driver_status_free);
  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(), 0);

  // 5 minutes min block time + 4 minutes exceed max work time
  EXPECT_EQ(work_int_merger.GetBlockTime().count(), 540);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);
}

TEST(WorkIntervalMerger, test_free_no_move_intervals) {
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, boost::none);

  const auto driver_status_free =
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none);
  const auto driver_status_free_no_move =
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, true, boost::none);
  const auto driver_status_busy_no_move =
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::BUSY,
                           DStatus::Name::FREE, false, true, boost::none);
  const auto driver_status_order_free_no_move = models::DriverStatus(
      utils::TimePoint(), TaximeterStatus::StatusInt::ORDER_FREE,
      DStatus::Name::FREE, false, true, boost::none);
  const auto driver_status_unknown_no_move = models::DriverStatus(
      utils::TimePoint(), TaximeterStatus::StatusInt::UNKNOWN_STATUS,
      DStatus::Name::VERYBUSY, false, true, boost::none);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(10)),
                              utils::TimePoint(std::chrono::minutes(11)),
                              driver_status_free);
  EXPECT_FALSE(work_int_merger.GetStatusFreeNoMoveTimePoint());
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(11)),
                              utils::TimePoint(std::chrono::minutes(12)),
                              driver_status_free_no_move);
  EXPECT_EQ(*work_int_merger.GetStatusFreeNoMoveTimePoint(),
            utils::TimePoint(std::chrono::minutes(11)));

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(12)),
                              utils::TimePoint(std::chrono::minutes(13)),
                              driver_status_busy_no_move);
  EXPECT_EQ(*work_int_merger.GetStatusFreeNoMoveTimePoint(),
            utils::TimePoint(std::chrono::minutes(11)));

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(13)),
                              utils::TimePoint(std::chrono::minutes(14)),
                              driver_status_order_free_no_move);
  EXPECT_EQ(*work_int_merger.GetStatusFreeNoMoveTimePoint(),
            utils::TimePoint(std::chrono::minutes(11)));

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(14)),
                              utils::TimePoint(std::chrono::minutes(15)),
                              driver_status_free);
  EXPECT_FALSE(work_int_merger.GetStatusFreeNoMoveTimePoint());

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(15)),
                              utils::TimePoint(std::chrono::minutes(16)),
                              driver_status_free_no_move);
  EXPECT_EQ(*work_int_merger.GetStatusFreeNoMoveTimePoint(),
            utils::TimePoint(std::chrono::minutes(15)));

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(16)),
                              utils::TimePoint(std::chrono::minutes(17)),
                              driver_status_unknown_no_move);
  EXPECT_FALSE(work_int_merger.GetStatusFreeNoMoveTimePoint());
}

TEST(WorkIntervalMerger, test_work_rest_time_middle) {
  auto work_rest_time = std::chrono::minutes(5);
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, work_rest_time);

  const auto driver_status_free =
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(10)),
                              utils::TimePoint(std::chrono::minutes(11)),
                              driver_status_free);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(22)),
                              utils::TimePoint(std::chrono::minutes(25)),
                              driver_status_free);

  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count() - (3 * 60));
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 1260);
  EXPECT_EQ(work_int_merger.IntervalCount(), 1u);
}

TEST(WorkIntervalMerger, test_work_rest_time_in_the_end) {
  auto work_rest_time = std::chrono::minutes(5);
  auto work_int_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_timepoint, now, max_work_time, max_interval_time,
          min_block_time, status_free_no_move_time, work_rest_time);

  const auto driver_status_free =
      models::DriverStatus(utils::TimePoint(), TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none);

  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(10)),
                              utils::TimePoint(std::chrono::minutes(11)),
                              driver_status_free);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(12)),
                              utils::TimePoint(std::chrono::minutes(15)),
                              driver_status_free);
  work_int_merger.AddInterval(utils::TimePoint(std::chrono::minutes(18)),
                              utils::TimePoint(std::chrono::minutes(21)),
                              driver_status_free);

  work_int_merger.CalculateTimes();

  EXPECT_EQ(work_int_merger.GetRemainingTime().count(),
            max_work_time_seconds.count());
  EXPECT_EQ(work_int_merger.GetTimeToFirstInterval().count(), 0);
  EXPECT_EQ(work_int_merger.IntervalCount(), 0u);
}

}  // namespace work_interval_merger_test
