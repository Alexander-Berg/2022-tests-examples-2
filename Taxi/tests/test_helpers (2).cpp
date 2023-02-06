#include <gtest/gtest.h>

#include <userver/utils/datetime.hpp>

#include <helpers/datetime.hpp>

namespace metadata_storage {

TEST(TestHelpers, TestDoubleToDateTime) {
  auto value = helpers::DoubleToTimePoint(1496252630.763);
  auto expected = ::utils::datetime::GuessStringtime(
      "2017-05-31T17:43:50.763+00:00", "UTC");
  EXPECT_EQ(expected, value);
}

}  // namespace metadata_storage
