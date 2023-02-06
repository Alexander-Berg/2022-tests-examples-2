#include <gtest/gtest.h>

#include <cstdint>
#include <limits>
#include <optional>

#include <utils/fbs/signal_device_api.hpp>

namespace signalq_drivematics_api::utils::fbs {

namespace {

using signal_device_api::FbsGetNullable;

const int WRONG_TYPE = -1;
int FbsGetNullable(...) { return WRONG_TYPE; };

}  // namespace

TEST(FbsGetNullable, BOOL) {
  bool value1 = true;
  bool value2 = false;
  ASSERT_EQ(FbsGetNullable(value1), WRONG_TYPE);
  ASSERT_EQ(FbsGetNullable(value2), WRONG_TYPE);
}

TEST(FbsGetNullable, INT) {
  int value1 = -1000;
  int value2 = 1000;
  ASSERT_EQ(FbsGetNullable(value1), std::nullopt);
  ASSERT_EQ(FbsGetNullable(value2), 1000);
}

TEST(FbsGetNullable, SHORT) {
  short value1 = -1000;
  short value2 = 1000;
  ASSERT_EQ(FbsGetNullable(value1), std::nullopt);
  ASSERT_EQ(FbsGetNullable(value2), 1000);
}

TEST(FbsGetNullable, UNSIGNED) {
  unsigned value = 1;
  ASSERT_EQ(FbsGetNullable(value), WRONG_TYPE);
}

TEST(FbsGetNullable, LONG_LONG) {
  long long value1 = -1000;
  long long value2 = 1000;
  ASSERT_EQ(FbsGetNullable(value1), std::nullopt);
  ASSERT_EQ(FbsGetNullable(value2), 1000);
}

TEST(FbsGetNullable, UNSIGNED_LONG_LONG) {
  unsigned long long value1 = 1;
  ASSERT_EQ(FbsGetNullable(value1), WRONG_TYPE);
}

TEST(FbsGetNullable, CHAR) {
  char value = 1;
  ASSERT_EQ(FbsGetNullable(value), WRONG_TYPE);
}

TEST(FbsGetNullable, UNSIGNED_CHAR) {
  unsigned char value = 1;
  ASSERT_EQ(FbsGetNullable(value), WRONG_TYPE);
}

TEST(FbsGetNullable, INT8_T) {
  int8_t value = 1;
  ASSERT_EQ(FbsGetNullable(value), WRONG_TYPE);
}

TEST(FbsGetNullable, UINT8_T) {
  uint8_t value = 1;
  ASSERT_EQ(FbsGetNullable(value), WRONG_TYPE);
}

TEST(FbsGetNullable, INT16_T) {
  long long value1 = -1000;
  long long value2 = 1000;
  ASSERT_EQ(FbsGetNullable(value1), std::nullopt);
  ASSERT_EQ(FbsGetNullable(value2), 1000);
}

TEST(FbsGetNullable, UINT16_T) {
  uint16_t value = 1;
  ASSERT_EQ(FbsGetNullable(value), WRONG_TYPE);
}

TEST(FbsGetNullable, INT32_T) {
  int32_t value1 = -1000;
  int32_t value2 = 1000;
  ASSERT_EQ(FbsGetNullable(value1), std::nullopt);
  ASSERT_EQ(FbsGetNullable(value2), 1000);
}

TEST(FbsGetNullable, UINT32_T) {
  uint32_t value = -1000;
  ASSERT_EQ(FbsGetNullable(value), WRONG_TYPE);
}

TEST(FbsGetNullable, INT64_T) {
  int64_t value1 = -1000;
  int64_t value2 = 1000;
  ASSERT_EQ(FbsGetNullable(value1), std::nullopt);
  ASSERT_EQ(FbsGetNullable(value2), 1000);
}

TEST(FbsGetNullable, UINT64_T) {
  uint64_t value = 1;
  ASSERT_EQ(FbsGetNullable(value), WRONG_TYPE);
}

TEST(FbsGetNullable, FLOAT) {
  float value1 = std::numeric_limits<float>::quiet_NaN();
  float value2 = -1000.;
  ASSERT_EQ(FbsGetNullable(value1), std::nullopt);
  ASSERT_EQ(FbsGetNullable(value2), -1000.);
}

TEST(FbsGetNullable, DOUBLE) {
  double value1 = std::numeric_limits<double>::quiet_NaN();
  double value2 = -1000.;
  ASSERT_EQ(FbsGetNullable(value1), std::nullopt);
  ASSERT_EQ(FbsGetNullable(value2), -1000.);
}

TEST(FbsGetNullable, STRING) {
  std::string value1 = "";
  std::string value2 = "string";
  ASSERT_EQ(FbsGetNullable(value1), std::nullopt);
  ASSERT_EQ(FbsGetNullable(value2), "string");
}

}  // namespace signalq_drivematics_api::utils::fbs
