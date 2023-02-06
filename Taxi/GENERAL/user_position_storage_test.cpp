#include "user_position_storage.hpp"

#include <gtest/gtest.h>

using models::UserPosition;
using models::detail::PackUserPosition;
using models::detail::UnpackUserPosition;

TEST(PackUnpackUserPosition, One) {
  UserPosition pos;
  // pos.user_id is not packed
  pos.lon = 3.14;
  pos.lat = 2.72;
  pos.timestamp = std::chrono::system_clock::from_time_t(time(nullptr));
  pos.accuracy = 14;

  const std::string& pack = PackUserPosition(pos);
  ASSERT_FALSE(pack.empty());
  const UserPosition& unpack = UnpackUserPosition(pack);
  // EXPECT_EQ(pos, unpack) << pack;  // doubles are not equals
  EXPECT_EQ(pos.user_id, unpack.user_id);
  EXPECT_NEAR(pos.lon, unpack.lon, 0.000001);
  EXPECT_NEAR(pos.lat, unpack.lat, 0.000001);
  EXPECT_EQ(pos.timestamp, unpack.timestamp);
  EXPECT_EQ(pos.accuracy, unpack.accuracy);
}
