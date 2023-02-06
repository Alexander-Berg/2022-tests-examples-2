#include <geometry/azimuth.hpp>

#include <iostream>

#include <gtest/gtest.h>

using namespace ::geometry::literals;

struct AzimuthTestData {
  ::geometry::Position start;
  ::geometry::Position end;
  double reference_direction;
};

class AzimuthDataTestFixture
    : public ::testing::TestWithParam<AzimuthTestData> {
 public:
  static constexpr const double kRoughAzimuthThreshold = 5.0;

  static std::vector<AzimuthTestData> RoughTestData;
};

TEST_P(AzimuthDataTestFixture, TestAzimuth) {
  const auto& data = GetParam();
  const auto direction = CalculateAzimuthRoughly(data.start, data.end);
  ASSERT_NE(std::nullopt, direction);
  EXPECT_NEAR(direction->value(), data.reference_direction,
              kRoughAzimuthThreshold);

  const auto inverse_direction = CalculateAzimuthRoughly(data.end, data.start);
  const auto inverse_reference = fmod(180 + data.reference_direction, 360);
  ASSERT_NE(std::nullopt, inverse_direction);
  EXPECT_NEAR(inverse_direction->value(), inverse_reference,
              kRoughAzimuthThreshold);
}

// clang-format off
std::vector<AzimuthTestData> AzimuthDataTestFixture::RoughTestData{{
    {{55.856548_lat, 37.687837_lon}, {55.857282_lat, 37.686272_lon}, 310},
    {{55.865324_lat, 37.681315_lon}, {55.853473_lat, 37.649128_lon}, 237},
     // Real azimuth is 22
    {{0.0_lat, 0.0_lon}, {55.853473_lat, 37.649128_lon}, 29}
}};
// clang-format on

TEST(AzimuzthTest, TestSamePoint) {
  using namespace geometry;
  Position pos{5 * lat, 5 * lon};

  EXPECT_EQ(std::nullopt, CalculateAzimuthRoughly(pos, pos));
}

INSTANTIATE_TEST_SUITE_P(
    TestRough, AzimuthDataTestFixture,
    ::testing::ValuesIn(AzimuthDataTestFixture::RoughTestData.begin(),
                        AzimuthDataTestFixture::RoughTestData.end()));

TEST(AccurateAzimuthTest, TestSamePoint) {
  using namespace geometry;
  Position pos{5 * lat, 5 * lon};

  EXPECT_EQ(geometry::CalculateAzimuth(pos, pos).value(), 0);
}

TEST(AccurateAzimuthTest, Base) {
  EXPECT_EQ(geometry::CalculateAzimuth({0.0_lat, 0.0_lon},
                                       {55.853473_lat, 37.649128_lon})
                .value(),
            22);
  EXPECT_EQ(geometry::CalculateAzimuth({55.856548_lat, 37.687837_lon},
                                       {55.857282_lat, 37.686272_lon})
                .value(),
            309);
  EXPECT_EQ(geometry::CalculateAzimuth({55.865324_lat, 37.681315_lon},
                                       {55.853473_lat, 37.649128_lon})
                .value(),
            236);
}
