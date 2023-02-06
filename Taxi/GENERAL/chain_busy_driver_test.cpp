#include "chain_busy_driver.hpp"

#include <gtest/gtest.h>

bool operator==(const ChainBusyDriver& l, const ChainBusyDriver& r) {
  return l.driver_id == r.driver_id && l.order_id == r.order_id &&
         l.destination == r.destination && l.left_time == r.left_time &&
         l.left_dist == r.left_dist && l.approximate == r.approximate &&
         l.flags == r.flags;
}

TEST(ChainBusyDrivers, Serialize) {
  const std::chrono::system_clock::time_point timestamp =
      std::chrono::system_clock::now();
  models::driver::busy_info_flag::Mask flags;
  const std::vector<ChainBusyDriver> drivers(
      {{"0", "order_0", {0, 0}, 0, 0, false, flags, timestamp},
       {"1", "order_1", {1, 1}, 1, 1, false, flags, timestamp},
       {"2", "order_2", {2, 2}, 2, 2, false, flags, timestamp},
       {"3", "order_3", {3, 3}, 3, 3, false, flags, timestamp}});

  const std::string& data =
      tracker::SerializeChainBusyDrivers(drivers, timestamp);
  ASSERT_FALSE(data.empty());

  std::chrono::system_clock::time_point out_timestamp;
  ChainBusyDrivers out_drivers =
      tracker::DeserializeChainBusyDrivers(data, &out_timestamp);
  EXPECT_GT(std::chrono::seconds(1), timestamp - out_timestamp);
  ASSERT_EQ(4u, out_drivers.size());
  EXPECT_EQ(drivers[0], out_drivers["0"]);
  EXPECT_EQ(drivers[1], out_drivers["1"]);
  EXPECT_EQ(drivers[2], out_drivers["2"]);
  EXPECT_EQ(drivers[3], out_drivers["3"]);

  EXPECT_NO_THROW(tracker::DeserializeChainBusyDrivers(data));
}
