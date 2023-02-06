#include <gtest/gtest.h>

#include <defs/definitions.hpp>

#include <models/gps_coord_type.hpp>

namespace pm = personal::models;

namespace {

struct TestCase {
  handlers::GpsCoord as_coord;
  std::string as_string;
};

TestCase PositiveCoordCase() {
  TestCase result;
  result.as_coord.latitude = 123.22222222;
  result.as_coord.longitude = 54.7654321;

  result.as_string = "{\"latitude\":123.22222222,\"longitude\":54.7654321}";
  return result;
}

TestCase NegativeCoordCase() {
  TestCase result;
  result.as_coord.latitude = -43.456789;
  result.as_coord.longitude = -76.98765;

  result.as_string = "{\"latitude\":-43.456789,\"longitude\":-76.98765}";
  return result;
}

const std::vector<TestCase> cases = {
    PositiveCoordCase(),
    NegativeCoordCase(),
};

}  // namespace

namespace V2 {

struct TestCaseV2 {
  handlers::GpsCoordV2 as_coord;
  std::string as_string;
};

TestCaseV2 PositiveCoordCaseV2() {
  TestCaseV2 result;
  result.as_coord.latitude = "58.506118930174495";
  result.as_coord.longitude = "49.69658916490733";

  result.as_string =
      "{\"latitude\":\"58.506118930174495\",\"longitude\":\"49."
      "69658916490733\"}";
  return result;
}

TestCaseV2 NegativeCoordCaseV2() {
  TestCaseV2 result;
  result.as_coord.latitude = "-58.506118930174495";
  result.as_coord.longitude = "-49.69658916490733";

  result.as_string =
      "{\"latitude\":\"-58.506118930174495\",\"longitude\":\"-49."
      "69658916490733\"}";
  return result;
}

const std::vector<TestCaseV2> cases = {
    PositiveCoordCaseV2(),
    NegativeCoordCaseV2(),
};

}  // namespace V2

TEST(GpsCoordTypeTest, GpsCoordToStringTest) {
  for (const auto& coord : cases) {
    auto output = pm::GpsCoordToString(coord.as_coord);
    EXPECT_EQ(output, coord.as_string);
  }
}

TEST(GpsCoordTypeTest, GpsCoordFromStringTest) {
  for (const auto& coord : cases) {
    auto output = pm::GpsCoordFromString(coord.as_string);
    EXPECT_EQ(output, coord.as_coord);
  }
}

TEST(GpsCoordTypeTest, GpsStringBasedToStringTest) {
  for (const auto& coord : V2::cases) {
    auto output = pm::GpsStringBasedToString(coord.as_coord);
    EXPECT_EQ(output, coord.as_string);
  }
}

TEST(GpsCoordTypeTest, GpsStringBasedFromStringTest) {
  for (const auto& coord : V2::cases) {
    auto output = pm::GpsStringBasedFromString(coord.as_string);
    EXPECT_EQ(output, coord.as_coord);
  }
}
