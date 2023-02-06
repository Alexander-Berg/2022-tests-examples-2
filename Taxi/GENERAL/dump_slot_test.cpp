#include <gtest/gtest.h>

#include <userver/dump/test_helpers.hpp>

#include "caches/place_orders_per_slot_cache.hpp"

namespace eats_customer_slots {
constexpr bool operator==(const eats_customer_slots::Slot& lhs,
                          const eats_customer_slots::Slot& rhs) {
  return std::tie(lhs.start, lhs.end, lhs.estimated_delivery_timepoint) ==
         std::tie(rhs.start, rhs.end, rhs.estimated_delivery_timepoint);
}
}  // namespace eats_customer_slots

namespace {
eats_customer_slots::Slot MakeSlot() {
  eats_customer_slots::Slot slot;
  slot.start = std::chrono::system_clock::now();
  slot.end = slot.start + std::chrono::hours(2);
  slot.estimated_delivery_timepoint = std::chrono::system_clock::now();

  return slot;
}
}  // namespace

TEST(DumpSlotTest, ReadWriteTest) {
  caches::PlaceOrdersPerSlotCacheDataType data;
  const int64_t place_id = 1;
  const auto slot = MakeSlot();
  const size_t orders_count = 10;

  data[place_id][slot] = orders_count;

  dump::TestWriteReadCycle(data);
}
