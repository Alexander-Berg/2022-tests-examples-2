#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include "driver_position_entry.hpp"

namespace {
namespace drwi = driver_route_watcher::internal;
namespace drwm = driver_route_watcher::models;

const auto kAdjusted = drwm::Adjusted::kNo;
}  // namespace

UTEST(driver_position_entry, to_flatbuffers_and_back_to_normal) {
  drwm::DriverPosition src_position =
      drwm::DriverPosition(10 * geometry::lat, 10 * geometry::lon,
                           drwm::TransportType::kCar, kAdjusted);
  auto fbs_position = drwi::ToFlatbuffers(src_position);

  drwm::DriverPosition same_position = drwi::ToDriverPosition(fbs_position);
  ASSERT_EQ(src_position, same_position);
}
