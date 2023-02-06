#include <gtest/gtest.h>

#include <models/status_history.hpp>
#include <utils/driver_weariness/work_calc.hpp>

namespace driver_weariness_test {

using tracker_internal::DStatus;
using tracker_internal::TaximeterStatus;

namespace {
auto long_check_period = std::chrono::minutes(50);
auto check_period = std::chrono::minutes(25);
auto max_work_time = std::chrono::minutes(20);
auto max_interval_time = std::chrono::minutes(5);
auto status_prolong_time = std::chrono::minutes(5);
auto max_work_time_seconds =
    std::chrono::duration_cast<std::chrono::seconds>(max_work_time);
auto min_block_time = std::chrono::minutes(5);
auto status_free_no_move_time = std::chrono::minutes(1);
}  // namespace

TEST(DriverWeariness, find_begin_status) {
  models::DriverStatuses statuses = {
      models::DriverStatus{utils::TimePoint(std::chrono::seconds(1))},
      models::DriverStatus{utils::TimePoint(std::chrono::seconds(4))},
      models::DriverStatus{utils::TimePoint(std::chrono::seconds(10))},
      models::DriverStatus{utils::TimePoint(std::chrono::seconds(16))},
      models::DriverStatus(utils::TimePoint(std::chrono::seconds(20)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none),
      models::DriverStatus{utils::TimePoint(std::chrono::seconds(24))}};

  // after all intervals
  const auto& begin_info = helpers::driver_weariness::FindBeginStatus(
      statuses, utils::TimePoint(std::chrono::seconds(25)));
  EXPECT_FALSE(begin_info);

  // before all intervals
  const auto& begin_info_before =
      helpers::driver_weariness::FindBeginStatus(statuses, utils::TimePoint());
  EXPECT_EQ(
      begin_info_before->time_point.time_since_epoch().count(),
      utils::TimePoint(std::chrono::seconds(1)).time_since_epoch().count());

  // at interval bound and end
  auto timepoint_bound_end = utils::TimePoint(std::chrono::seconds(24));
  const auto& begin_info2 =
      helpers::driver_weariness::FindBeginStatus(statuses, timepoint_bound_end);
  EXPECT_EQ(begin_info2->time_point.time_since_epoch().count(),
            timepoint_bound_end.time_since_epoch().count());

  // at interval bound
  auto timepoint_bound = utils::TimePoint(std::chrono::seconds(16));
  const auto& begin_info3 =
      helpers::driver_weariness::FindBeginStatus(statuses, timepoint_bound);
  EXPECT_EQ(begin_info3->time_point.time_since_epoch().count(),
            timepoint_bound.time_since_epoch().count());

  // in the middle of interval
  auto timepoint_middle = utils::TimePoint(std::chrono::seconds(21));
  const auto& begin_info4 =
      helpers::driver_weariness::FindBeginStatus(statuses, timepoint_middle);
  auto driver_status = statuses[begin_info4->begin_idx];
  EXPECT_EQ(begin_info4->time_point.time_since_epoch().count(),
            timepoint_middle.time_since_epoch().count());
  EXPECT_EQ(driver_status.status, TaximeterStatus::StatusInt::FREE);
  EXPECT_EQ(driver_status.is_blocked, false);
}

TEST(DriverWeariness, calculate_work_time_no_intevals) {
  models::DriverStatuses statuses = {
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(1))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(2))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(3))},
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(4)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none),
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(5))}};

  auto now = utils::TimePoint(utils::TimePoint(std::chrono::minutes(50)));
  auto start_time = now - check_period;

  auto work_interval_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_time, now, max_work_time, max_interval_time, min_block_time,
          status_free_no_move_time, boost::none);
  ;
  auto work_info = helpers::driver_weariness::CalcDriverWorkingTime(
      work_interval_merger, statuses, now, check_period, max_work_time,
      status_prolong_time);
  EXPECT_EQ(work_info.work_time.count(), 0);
  EXPECT_EQ(work_info.remaining_time.count(), max_work_time_seconds.count());
  EXPECT_EQ(work_info.last_status_timepoint.time_since_epoch().count(), 0);
  EXPECT_EQ(work_info.last_work_timepoint.time_since_epoch().count(), 0);
}

TEST(DriverWeariness, calculate_work_time_good_interval) {
  models::DriverStatuses statuses = {
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(21))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(22))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(23))},
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(24)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none),
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(25))}};

  auto now = utils::TimePoint(utils::TimePoint(std::chrono::minutes(26)));
  auto start_time = now - check_period;
  auto time_to_time_work_secs =
      std::chrono::duration_cast<std::chrono::seconds>(
          utils::TimePoint(std::chrono::minutes(24)) - start_time);

  auto work_interval_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_time, now, max_work_time, max_interval_time, min_block_time,
          status_free_no_move_time, boost::none);
  auto work_info = helpers::driver_weariness::CalcDriverWorkingTime(
      work_interval_merger, statuses, now, check_period, max_work_time,
      status_prolong_time);
  EXPECT_EQ(work_info.work_time.count(), 60);
  EXPECT_EQ(work_info.remaining_time.count(), 1140);
  EXPECT_EQ(work_interval_merger.GetTimeToFirstInterval().count(),
            time_to_time_work_secs.count());
  EXPECT_EQ(
      work_info.last_status_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(25)).time_since_epoch().count());
  EXPECT_EQ(
      work_info.last_work_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(25)).time_since_epoch().count());
}

TEST(DriverWeariness, calculate_work_time_check_status_prolong) {
  models::DriverStatuses statuses = {
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(20))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(22))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(23))},
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(24)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none),
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(25)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none)};

  auto now = utils::TimePoint(utils::TimePoint(std::chrono::minutes(26)));
  auto start_time = now - check_period;
  auto time_to_time_work_secs =
      std::chrono::duration_cast<std::chrono::seconds>(
          utils::TimePoint(std::chrono::minutes(24)) - start_time);

  auto work_interval_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_time, now, max_work_time, max_interval_time, min_block_time,
          status_free_no_move_time, boost::none);
  auto work_info = helpers::driver_weariness::CalcDriverWorkingTime(
      work_interval_merger, statuses, now, check_period, max_work_time,
      status_prolong_time);
  EXPECT_EQ(work_info.work_time.count(), 120);
  EXPECT_EQ(work_info.remaining_time.count(), 1080);
  EXPECT_EQ(work_interval_merger.GetTimeToFirstInterval().count(),
            time_to_time_work_secs.count());
  EXPECT_EQ(
      work_info.last_status_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(26)).time_since_epoch().count());
  EXPECT_EQ(
      work_info.last_work_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(26)).time_since_epoch().count());
}

TEST(DriverWeariness, calculate_two_profiles) {
  models::DriverStatuses statuses = {
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(21))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(22))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(23))},
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(24)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none),
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(25))}};

  models::DriverStatuses statuses2 = {
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(31)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none),
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(32))},
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(33)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none),
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(34)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none),
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(35))}};

  auto now = utils::TimePoint(utils::TimePoint(std::chrono::minutes(51)));
  auto start_time = now - long_check_period;
  auto time_to_time_work_secs =
      std::chrono::duration_cast<std::chrono::seconds>(
          utils::TimePoint(std::chrono::minutes(24)) - start_time);

  auto work_interval_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_time, now, max_work_time, max_interval_time, min_block_time,
          status_free_no_move_time, boost::none);
  helpers::driver_weariness::CalcDriverWorkingTime(
      work_interval_merger, statuses, now, long_check_period, max_work_time,
      status_prolong_time);
  auto work_info = helpers::driver_weariness::CalcDriverWorkingTime(
      work_interval_merger, statuses2, now, long_check_period, max_work_time,
      status_prolong_time);
  EXPECT_EQ(work_info.work_time.count(), 240);
  EXPECT_EQ(work_info.remaining_time.count(), 960);
  EXPECT_EQ(work_interval_merger.GetTimeToFirstInterval().count(),
            time_to_time_work_secs.count());
  EXPECT_EQ(
      work_info.last_status_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(35)).time_since_epoch().count());
  EXPECT_EQ(
      work_info.last_work_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(35)).time_since_epoch().count());
}

TEST(DriverWeariness, calculate_two_profile_with_merged_intervals) {
  models::DriverStatuses statuses = {
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(21))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(22))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(23))},
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(24)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none),
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(25))}};

  models::DriverStatuses statuses2 = {
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(21)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none),
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(25))},
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(33)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none),
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(34)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none),
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(35))}};

  auto now = utils::TimePoint(utils::TimePoint(std::chrono::minutes(51)));
  auto start_time = now - long_check_period;
  auto time_to_time_work_secs =
      std::chrono::duration_cast<std::chrono::seconds>(
          utils::TimePoint(std::chrono::minutes(21)) - start_time);

  auto work_interval_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_time, now, max_work_time, max_interval_time, min_block_time,
          status_free_no_move_time, boost::none);
  helpers::driver_weariness::CalcDriverWorkingTime(
      work_interval_merger, statuses, now, long_check_period, max_work_time,
      status_prolong_time);
  auto work_info = helpers::driver_weariness::CalcDriverWorkingTime(
      work_interval_merger, statuses2, now, long_check_period, max_work_time,
      status_prolong_time);
  EXPECT_EQ(work_info.work_time.count(), 360);
  EXPECT_EQ(work_info.remaining_time.count(), 840);
  EXPECT_EQ(work_interval_merger.GetTimeToFirstInterval().count(),
            time_to_time_work_secs.count());
  EXPECT_EQ(
      work_info.last_status_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(35)).time_since_epoch().count());
  EXPECT_EQ(
      work_info.last_work_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(35)).time_since_epoch().count());
}

TEST(DriverWeariness, calculate_work_time_with_no_move_free) {
  models::DriverStatuses statuses = {
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(21))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(22))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(23))},
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(24)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, true, boost::none),
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(25)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, true, boost::none),
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(26)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, true, boost::none),
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(27)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, true, boost::none),
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(28))}};

  auto now = utils::TimePoint(utils::TimePoint(std::chrono::minutes(51)));
  auto start_time = now - long_check_period;
  auto time_to_time_work_secs =
      std::chrono::duration_cast<std::chrono::seconds>(
          utils::TimePoint(std::chrono::minutes(24)) - start_time);

  auto work_interval_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_time, now, max_work_time, max_interval_time, min_block_time,
          status_free_no_move_time, boost::none);
  auto work_info = helpers::driver_weariness::CalcDriverWorkingTime(
      work_interval_merger, statuses, now, long_check_period, max_work_time,
      status_prolong_time);
  EXPECT_EQ(work_info.work_time.count(), 60);
  EXPECT_EQ(work_info.remaining_time.count(), 1140);
  EXPECT_EQ(work_interval_merger.GetTimeToFirstInterval().count(),
            time_to_time_work_secs.count());
  EXPECT_EQ(
      work_info.last_status_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(28)).time_since_epoch().count());
  EXPECT_EQ(
      work_info.last_work_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(25)).time_since_epoch().count());
}

TEST(DriverWeariness, calculate_work_time_with_no_move_free_two_profiles) {
  models::DriverStatuses statuses = {
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(33))},
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(34)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, true, boost::none),
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(35)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, true, boost::none),
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(36)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, true, boost::none),
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(37)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, true, boost::none),
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(38))}};

  models::DriverStatuses statuses2 = {
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(21))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(22))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(23))},
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(24)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, true, boost::none),
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(25)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, true, boost::none),
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(26)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, true, boost::none),
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(27)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, true, boost::none),
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(28))}};

  auto now = utils::TimePoint(utils::TimePoint(std::chrono::minutes(51)));
  auto start_time = now - long_check_period;
  auto time_to_time_work_secs =
      std::chrono::duration_cast<std::chrono::seconds>(
          utils::TimePoint(std::chrono::minutes(24)) - start_time);
  auto time_to_time_first_profile_work_secs =
      std::chrono::duration_cast<std::chrono::seconds>(
          utils::TimePoint(std::chrono::minutes(34)) - start_time);

  auto work_interval_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_time, now, max_work_time, max_interval_time, min_block_time,
          status_free_no_move_time, boost::none);
  auto work_info = helpers::driver_weariness::CalcDriverWorkingTime(
      work_interval_merger, statuses, now, long_check_period, max_work_time,
      status_prolong_time);

  EXPECT_EQ(work_info.work_time.count(), 60);
  EXPECT_EQ(work_info.remaining_time.count(), 1140);
  EXPECT_EQ(work_interval_merger.GetTimeToFirstInterval().count(),
            time_to_time_first_profile_work_secs.count());
  EXPECT_EQ(
      work_info.last_status_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(38)).time_since_epoch().count());
  EXPECT_EQ(
      work_info.last_work_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(35)).time_since_epoch().count());

  auto work_info2 = helpers::driver_weariness::CalcDriverWorkingTime(
      work_interval_merger, statuses2, now, long_check_period, max_work_time,
      status_prolong_time);

  EXPECT_EQ(work_info2.work_time.count(), 120);
  EXPECT_EQ(work_info2.remaining_time.count(), 1080);
  EXPECT_EQ(work_interval_merger.GetTimeToFirstInterval().count(),
            time_to_time_work_secs.count());
  EXPECT_EQ(
      work_info2.last_status_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(38)).time_since_epoch().count());
  EXPECT_EQ(
      work_info2.last_work_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(35)).time_since_epoch().count());
}

TEST(DriverWeariness, calculate_work_time_with_rest_middle) {
  models::DriverStatuses statuses = {
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(1))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(2))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(30))},
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(20)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none),
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(30)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none),
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(35))},
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(40)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none),
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(45))}};

  auto work_rest_time = std::chrono::minutes(10);
  auto now = utils::TimePoint(utils::TimePoint(std::chrono::minutes(51)));
  auto start_time = now - long_check_period;

  auto work_interval_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_time, now, max_work_time, max_interval_time, min_block_time,
          status_free_no_move_time, work_rest_time);
  auto work_info = helpers::driver_weariness::CalcDriverWorkingTime(
      work_interval_merger, statuses, now, check_period, max_work_time,
      status_prolong_time);
  EXPECT_EQ(work_info.work_time.count(), 300);
  EXPECT_EQ(work_info.remaining_time.count(),
            max_work_time_seconds.count() - 300);
  EXPECT_EQ(
      work_info.last_status_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(45)).time_since_epoch().count());
  EXPECT_EQ(
      work_info.last_work_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(45)).time_since_epoch().count());
}

TEST(DriverWeariness, calculate_work_time_with_rest_in_the_end) {
  models::DriverStatuses statuses = {
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(1))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(2))},
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(30))},
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(20)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none),
      models::DriverStatus(utils::TimePoint(std::chrono::minutes(30)),
                           TaximeterStatus::StatusInt::FREE,
                           DStatus::Name::FREE, false, false, boost::none),
      models::DriverStatus{utils::TimePoint(std::chrono::minutes(35))}};

  auto work_rest_time = std::chrono::minutes(10);
  auto now = utils::TimePoint(utils::TimePoint(std::chrono::minutes(51)));
  auto start_time = now - long_check_period;

  auto work_interval_merger =
      helpers::driver_weariness::WorkIntervalMerger::CreateNew(
          start_time, now, max_work_time, max_interval_time, min_block_time,
          status_free_no_move_time, work_rest_time);
  auto work_info = helpers::driver_weariness::CalcDriverWorkingTime(
      work_interval_merger, statuses, now, check_period, max_work_time,
      status_prolong_time);
  EXPECT_EQ(work_info.work_time.count(), 0);
  EXPECT_EQ(work_info.remaining_time.count(), max_work_time_seconds.count());
  EXPECT_EQ(
      work_info.last_status_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(35)).time_since_epoch().count());
  EXPECT_EQ(
      work_info.last_work_timepoint.time_since_epoch().count(),
      utils::TimePoint(std::chrono::minutes(35)).time_since_epoch().count());
}

}  // namespace driver_weariness_test
