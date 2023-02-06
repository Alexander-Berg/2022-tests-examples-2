#include <gtest/gtest.h>

#include <geobus/types/driver_id.hpp>

// The code is copied with some modifications from:
// https://github.yandex-team.ru/taxi/backend-cpp/blob/1920f9e3249f40bf71accd14636cc70334541825/common/src/models/drivers_test.hpp

TEST(DriverId, FromDbidUuid) {
  const auto& id = geobus::types::DriverId{"asd_fgh"};
  EXPECT_TRUE(id.IsValid());
  EXPECT_EQ(std::string{"asd"}, id.GetDbid().GetUnderlying());
  EXPECT_EQ(std::string{"fgh"}, id.GetUuid().GetUnderlying());
  EXPECT_EQ(std::string{"asd_fgh"}, id.GetDbidUndscrUuid());
}
