#include <gpssignal/test/print_to.hpp>
#include <gpssignal/units.hpp>

#include <gtest/gtest.h>

namespace gpssignal {

class UnitFixture : public testing::Test {};

TEST_F(UnitFixture, Speed) {
  {
    Speed reference_value = 16.6 * meters_per_second;
    Speed test_value = 16.6 * meters / second;
    EXPECT_EQ(reference_value, test_value);
  }
  {
    Speed reference_value = 16600 * meters_per_second;
    Speed test_value{16.6 * kilo * meters / second};
    EXPECT_EQ(reference_value, test_value);
  }
}

TEST_F(UnitFixture, KmhToMs) {
  {
    Speed reference_value = 16.6 * meters_per_second;
    Speed test_value{60 * kilo * meters / hour};
    EXPECT_NEAR(reference_value.value(), test_value.value(), 0.1);
  }
}

TEST_F(UnitFixture, MsToKmh) {
  using SpeedKmh = ::gpssignal::SpeedKmh<int>;
  {
    SpeedKmh reference_value{60 * kilo * meters / hour};
    EXPECT_EQ(reference_value.value(), 60);

    {
      // Check km_per_hour prefix
      SpeedKmh test_value{60 * km_per_hour};
      EXPECT_EQ(reference_value.value(), test_value.value());
    }

    {
      SpeedKmh test_value{16.66667 * meters / second};
      EXPECT_EQ(reference_value.value(), test_value.value());
    }

    {
      Speed test_source = 16.66667 * meters / second;
      SpeedKmh test_value = SpeedKmh{test_source};
      EXPECT_EQ(reference_value.value(), test_value.value());
    }
  }
}

}  // namespace gpssignal
