#include <models/status_interval_merger.hpp>

#include <gtest/gtest.h>

namespace models {

namespace {

using handlers::OrderStatus;
using handlers::Status;
using handlers::StatusItem;

const auto kStartTime = models::TimePoint(std::chrono::minutes(5));
const auto kEndTime = models::TimePoint(std::chrono::minutes(25));
const auto kMaxIntervalTime = std::chrono::minutes(10);

const std::vector<OrderStatus> kNonWorking{OrderStatus::kComplete,
                                           OrderStatus::kNone};
const std::vector<OrderStatus> kWorking{OrderStatus::kDriving,
                                        OrderStatus::kCancelled};

const std::unordered_set<Status> kDefaultWorkingDriverStatuses{
    Status::kOnline,
    Status::kBusy,
};

const std::unordered_set<OrderStatus> kDefaultWorkingOrderStatuses{
    OrderStatus::kDriving,
    OrderStatus::kWaiting,
    OrderStatus::kTransporting,
};

StatusItem MakeEvent(
    const int32_t minutes, const Status status,
    const std::optional<std::vector<OrderStatus>> order_statuses) {
  return StatusItem{models::TimePoint(std::chrono::minutes(minutes)), status,
                    order_statuses};
}

StatusInterval MakeInterval(const int32_t start_minutes,
                            const int32_t end_minutes, const bool is_work) {
  return StatusInterval{models::TimePoint(std::chrono::minutes(start_minutes)),
                        models::TimePoint(std::chrono::minutes(end_minutes)),
                        is_work};
}

void CompareData(const std::vector<StatusItem>& sorted_events,
                 std::unordered_set<Status> working_driver_statuses,
                 std::unordered_set<OrderStatus> working_order_statuses,
                 const StatusIntervals& expected_intervals) {
  const StatusIntervalMerger interval_merger{
      kStartTime, kEndTime, kMaxIntervalTime,
      std::move(working_driver_statuses), std::move(working_order_statuses)};

  const auto intervals = interval_merger.TransformStatusEvents(sorted_events);

  EXPECT_EQ(intervals.size(), expected_intervals.size());
  if (intervals.empty()) {
    return;
  }

  for (size_t index = 0; index < intervals.size() - 1; ++index) {
    EXPECT_EQ(intervals[index].start_time,
              expected_intervals[index].start_time);
    EXPECT_EQ(intervals[index].end_time, expected_intervals[index].end_time);
    EXPECT_EQ(intervals[index].is_work, expected_intervals[index].is_work);
  }
}

}  // namespace

TEST(StatusIntervalMergerTest, TestNoTransformOneEvent) {
  CompareData(
      {
          MakeEvent(22, Status::kOnline, kNonWorking),
      },
      kDefaultWorkingDriverStatuses, kDefaultWorkingOrderStatuses, {});
}

TEST(StatusIntervalMergerTest, TestCreateSingleInterval) {
  CompareData(
      {
          MakeEvent(22, Status::kBusy, std::nullopt),
          MakeEvent(24, Status::kBusy, std::nullopt),
      },
      kDefaultWorkingDriverStatuses, kDefaultWorkingOrderStatuses,
      {MakeInterval(22, 24, false)});
}

TEST(StatusIntervalMergerTest, TestTransformEvents) {
  CompareData(
      {
          MakeEvent(5, Status::kBusy,
                    std::vector<OrderStatus>{OrderStatus::kDriving}),
          MakeEvent(9, Status::kOnline, std::nullopt),
          MakeEvent(17, Status::kOnline,
                    std::vector<OrderStatus>{OrderStatus::kDriving}),
          MakeEvent(21, Status::kOffline, std::nullopt),
      },
      kDefaultWorkingDriverStatuses, kDefaultWorkingOrderStatuses,
      {
          MakeInterval(5, 9, true),    //
          MakeInterval(9, 17, false),  //
          MakeInterval(17, 21, true)   //
      });
}

TEST(StatusIntervalMergerTest, TestWorkingOrderStatuses) {
  const std::vector<StatusItem> kSortedEvents{
      MakeEvent(5, Status::kBusy,
                std::vector<OrderStatus>{OrderStatus::kDriving}),
      MakeEvent(9, Status::kOnline,
                std::vector<OrderStatus>{OrderStatus::kWaiting}),
      MakeEvent(17, Status::kOnline,
                std::vector<OrderStatus>{OrderStatus::kTransporting}),
      MakeEvent(21, Status::kOffline, std::nullopt),
  };

  CompareData(kSortedEvents, kDefaultWorkingDriverStatuses,
              kDefaultWorkingOrderStatuses, {MakeInterval(5, 21, true)});

  CompareData(kSortedEvents, kDefaultWorkingDriverStatuses,
              {OrderStatus::kDriving, OrderStatus::kTransporting},
              {
                  MakeInterval(5, 9, true),
                  MakeInterval(9, 17, false),
                  MakeInterval(17, 21, true),
              });

  CompareData(kSortedEvents, {Status::kOnline},
              {OrderStatus::kDriving, OrderStatus::kTransporting},
              {
                  MakeInterval(5, 17, false),
                  MakeInterval(17, 21, true),
              });

  CompareData(kSortedEvents, {Status::kBusy},
              {OrderStatus::kDriving, OrderStatus::kTransporting},
              {
                  MakeInterval(5, 9, true),
                  MakeInterval(9, 21, false),
              });

  CompareData(kSortedEvents, {}, kDefaultWorkingOrderStatuses,
              {
                  MakeInterval(5, 21, false),
              });

  CompareData(kSortedEvents, kDefaultWorkingDriverStatuses,
              {OrderStatus::kTransporting},
              {
                  MakeInterval(5, 17, false),
                  MakeInterval(17, 21, true),
              });

  CompareData(kSortedEvents, kDefaultWorkingDriverStatuses, {},
              {
                  MakeInterval(5, 21, false),
              });
}

TEST(StatusIntervalMergerTest, TestMergeIntervals) {
  CompareData(
      {
          MakeEvent(5, Status::kBusy, kWorking),
          MakeEvent(6, Status::kOnline, kWorking),
          MakeEvent(7, Status::kBusy, kWorking),
          MakeEvent(8, Status::kBusy, kWorking),
          MakeEvent(9, Status::kOnline, kWorking),
          MakeEvent(10, Status::kOnline, kWorking),
          MakeEvent(11, Status::kOffline, std::nullopt),
          MakeEvent(12, Status::kOnline, kNonWorking),
          MakeEvent(13, Status::kBusy, kNonWorking),
          MakeEvent(14, Status::kOffline, std::nullopt),
          MakeEvent(15, Status::kOffline, std::nullopt),
          MakeEvent(16, Status::kBusy, std::nullopt),
          MakeEvent(17, Status::kBusy, std::nullopt),
          MakeEvent(18, Status::kOnline, kWorking),
          MakeEvent(30, Status::kOnline, kWorking),
      },
      kDefaultWorkingDriverStatuses, kDefaultWorkingOrderStatuses,
      {MakeInterval(5, 11, true), MakeInterval(11, 18, false),
       // last status has greater timepoint than merger limit
       MakeInterval(18, 25, true)});
}

TEST(StatusIntervalMergerTest, TestTooLongIntervals) {
  CompareData(
      {
          MakeEvent(5, Status::kBusy, kWorking),
          MakeEvent(6, Status::kOnline, kWorking),
          MakeEvent(17, Status::kOnline, kWorking),
          MakeEvent(18, Status::kOnline, kWorking),
      },
      kDefaultWorkingDriverStatuses, kDefaultWorkingOrderStatuses,
      {MakeInterval(5, 6, true), MakeInterval(17, 28, true)});
}

TEST(StatusIntervalMergerTest, TestAddOutBoundariesIntervals) {
  CompareData(
      {
          MakeEvent(3, Status::kBusy, kWorking),
          MakeEvent(4, Status::kOnline, kWorking),
          MakeEvent(6, Status::kOnline, kNonWorking),
          MakeEvent(16, Status::kBusy, kWorking),
          MakeEvent(24, Status::kOnline, std::nullopt),
          MakeEvent(30, Status::kOffline, std::nullopt),
          MakeEvent(32, Status::kOnline, kWorking),
      },
      kDefaultWorkingDriverStatuses, kDefaultWorkingOrderStatuses,
      {MakeInterval(5, 6, true), MakeInterval(6, 16, false),
       MakeInterval(16, 24, true), MakeInterval(24, 25, false)});
}

}  // namespace models
