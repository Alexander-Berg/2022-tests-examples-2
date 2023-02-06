#include <gpssignal/gps_signal.hpp>

#include <gtest/gtest.h>

namespace gpssignal {

class GpsSignalFixture : public ::testing::Test {};

TEST_F(GpsSignalFixture, CreateAnyOrder) {
  {
    GpsSignal signal(5.0 * lat, 7.0 * lon);

    EXPECT_EQ(7.0 * lon, signal.longitude);
    EXPECT_EQ(5.0 * lat, signal.latitude);
  }
  {
    GpsSignal signal(7.0 * lon, 5.0 * lat);

    EXPECT_EQ(7.0 * lon, signal.longitude);
    EXPECT_EQ(5.0 * lat, signal.latitude);
  }
  {
    /// Test templated constructor
    GpsSignal signal(5.0 * lat, 7.0 * lon, std::nullopt, std::nullopt,
                     std::nullopt, std::chrono::system_clock::now());

    EXPECT_EQ(7.0 * lon, signal.longitude);
    EXPECT_EQ(5.0 * lat, signal.latitude);
  }
  {
    /// Test templated constructor
    GpsSignal signal(7.0 * lon, 5.0 * lat, std::nullopt, std::nullopt,
                     std::nullopt, std::chrono::system_clock::now());

    EXPECT_EQ(7.0 * lon, signal.longitude);
    EXPECT_EQ(5.0 * lat, signal.latitude);
  }
}

TEST_F(GpsSignalFixture, Speed) {
  Speed reference_value = 16.6 * meters_per_second;

  GpsSignal signal(5.0 * lat, 7.0 * lon);

  signal.speed = Speed{16.6 * meters / second};
  EXPECT_EQ(reference_value, *signal.speed);

  signal.speed = Speed{60 * kilo * meters / hour};
  EXPECT_NEAR(reference_value.value(), signal.speed->value(), 0.1);
}

}  // namespace gpssignal
