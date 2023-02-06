#include "airport.hpp"

#include <gtest/gtest.h>
#include <iostream>

#include <utils/datetime.hpp>
using VirtualTimePoint = models::driver::airport::VirtualTimePoint;
TEST(VirtualTimePointsTest, Comparison) {
  const auto now = utils::datetime::Now();
  const auto prev = now - std::chrono::seconds(10);
  using VirtualTimePoint = models::driver::airport::VirtualTimePoint;
  const std::vector<VirtualTimePoint> virtual_times{
      // prev
      {prev, now},          // virtual preferred
      {boost::none, prev},  // actual time is prev
      // now
      {now, prev},
      {now, now},
      {boost::none, now},
      // none
      {boost::none, boost::none},
      {now, boost::none},
  };

  const std::vector<size_t> shuffle{3, 2, 0, 4, 1, 6, 5};

  EXPECT_EQ(shuffle.size(), virtual_times.size());

  std::vector<VirtualTimePoint> sorter(virtual_times.size());
  for (size_t i = 0; i < virtual_times.size(); ++i) {
    sorter[i] = virtual_times.at(shuffle[i]);
  }
  std::sort(sorter.begin(), sorter.end());

  EXPECT_EQ(sorter, virtual_times);
}
