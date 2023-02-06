#include <gtest/gtest.h>

#include <chrono>

#include "utils/slots_capacities.hpp"

namespace slots = eats_customer_slots;

namespace eats_customer_slots {
bool operator==(const slots::Slot& lhs, const slots::Slot& rhs) {
  return std::tie(lhs.start, lhs.end, lhs.estimated_delivery_timepoint) ==
         std::tie(rhs.start, rhs.end, rhs.estimated_delivery_timepoint);
}
}  // namespace eats_customer_slots

namespace {
slots::models::IntervalCapacity MakeIntervalCapacity(
    std::chrono::system_clock::time_point start,
    std::chrono::system_clock::time_point end, size_t capacity) {
  slots::models::IntervalCapacity interval;
  interval.interval_start = storages::postgres::TimePointTz{start};
  interval.interval_end = storages::postgres::TimePointTz{end};
  interval.capacity = capacity;
  return interval;
}
}  // namespace

/**
 * |-------- slot -------|
 * |--int1---||---int2---|
 */
TEST(SlotsCapacities, TwoFullIntervalsInOneSlot) {
  const auto now = std::chrono::system_clock::now();
  const auto interval1 =
      MakeIntervalCapacity(now, now + std::chrono::hours(1), 10);
  const auto interval2 = MakeIntervalCapacity(now + std::chrono::hours(1),
                                              now + std::chrono::hours(2), 10);

  slots::Slot slot;
  slot.start = now;
  slot.end = now + std::chrono::hours(2);
  slot.estimated_delivery_timepoint = now + std::chrono::minutes(30);

  const auto result =
      slots::CalculateSlotsCapacities({slot}, {{interval1, interval2}});

  ASSERT_EQ(result.size(), 1);
  EXPECT_EQ(result[0].slot, slot);
  EXPECT_EQ(result[0].capacity, 20);
}

/**
 *       |--slot--|
 * |--int1---||---int2---|
 */
TEST(SlotsCapacities, TwoIntervalsOverlapOneSlot) {
  const auto now = std::chrono::system_clock::now();
  const auto interval1 =
      MakeIntervalCapacity(now, now + std::chrono::hours(1), 17);
  const auto interval2 = MakeIntervalCapacity(now + std::chrono::hours(1),
                                              now + std::chrono::hours(2), 10);

  slots::Slot slot;
  slot.start = now + std::chrono::minutes(30);
  slot.end = now + std::chrono::minutes(90);
  slot.estimated_delivery_timepoint = now + std::chrono::minutes(60);

  const auto result =
      slots::CalculateSlotsCapacities({slot}, {{interval1, interval2}});

  ASSERT_EQ(result.size(), 1);
  EXPECT_EQ(result[0].slot, slot);
  EXPECT_EQ(result[0].capacity, 13);
}

/**
 *           |--slot--|
 * |--int1---|        |---int2---|
 */
TEST(SlotsCapacities, TwoIntervalsDoNotIntersectOneSlot) {
  const auto now = std::chrono::system_clock::now();
  const auto interval1 =
      MakeIntervalCapacity(now, now + std::chrono::hours(1), 17);
  const auto interval2 = MakeIntervalCapacity(now + std::chrono::hours(2),
                                              now + std::chrono::hours(3), 10);

  slots::Slot slot;
  slot.start = now + std::chrono::hours(1);
  slot.end = now + std::chrono::hours(2);
  slot.estimated_delivery_timepoint = now + std::chrono::minutes(90);

  const auto result =
      slots::CalculateSlotsCapacities({slot}, {{interval1, interval2}});

  ASSERT_EQ(result.size(), 1);
  EXPECT_EQ(result[0].slot, slot);
  EXPECT_EQ(result[0].capacity, 0);
}

TEST(SlotsCapacities, NoIntervals) {
  const auto now = std::chrono::system_clock::now();

  slots::Slot slot;
  slot.start = now + std::chrono::hours(1);
  slot.end = now + std::chrono::hours(2);
  slot.estimated_delivery_timepoint = now + std::chrono::minutes(90);

  const auto result = slots::CalculateSlotsCapacities({slot}, std::nullopt);

  ASSERT_EQ(result.size(), 1);
  EXPECT_EQ(result[0].slot, slot);
  EXPECT_EQ(result[0].capacity,
            std::numeric_limits<decltype(result[0].capacity)>::max());
}
