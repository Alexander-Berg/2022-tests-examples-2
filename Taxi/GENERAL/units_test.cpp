#include <geometry/units.hpp>

#include <gtest/gtest.h>

namespace geometry {

class UnitFixture : public testing::Test {};

TEST_F(UnitFixture, LatLonToRad) {
  using namespace ::geometry::literals;
  {
    auto test_latitude = 0.0_lat;
    auto test_radian = ToRadians(test_latitude);

    EXPECT_DOUBLE_EQ(test_radian.value(), 0.0);
    EXPECT_DOUBLE_EQ(0.0, test_latitude.AsRadians().value());
  }
  {
    auto test_latitude = 90.0_lat;
    auto test_radian = ToRadians(test_latitude);

    EXPECT_NEAR(M_PI / 2.0, test_radian.value(), 1e-11);
  }
}

TEST_F(UnitFixture, LonLatArithmetic) {
  using namespace ::geometry::literals;
  {
    // substract coordinates
    EXPECT_EQ(10.0 * degree, 15.0_lat - 5.0_lat);

    // Add degrees
    EXPECT_EQ(10.0_lat, 5.0_lat + 5.0 * degree);
    EXPECT_EQ(10.0_lat, 5.0 * degree + 5.0_lat);

    // Compare
    EXPECT_GT(10.0_lat, 5.0_lat);
    EXPECT_LT(10.0_lat, 100.0_lat);
    EXPECT_GE(10.0_lat, 5.0_lat);
    EXPECT_LE(10.0_lat, 100.0_lat);
    EXPECT_NE(10.0_lat, 15.0_lat);

    // unary + and -
    EXPECT_EQ((-10.0) * lat, -10.0_lat);
    EXPECT_EQ(10.0_lat, +10.0_lat);
  }
}

TEST_F(UnitFixture, LonLatDeltaArithmetic) {
  using namespace ::geometry::literals;
  {
    // automatic conversion to degrees
    EXPECT_EQ(20.0 * degree, 20.0 * degree);
  }
  {
    // Summation
    EXPECT_EQ(20.0 * degree, 10.0 * degree + 10.0 * degree);
    // Subtraction
    EXPECT_EQ(7.0 * degree, 10.0 * degree - 3.0 * degree);
    // Multiplication
    EXPECT_EQ(30.0 * degree, (10.0 * degree) * 3.0);
    EXPECT_EQ(30.0 * degree, 3.0 * (10.0 * degree));

    // Division
    EXPECT_EQ(3.0, (30.0 * degree) / (10.0 * degree));

    EXPECT_EQ(10.0 * degree,
              (1.0 / (10.0 * degree)) * (10.0 * degree) * (10.0 * degree));

    // Inverse division
    EXPECT_EQ(1.0 / (3.0 * degree), 1.0 / (3.0 * degree));

    // +=, -=
    auto val = 10.0_lat;
    val += 5.0 * degree;
    EXPECT_EQ(15.0_lat, val);

    val -= 2.0 * degree;
    EXPECT_EQ(13.0_lat, val);
  }
}
TEST_F(UnitFixture, LonLatStrongDelta) {
  using namespace ::geometry::literals;
  // Testing various methods of creation
  LatitudeDelta d1{180.0};           // from double
  LatitudeDelta d2{180.0 * degree};  // from degree
  EXPECT_EQ(d1, d2);

  // 180 degree = pi radians
  LatitudeDelta drad{Degrees{M_PI * radians}};
  EXPECT_NEAR(d1.value(), drad.value(), 0.00001);
}

TEST_F(UnitFixture, LonLatTrigonometric) {
  using namespace ::geometry::literals;
  EXPECT_NEAR(0.0, cos(90.0 * degree), 1e-6);
  EXPECT_NEAR(1.0, sin(90.0 * degree), 1e-6);
  EXPECT_NEAR(0.5, cos(60.0 * degree), 1e-6);
  EXPECT_NEAR(0.5, sin(30.0 * degree), 1e-6);

  EXPECT_EQ(cos(90.0 * degree), cos((90.0_lat).AsDegrees()));
}

namespace {
bool IsGoodLatOverload(Latitude) { return true; }
template <typename T>
bool IsGoodLatOverload(T&&) {
  return false;
}

bool IsGoodLatDeltaOverload(LatitudeDelta) { return true; }
template <typename T>
bool IsGoodLatDeltaOverload(T&&) {
  return false;
}
}  // namespace

TEST_F(UnitFixture, LonLatConversion) {
  using namespace ::geometry::literals;
  // in this test we check that overload we desire is always selected
  EXPECT_TRUE(IsGoodLatOverload(10.0_lat));
  // converting from degree should work
  EXPECT_TRUE(IsGoodLatOverload((10.0 * degree) * lat));
  // however, using degree directly should not
  EXPECT_FALSE(IsGoodLatOverload(10.0 * degree));
  // also, using double or int should not work
  EXPECT_FALSE(IsGoodLatOverload(10));
  EXPECT_FALSE(IsGoodLatOverload(10.0));
  // longitude should not work, obviously
  EXPECT_FALSE(IsGoodLatOverload(10.0_lon));
  EXPECT_FALSE(IsGoodLatOverload(10.0 * dlon));
}

TEST_F(UnitFixture, LonLatDeltaConversion) {
  using namespace ::geometry::literals;
  // in this test we check that overload we desire is always selected
  EXPECT_TRUE(IsGoodLatDeltaOverload(10.0 * dlat));
  // converting from degree should work
  EXPECT_TRUE(IsGoodLatDeltaOverload((10.0 * degree) * dlat));
  // however, using degree directly should not
  EXPECT_FALSE(IsGoodLatDeltaOverload(10.0 * degree));
  // also, using double or int should not work
  EXPECT_FALSE(IsGoodLatDeltaOverload(10));
  EXPECT_FALSE(IsGoodLatDeltaOverload(10.0));
  // longitude should not work, obviously
  EXPECT_FALSE(IsGoodLatDeltaOverload(10.0_lon));
  EXPECT_FALSE(IsGoodLatDeltaOverload(10.0 * dlon));
}

// ==== Test chrono conversions ===
TEST_F(UnitFixture, ChronoConversions) {
  using namespace ::geometry::literals;

  const auto d1 = 10.0_meters;
  const auto t1 = std::chrono::milliseconds{1000};

  // first, let's test that this one at least compiles
  auto r1 = d1 * t1;

  // and that tick is processed correctly
  const auto t2 = std::chrono::seconds{1};
  auto r2 = d1 * t2;

  EXPECT_EQ(r1, r2);

  // now let's test that some useful cases: velocity
  // Because OK continue to insist that Speed should not be defined in geometry
  // we define it here
  using boost::units::si::meters_per_second;
  const auto velocity = d1 / t1;

  EXPECT_EQ(10.0 * meters_per_second, velocity);
  EXPECT_EQ(d1, velocity * t1);  // these will be double, but input is strictly
                                 // int - so comparison should work

  // comparison. not that anybody needs it
  EXPECT_GE(std::chrono::seconds{5}, 1.0 * boost::units::si::seconds);
}

// ==== Test WGS84 ===

TEST(WGS84, Axes) { EXPECT_NEAR(6356752.3142, kWgs84MinorSemiaxis, 0.001); }

TEST(WGS84, LatitudeLength) {
  using namespace ::geometry::literals;
  // Test data is from here:
  // https://en.wikipedia.org/wiki/Latitude#Length_of_a_degree_of_latitude
  EXPECT_NEAR(110574.0, LatitudeDegreeLength(0.0_lat).value(), 0.5);
  EXPECT_NEAR(110649.0, LatitudeDegreeLength(15.0_lat).value(), 0.5);
  EXPECT_NEAR(111132.0, LatitudeDegreeLength(45.0_lat).value(), 0.5);
  EXPECT_NEAR(111412.0, LatitudeDegreeLength(60.0_lat).value(), 0.5);
  EXPECT_NEAR(111694.0, LatitudeDegreeLength(90.0_lat).value(), 0.5);
  EXPECT_NEAR(111132.0, LatitudeDegreeLength(-45.0_lat).value(), 0.5);
}

TEST(WGS84, LongitudeLength) {
  using namespace ::geometry::literals;
  // Test data is from here:
  // https://www.webcitation.org/6DzvTFimc?url=http://msi.nga.mil/MSISiteContent/StaticFiles/Calculators/degree.html
  EXPECT_NEAR(111319.0, LongitudeDegreeLength(0.0_lat).value(), 0.5);
  EXPECT_NEAR(107550.0, LongitudeDegreeLength(15.0_lat).value(), 0.5);
  EXPECT_NEAR(78847.0, LongitudeDegreeLength(45.0_lat).value(), 0.5);
  EXPECT_NEAR(55800.0, LongitudeDegreeLength(60.0_lat).value(), 0.5);
  EXPECT_NEAR(0.0, LongitudeDegreeLength(90.0_lat).value(), 0.5);
  EXPECT_NEAR(78847.0, LongitudeDegreeLength(-45.0_lat).value(), 0.5);
}

}  // namespace geometry
