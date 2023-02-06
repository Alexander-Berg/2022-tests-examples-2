#include <gtest/gtest.h>

#include <geohistory/user_position.hpp>

TEST(UserFbConversion, NormalConversion) {
  models::UserPosition position;
  position.lon = 42;
  position.lat = 0.4283726124352;
  position.user_id = "user_id";
  position.timestamp = std::chrono::system_clock::now();
  position.accuracy = 5;
  const auto bin_user = geohistory::user::SerializePoint(position);
  const auto restored_position = geohistory::user::DeserializePoint(bin_user);

  const double kAbsPointError = 1e-5;
  EXPECT_NEAR(position.lon, restored_position.lon, kAbsPointError);
  EXPECT_NEAR(position.lat, restored_position.lat, kAbsPointError);
  EXPECT_EQ(std::chrono::system_clock::to_time_t(position.timestamp),
            std::chrono::system_clock::to_time_t(restored_position.timestamp));
  EXPECT_EQ(position.accuracy, restored_position.accuracy);
}

TEST(UserFbConversion, ErrorConversion) {
  std::string wrong_data = "This is definitely not a flatbuffer";
  ASSERT_THROW(geohistory::user::DeserializePoint(wrong_data),
               std::runtime_error);
}

TEST(UserTrackFbConversion, NormalConversion) {
  const std::vector<models::UserPosition> positions = {
      {{42, 0.4283726124352},
       "user_id",
       std::chrono::system_clock::from_time_t(1538352000),
       5},
      {{33.5, 20.2},
       "user_id",
       std::chrono::system_clock::from_time_t(1538353000),
       4},
      {{30, 21.5},
       "user_id",
       std::chrono::system_clock::from_time_t(1538354000),
       3}};

  const auto bin_user = geohistory::user::SerializeTrack(positions);
  const auto restored_positions = geohistory::user::DeserializeTrack(bin_user);

  const double kAbsPointError = 1e-5;
  ASSERT_EQ(positions.size(), restored_positions.size());
  for (size_t i = 0; i < positions.size(); ++i) {
    EXPECT_NEAR(positions[i].lon, restored_positions[i].lon, kAbsPointError);
    EXPECT_NEAR(positions[i].lat, restored_positions[i].lat, kAbsPointError);
    EXPECT_EQ(
        std::chrono::system_clock::to_time_t(positions[i].timestamp),
        std::chrono::system_clock::to_time_t(restored_positions[i].timestamp));
    EXPECT_EQ(positions[i].accuracy, restored_positions[i].accuracy);
  }
}

TEST(UserTrackFbConversion, ErrorConversion) {
  std::string wrong_data = "This is definitely not a flatbuffer";
  ASSERT_THROW(geohistory::user::DeserializeTrack(wrong_data),
               std::runtime_error);
}
