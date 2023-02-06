#include <gtest/gtest.h>

#include "get_next_date_first_second.hpp"

#include <userver/utils/mock_now.hpp>

TEST(GetNextDateFirstSecond, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2020-11-26T11:12:15", "UTC",
                                                "%Y-%m-%dT%H:%M:%S");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_restapp_promo::utils::GetNextDateFirstSecond();
  ASSERT_EQ(utils::datetime::Timestring(result, "Europe/Moscow"),
            "2020-11-27T00:00:00+0300");

  result = eats_restapp_promo::utils::GetCurrentDateFirstSecond();
  ASSERT_EQ(utils::datetime::Timestring(result, "Europe/Moscow"),
            "2020-11-26T00:00:00+0300");
}

TEST(GetNextDateFirstSecond, CurrentTimeWithTimezone) {
  auto mock_now =
      ::utils::datetime::Stringtime("2020-11-26T01:26:31.000000+0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_restapp_promo::utils::GetNextDateFirstSecond();
  ASSERT_EQ(utils::datetime::Timestring(result, "Europe/Moscow"),
            "2020-11-27T00:00:00+0300");

  result = eats_restapp_promo::utils::GetCurrentDateFirstSecond();
  ASSERT_EQ(utils::datetime::Timestring(result, "Europe/Moscow"),
            "2020-11-26T00:00:00+0300");
}

TEST(GetNextDateFirstSecond, CurrentTimeAfterMidnight) {
  auto mock_now =
      ::utils::datetime::Stringtime("2021-12-31T22:15:17.000000+0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_restapp_promo::utils::GetNextDateFirstSecond();
  ASSERT_EQ(utils::datetime::Timestring(result, "Europe/Moscow"),
            "2022-01-01T00:00:00+0300");

  result = eats_restapp_promo::utils::GetCurrentDateFirstSecond();
  ASSERT_EQ(utils::datetime::Timestring(result, "Europe/Moscow"),
            "2021-12-31T00:00:00+0300");
}
