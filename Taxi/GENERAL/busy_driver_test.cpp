#include "busy_driver.hpp"

#include <gtest/gtest.h>

bool Contains(models::BusyDrivers& l, models::BusyDrivers& r) {
  for (auto& item : l) {
    auto key = item.first;
    if (!r.count(key) || l[key].taxi_status != r[key].taxi_status) {
      return false;
    }
  }
  return true;
}

TEST(BusyDrivers, Serialize) {
  const std::chrono::system_clock::time_point timestamp =
      std::chrono::system_clock::now();
  models::BusyDrivers drivers;
  drivers["1234234_34a23b21fe45bc3"] =
      models::TaxiStatus({static_cast<models::order_status::Status>(0)});
  drivers["213213_54654654432"] =
      models::TaxiStatus({static_cast<models::order_status::Status>(1)});
  drivers["435345"] =
      models::TaxiStatus({static_cast<models::order_status::Status>(2)});
  drivers["24342_qwerty"] =
      models::TaxiStatus({static_cast<models::order_status::Status>(4)});
  drivers["123123e781d76a_0123a7fd236"] =
      models::TaxiStatus({static_cast<models::order_status::Status>(8)});

  const std::string& data = tracker::SerializeBusyDrivers(drivers, timestamp);
  ASSERT_FALSE(data.empty());

  std::chrono::system_clock::time_point out_timestamp;
  auto out_drivers = tracker::DeserializeRedisBusyDrivers(data, &out_timestamp);
  EXPECT_GT(std::chrono::seconds(1), timestamp - out_timestamp);
  EXPECT_TRUE(Contains(drivers, out_drivers));
  EXPECT_TRUE(Contains(out_drivers, drivers));

  EXPECT_NO_THROW(tracker::DeserializeRedisBusyDrivers(data));
}
