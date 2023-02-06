#include <userver/utest/utest.hpp>

#include <utils/unlocalize_time.hpp>

namespace eats_report_storage::utils {

TEST(UnlocalizeTime, function_should_return_time_without_time_zone) {
  auto time = ::utils::datetime::Stringtime("2010-01-01T15:00:00+0300");
  auto expected_unlocalize_time =
      ::utils::datetime::Stringtime("2010-01-01T12:00:00+0000");
  ASSERT_EQ(UnlocalizeTime(time), expected_unlocalize_time);
}

TEST(DropTimeZone, function_should_return_time_without_moscow_time_zone) {
  auto time = ::utils::datetime::Stringtime("2010-01-01T15:00:00+0300");
  auto expected_unlocalize_time =
      ::utils::datetime::Stringtime("2010-01-01T15:00:00+0000");
  ASSERT_EQ(DropTimeZone(time), expected_unlocalize_time);
}

TEST(DropTimeZone, function_should_return_time_if_time_in_utc) {
  auto time = ::utils::datetime::Stringtime("2010-01-01T15:00:00+0000");
  auto expected_unlocalize_time =
      ::utils::datetime::Stringtime("2010-01-01T15:00:00+0000");
  ASSERT_EQ(DropTimeZone(time, "UTC"), expected_unlocalize_time);
}

}  // namespace eats_report_storage::utils
