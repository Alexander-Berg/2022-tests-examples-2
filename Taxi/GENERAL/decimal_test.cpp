#include <userver/utest/utest.hpp>

#include <models/decimal.hpp>

#include <cctz/time_zone.h>

namespace models {

TEST(DecimalTest, RoundDown) {
  EXPECT_EQ(RoundDown(Decimal4{"0.9999"}), Decimal4{0});
  EXPECT_EQ(RoundDown(Decimal4{"1.0000"}), Decimal4{1});
  EXPECT_EQ(RoundDown(Decimal4{"1.0001"}), Decimal4{1});
}

TEST(DecimalTest, RoundUp) {
  EXPECT_EQ(RoundUp(Decimal4{"0.9999"}), Decimal4{1});
  EXPECT_EQ(RoundUp(Decimal4{"1.0000"}), Decimal4{1});
  EXPECT_EQ(RoundUp(Decimal4{"1.0001"}), Decimal4{2});
}

TEST(DecimalTest, MulDown) {
  // 1.2255 * 0.3355 = 0.41115525 ▼ 0.4111
  EXPECT_EQ(MulDown(Decimal4{"1.2255"}, Decimal4{"0.3355"}),
            Decimal4{"0.4111"});
}

TEST(DecimalTest, DivUp) {
  // 1.2255 / 0.3355 = 3.65275707 ▲ 3.6528
  EXPECT_EQ(DivUp(Decimal4{"1.2255"}, Decimal4{"0.3355"}), Decimal4{"3.6528"});
}

TEST(DecimalTest, AddPercent) {
  // 1.2254 * 0.3355 = 0.41112170 ▼ 0.4111
  // 1.2255 * 0.3355 = 0.41115525 ▼ 0.4111

  // 1.2254 + MAX(0.4111, 0.4112) = 1.6366
  EXPECT_EQ(
      AddPercent(Decimal4{"1.2254"}, Decimal4{"0.3355"}, Decimal4{"0.4112"}),
      Decimal4{"1.6366"});

  // 1.2255 + MAX(0.4111, 0.4110) = 1.6366
  EXPECT_EQ(
      AddPercent(Decimal4{"1.2255"}, Decimal4{"0.3355"}, Decimal4{"0.4110"}),
      Decimal4{"1.6366"});

  // 1.2255 + MAX(0.4111, 0.4111) = 1.6366
  EXPECT_EQ(
      AddPercent(Decimal4{"1.2255"}, Decimal4{"0.3355"}, Decimal4{"0.4111"}),
      Decimal4{"1.6366"});

  // 1.2255 + MAX(0.4111, 0.4112) = 1.6367
  EXPECT_EQ(
      AddPercent(Decimal4{"1.2255"}, Decimal4{"0.3355"}, Decimal4{"0.4112"}),
      Decimal4{"1.6367"});
}

TEST(DecimalTest, SubPercent) {
  // 1.6366 / (1 + 0.3355) = 1.22545862 ▲ 1.2255
  // 1.6366 - 1.2255 = 0.4111
  // 1.6367 / (1 + 0.3355) = 1.22553350 ▲ 1.2256
  // 1.6367 - 1.2256 = 0.4110

  // 1.6366 - MAX(0.4111, 0.4112) = 1.2254
  EXPECT_EQ(
      SubPercent(Decimal4{"1.6366"}, Decimal4{"0.3355"}, Decimal4{"0.4112"}),
      Decimal4{"1.2254"});

  // 1.6366 - MAX(0.4111, 0.4110) = 1.2255
  EXPECT_EQ(
      SubPercent(Decimal4{"1.6366"}, Decimal4{"0.3355"}, Decimal4{"0.4110"}),
      Decimal4{"1.2255"});

  // 1.6366 - MAX(0.4111, 0.4111) = 1.2255
  EXPECT_EQ(
      SubPercent(Decimal4{"1.6366"}, Decimal4{"0.3355"}, Decimal4{"0.4111"}),
      Decimal4{"1.2255"});

  // 1.6367 - MAX(0.4110, 0.4112) = 1.2255
  EXPECT_EQ(
      SubPercent(Decimal4{"1.6367"}, Decimal4{"0.3355"}, Decimal4{"0.4112"}),
      Decimal4{"1.2255"});
}

}  // namespace models
