#include <gtest/gtest.h>

#include <models/driverid.hpp>

// The code is copied with some modifications from:
// https://github.yandex-team.ru/taxi/backend-cpp/blob/1920f9e3249f40bf71accd14636cc70334541825/common/src/models/drivers_test.hpp

TEST(DriverId, FromDbidUuid) {
  const auto& id = models::DriverId::FromDbidUuid("asd_fgh");
  EXPECT_TRUE(id.IsValid());
  EXPECT_STREQ("asd", id.dbid.c_str());
  EXPECT_STREQ("fgh", id.uuid.c_str());
  EXPECT_STREQ("asd_fgh", id.dbid_uuid().c_str());
}
