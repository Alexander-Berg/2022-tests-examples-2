#include <common/utils/time.hpp>
#include <common/utils/types.hpp>
#include <userver/utils/datetime.hpp>

#include <userver/utest/utest.hpp>

TEST(UtilsTest, DayOfWeekTest) {
  auto t = ::utils::datetime::Stringtime("2020-02-02T12:00:00Z", "UTC");
  EXPECT_EQ(billing_subventions_x::utils::GetDayOfWeekNumber(t, "UTC"), 7);
}

TEST(UtilsTest, LocalHourTest) {
  auto t = ::utils::datetime::Stringtime("2020-01-10T23:15:55Z", "UTC");
  EXPECT_EQ(billing_subventions_x::utils::GetLocalHour(t, "UTC"), 23);
  EXPECT_EQ(billing_subventions_x::utils::GetLocalHour(t, "Asia/Yekaterinburg"),
            4);
}
