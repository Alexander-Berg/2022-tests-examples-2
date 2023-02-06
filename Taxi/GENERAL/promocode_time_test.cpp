#include <gtest/gtest.h>

#include "promocode_time.hpp"

#include <cctz/civil_time.h>
#include <userver/utils/mock_now.hpp>

using eats_performer_support::helpers::LeftBound;
using eats_performer_support::helpers::RightBound;
using eats_performer_support::helpers::Timezone;

void MakeIsExpiredPromoCodeTest(
    const std::string& now_str,
    const std::optional<storages::postgres::TimePointTz>& expires_at,
    const bool expected_result) {
  auto mock_now = ::utils::datetime::Stringtime(now_str);
  ::utils::datetime::MockNowSet(mock_now);

  auto promocode = eats_performer_support::models::PerformerTaxiPromocodes();
  promocode.expires_at = expires_at;
  auto is_expired =
      eats_performer_support::helpers::IsExpiredPromocode(promocode);
  ASSERT_EQ(expected_result, is_expired);
}

TEST(IsExpiredPromocodeTest, PromocodeWithoutExpiresAt) {
  MakeIsExpiredPromoCodeTest("2021-06-17T23:20:11+0300",
                             std::optional<storages::postgres::TimePointTz>(),
                             false);
}

TEST(IsExpiredPromocodeTest, ExpiredPromocode) {
  auto expires_at = storages::postgres::TimePointTz(
      ::utils::datetime::Stringtime("2021-06-17T23:00:11+0300"));
  MakeIsExpiredPromoCodeTest("2021-06-17T23:20:11+0300", expires_at, true);
}

TEST(IsExpiredPromocodeTest, NotExpiredPromocode) {
  auto expires_at = storages::postgres::TimePointTz(
      ::utils::datetime::Stringtime("2021-06-17T23:21:11+0300"));
  MakeIsExpiredPromoCodeTest("2021-06-17T23:20:11+0300", expires_at, false);
}

TEST(IsExpiredPromocodeTest, NotExpiredPromocodeBorderCase) {
  auto expires_at = storages::postgres::TimePointTz(
      ::utils::datetime::Stringtime("2021-06-17T23:20:11+0300"));
  MakeIsExpiredPromoCodeTest("2021-06-17T23:20:11+0300", expires_at, false);

  auto expires_at_after_second = storages::postgres::TimePointTz(
      ::utils::datetime::Stringtime("2021-06-17T23:20:11+0300"));
  MakeIsExpiredPromoCodeTest("2021-06-17T23:20:12+0300",
                             expires_at_after_second, true);
}

TEST(IsExpiredPromocodeTest,
     NotExpiredPromocodeBorderCaseInDifferentTimezones) {
  auto expires_at = storages::postgres::TimePointTz(
      ::utils::datetime::Stringtime("2021-06-17T23:20:11+0300"));
  MakeIsExpiredPromoCodeTest("2021-06-17T20:20:11+0000", expires_at, false);

  auto expires_at_after_second = storages::postgres::TimePointTz(
      ::utils::datetime::Stringtime("2021-06-17T23:20:11+0300"));
  MakeIsExpiredPromoCodeTest("2021-06-17T20:20:12+0000",
                             expires_at_after_second, true);

  auto utc_expires_at = storages::postgres::TimePointTz(
      ::utils::datetime::Stringtime("2021-06-17T20:20:11+0000"));
  MakeIsExpiredPromoCodeTest("2021-06-17T23:20:11+0300", utc_expires_at, false);
}

void MakeTestGetActualPromoCodeDateTimeInterval(
    const std::string& now_time_str, const std::string& time_zone,
    const std::string& left_boundary, const std::string& right_boundary) {
  auto mock_now = ::utils::datetime::Stringtime(now_time_str);
  ::utils::datetime::MockNowSet(mock_now);

  auto courier_data = clients::couriers_core::CouriersCatalogSearchItem();
  courier_data.work_region =
      clients::couriers_core::CouriersCatalogSearchItemWorkregion();
  courier_data.work_region.timezone = time_zone;

  auto result =
      eats_performer_support::helpers::GetActualPromoCodeDateTimeInterval(
          courier_data);
  ASSERT_EQ(utils::datetime::Timestring(result.start, "UTC"), left_boundary);
  ASSERT_EQ(utils::datetime::Timestring(result.end, "UTC"), right_boundary);
}

TEST(GetPromocodeCurrentDateTimeIntervalTest,
     ServiceAndCourierInMoscowTimezone) {
  MakeTestGetActualPromoCodeDateTimeInterval(
      "2021-06-17T23:20:11+0300", "Europe/Moscow", "2021-06-17T09:00:00+0000",
      "2021-06-18T09:00:00+0000");
  MakeTestGetActualPromoCodeDateTimeInterval(
      "2021-06-17T13:20:11+0300", "Europe/Moscow", "2021-06-17T09:00:00+0000",
      "2021-06-18T09:00:00+0000");
  MakeTestGetActualPromoCodeDateTimeInterval(
      "2021-06-17T11:20:11+0300", "Europe/Moscow", "2021-06-16T09:00:00+0000",
      "2021-06-17T09:00:00+0000");
}

TEST(GetPromocodeCurrentDateTimeIntervalTest,
     ServiceInUTCCourierInMoscowTimezone) {
  MakeTestGetActualPromoCodeDateTimeInterval(
      "2021-06-17T11:20:11+0000", "Europe/Moscow", "2021-06-17T09:00:00+0000",
      "2021-06-18T09:00:00+0000");
  MakeTestGetActualPromoCodeDateTimeInterval(
      "2021-06-17T15:20:11+0000", "Europe/Moscow", "2021-06-17T09:00:00+0000",
      "2021-06-18T09:00:00+0000");
  MakeTestGetActualPromoCodeDateTimeInterval(
      "2021-06-17T08:20:11+0000", "Europe/Moscow", "2021-06-16T09:00:00+0000",
      "2021-06-17T09:00:00+0000");
  MakeTestGetActualPromoCodeDateTimeInterval(
      "2021-06-17T23:20:11+0000", "Europe/Moscow", "2021-06-17T09:00:00+0000",
      "2021-06-18T09:00:00+0000");
}

TEST(GetPromocodeCurrentDateTimeIntervalTest,
     ServiceInUTCCourierInSamaraTimezone) {
  MakeTestGetActualPromoCodeDateTimeInterval(
      "2021-06-17T11:20:11+0000", "Europe/Samara", "2021-06-17T08:00:00+0000",
      "2021-06-18T08:00:00+0000");
  MakeTestGetActualPromoCodeDateTimeInterval(
      "2021-06-17T15:20:11+0000", "Europe/Samara", "2021-06-17T08:00:00+0000",
      "2021-06-18T08:00:00+0000");
  MakeTestGetActualPromoCodeDateTimeInterval(
      "2021-06-17T07:20:11+0000", "Europe/Samara", "2021-06-16T08:00:00+0000",
      "2021-06-17T08:00:00+0000");
  MakeTestGetActualPromoCodeDateTimeInterval(
      "2021-06-17T23:20:11+0000", "Europe/Samara", "2021-06-17T08:00:00+0000",
      "2021-06-18T08:00:00+0000");
  MakeTestGetActualPromoCodeDateTimeInterval(
      "2021-06-17T08:00:00+0000", "Europe/Samara", "2021-06-17T08:00:00+0000",
      "2021-06-18T08:00:00+0000");
}

TEST(GetPromocodeCurrentDateTimeIntervalTest,
     ServiceInMoscowCourierInLATimezone) {
  MakeTestGetActualPromoCodeDateTimeInterval(
      "2021-06-17T11:20:11+0300", "America/Los_Angeles",
      "2021-06-16T19:00:00+0000", "2021-06-17T19:00:00+0000");
  MakeTestGetActualPromoCodeDateTimeInterval(
      "2021-06-17T22:20:11+0300", "America/Los_Angeles",
      "2021-06-17T19:00:00+0000", "2021-06-18T19:00:00+0000");
}

//Входит в интервал
// Current time: 2021-06-17T23:20:11-03:00
// Config interval [23:00, 05:00)
// Calculated interval [2021-06-17T23:00:00+03:00, 2021-06-18T05:00:00+03:00)

TEST(GetTimeIntervalFromFormatHMTest1, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T22:20:11-0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("05:00"), Timezone("Europe/Moscow"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "Europe/Moscow"),
            "2021-06-17T23:00:00+0300");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "Europe/Moscow"),
            "2021-06-18T05:00:00+0300");
}

//Входит в интервал
// Current time: 2021-06-17T23:20:11-03:00
// Config interval [23:00, 23:00)
// Calculated interval [2021-06-17T23:00:00+03:00, 2021-06-18T23:00:00+03:00)
TEST(GetTimeIntervalFromFormatHMTest2, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T23:20:11-0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("23:00"), Timezone("Europe/Moscow"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "Europe/Moscow"),
            "2021-06-17T23:00:00+0300");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "Europe/Moscow"),
            "2021-06-18T23:00:00+0300");
}

//Входит в интервал
// Current time: 2021-06-17T23:20:11-03:00
// Config interval [23:00, 22:00)
// Calculated interval [2021-06-17T23:00:00+03:00, 2021-06-18T22:00:00+03:00)
TEST(GetTimeIntervalFromFormatHMTest3, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T23:20:11-0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("22:00"), Timezone("Europe/Moscow"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "Europe/Moscow"),
            "2021-06-17T23:00:00+0300");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "Europe/Moscow"),
            "2021-06-18T22:00:00+0300");
}

//Слишком рано
// Current time: 2021-06-17T01:20:11-03:00
// Config interval [13:00, 23:00)
// Calculated interval [2021-06-16T13:00:00+03:00, 2021-06-16T23:00:00+03:00)
TEST(GetTimeIntervalFromFormatHMTest4, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T01:20:11-0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("13:00"), RightBound("23:00"), Timezone("Europe/Moscow"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "Europe/Moscow"),
            "2021-06-17T13:00:00+0300");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "Europe/Moscow"),
            "2021-06-17T23:00:00+0300");
}

// Текущее время в другой таймзоне
// Current time: 2021-06-17T12:20:11-03:00
// Config interval [13:00, 23:00)
// Calculated interval [2021-06-16T13:00:00+03:00, 2021-06-16T23:00:00+03:00)
TEST(GetTimeIntervalFromFormatHMTest5, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T12:20:11-0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("13:00"), RightBound("23:00"), Timezone("Europe/Moscow"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "Europe/Moscow"),
            "2021-06-17T13:00:00+0300");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "Europe/Moscow"),
            "2021-06-17T23:00:00+0300");
}

//Входит в интервал
// Current time: 2021-06-17T13:20:11-03:00
// Config interval [13:00, 23:00)
// Calculated interval [2021-06-17T13:00:00+03:00, 2021-06-17T23:00:00+03:00)
TEST(GetTimeIntervalFromFormatHMTest6, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T13:20:11-0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("13:00"), RightBound("23:00"), Timezone("Europe/Moscow"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "Europe/Moscow"),
            "2021-06-17T13:00:00+0300");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "Europe/Moscow"),
            "2021-06-17T23:00:00+0300");
}

//Слишком поздно
// Current time: 2021-06-17T23:20:11-03:00
// Config interval [13:00, 23:00)
// Calculated interval [2021-06-18T13:00:00+03:00, 2021-06-18T23:00:00+03:00)
TEST(GetTimeIntervalFromFormatHMTest7, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T23:20:11-0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("13:00"), RightBound("23:00"), Timezone("Europe/Moscow"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "Europe/Moscow"),
            "2021-06-18T13:00:00+0300");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "Europe/Moscow"),
            "2021-06-18T23:00:00+0300");
}

//Слишком рано
// Current time: 2021-06-17T22:20:11-03:00
// Config interval [23:00, 01:00)
// Calculated interval [2021-06-16T23:00:00+03:00, 2021-06-17T01:00:00+03:00)
TEST(GetTimeIntervalFromFormatHMTest8, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T22:20:11-0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("01:00"), Timezone("Europe/Moscow"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "Europe/Moscow"),
            "2021-06-18T23:00:00+0300");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "Europe/Moscow"),
            "2021-06-19T01:00:00+0300");
}

//Слишком рано
// Current time: 2021-06-17T10:20:11-03:00
// Config interval [23:00, 01:00)
// Calculated interval [2021-06-16T23:00:00+03:00, 2021-06-17T01:00:00+03:00)
TEST(GetTimeIntervalFromFormatHMTest9, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T10:20:11-0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("01:00"), Timezone("Europe/Moscow"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "Europe/Moscow"),
            "2021-06-17T23:00:00+0300");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "Europe/Moscow"),
            "2021-06-18T01:00:00+0300");
}

//Входит в интервал тот же день
// Current time: 2021-06-17T23:20:11+03:00
// Config interval [23:00, 01:00)
// Calculated interval [2021-06-17T23:00:00+03:00, 2021-06-18T01:00:00+03:00)
TEST(GetTimeIntervalFromFormatHMTest10, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T23:20:11+0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("01:00"), Timezone("Europe/Moscow"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "Europe/Moscow"),
            "2021-06-17T23:00:00+0300");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "Europe/Moscow"),
            "2021-06-18T01:00:00+0300");
}

//Входит в интервал полночь
// Current time: 2021-06-17T00:00:00-03:00
// Config interval [23:00, 01:00)
// Calculated interval [2021-06-16T23:00:00+03:00, 2021-06-17T01:00:00+03:00)
TEST(GetTimeIntervalFromFormatHMTest11, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T00:00:00+0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("01:00"), Timezone("Europe/Moscow"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "Europe/Moscow"),
            "2021-06-16T23:00:00+0300");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "Europe/Moscow"),
            "2021-06-17T01:00:00+0300");
}

//Входит в интервал следующий день
// Current time: 2021-06-17T00:30:00-03:00
// Config interval [23:00, 01:00)
// Calculated interval [2021-06-16T23:00:00+03:00, 2021-06-17T01:00:00+03:00)
TEST(GetTimeIntervalFromFormatHMTest12, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T00:30:00+0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("01:00"), Timezone("Europe/Moscow"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "Europe/Moscow"),
            "2021-06-16T23:00:00+0300");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "Europe/Moscow"),
            "2021-06-17T01:00:00+0300");
}

//Не входит в интервал следующий день
// Current time: 2021-06-17T01:30:00+03:00
// Config interval [23:00, 01:00)
// Calculated interval [2021-06-16T23:00:00+03:00, 2021-06-17T01:00:00+03:00)
TEST(GetTimeIntervalFromFormatHMTest13, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T01:30:00+0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("01:00"), Timezone("Europe/Moscow"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "Europe/Moscow"),
            "2021-06-17T23:00:00+0300");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "Europe/Moscow"),
            "2021-06-18T01:00:00+0300");
}

// -------------------------

//Входит в интервал
// Current time: 2021-06-17T23:20:11+03:00
// Config interval [23:00, 05:00)
// Calculated interval [2021-06-17T23:00:00-07:00, 2021-06-18T05:00:00-07:00)

TEST(GetTimeIntervalFromFormatHMTest14, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T23:20:11+0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("05:00"), Timezone("America/Los_Angeles"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "America/Los_Angeles"),
            "2021-06-17T23:00:00-0700");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "America/Los_Angeles"),
            "2021-06-18T05:00:00-0700");
}

//Входит в интервал
// Current time: 2021-06-18T9:20:11+0300
// Config interval [23:00, 23:00)
// Calculated interval [2021-06-17T23:00:00-07:00, 2021-06-18T23:00:00-07:00)
TEST(GetTimeIntervalFromFormatHMTest15, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-18T9:20:11+0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("23:00"), Timezone("America/Los_Angeles"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "America/Los_Angeles"),
            "2021-06-17T23:00:00-0700");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "America/Los_Angeles"),
            "2021-06-18T23:00:00-0700");
}

//Входит в интервал
// Current time: 2021-06-17T23:20:11+03:00
// Config interval [23:00, 22:00)
// Calculated interval [2021-06-17T16:00:00-07:00, 2021-06-17T22:00:00-07:00)
TEST(GetTimeIntervalFromFormatHMTest16, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T23:20:11+0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("22:00"), Timezone("America/Los_Angeles"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "America/Los_Angeles"),
            "2021-06-16T23:00:00-0700");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "America/Los_Angeles"),
            "2021-06-17T22:00:00-0700");
}

//Слишком рано
// Current time: 2021-06-17T01:20:11+03:00
// Config interval [13:00, 23:00)
// Calculated interval [2021-06-16T13:00:00-07:00, 2021-06-16T23:00:00-07:00)
TEST(GetTimeIntervalFromFormatHMTest17, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T01:20:11+0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("13:00"), RightBound("23:00"), Timezone("America/Los_Angeles"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "America/Los_Angeles"),
            "2021-06-16T13:00:00-0700");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "America/Los_Angeles"),
            "2021-06-16T23:00:00-0700");
}

//Слишком рано
// Current time: 2021-06-17T12:20:11+03:00
// Config interval [13:00, 23:00)
// Calculated interval [2021-06-17T13:00:00-07:00, 2021-06-17T23:00:00-07:00)
TEST(GetTimeIntervalFromFormatHMTest18, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T12:20:11+0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("13:00"), RightBound("23:00"), Timezone("America/Los_Angeles"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "America/Los_Angeles"),
            "2021-06-17T13:00:00-0700");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "America/Los_Angeles"),
            "2021-06-17T23:00:00-0700");
}

//Входит в интервал
// Current time: 2021-06-17T13:20:11+03:00
// Config interval [13:00, 23:00)
// Calculated interval [2021-06-17T13:00:00-07:00, 2021-06-17T23:00:00-07:00)
TEST(GetTimeIntervalFromFormatHMTest19, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T13:20:11+0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("13:00"), RightBound("23:00"), Timezone("America/Los_Angeles"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "America/Los_Angeles"),
            "2021-06-17T13:00:00-0700");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "America/Los_Angeles"),
            "2021-06-17T23:00:00-0700");
}

// Входит в интервал
// Current time: 2021-06-17T23:20:11-03:00
// Config interval [13:00, 23:00)
// Calculated interval [2021-06-18T13:00:00-07:00, 2021-06-18T23:00:00-07:00)
TEST(GetTimeIntervalFromFormatHMTest20, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T23:20:11-0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("13:00"), RightBound("23:00"), Timezone("America/Los_Angeles"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "America/Los_Angeles"),
            "2021-06-17T13:00:00-0700");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "America/Los_Angeles"),
            "2021-06-17T23:00:00-0700");
}

//Слишком рано
// Current time: 2021-06-17T22:20:11+03:00
// Config interval [23:00, 01:00)
// Calculated interval [2021-06-16T23:00:00-07:00, 2021-06-17T01:00:00-07:00)
TEST(GetTimeIntervalFromFormatHMTest21, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T22:20:11+0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("01:00"), Timezone("America/Los_Angeles"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "America/Los_Angeles"),
            "2021-06-17T23:00:00-0700");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "America/Los_Angeles"),
            "2021-06-18T01:00:00-0700");
}

//Слишком рано
// Current time: 2021-06-17T10:20:11-03:00
// Config interval [23:00, 01:00)
// Calculated interval [2021-06-16T23:00:00-07:00, 2021-06-17T01:00:00-07:00)
TEST(GetTimeIntervalFromFormatHMTest22, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T10:20:11+0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("01:00"), Timezone("America/Los_Angeles"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "America/Los_Angeles"),
            "2021-06-16T23:00:00-0700");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "America/Los_Angeles"),
            "2021-06-17T01:00:00-0700");
}

//Входит в интервал тот же день
// Current time: 2021-06-17T23:20:11-03:00
// Config interval [23:00, 01:00)
// Calculated interval [2021-06-17T23:00:00-07:00, 2021-06-18T01:00:00-07:00)
TEST(GetTimeIntervalFromFormatHMTest23, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T23:20:11-0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("01:00"), Timezone("America/Los_Angeles"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "America/Los_Angeles"),
            "2021-06-17T23:00:00-0700");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "America/Los_Angeles"),
            "2021-06-18T01:00:00-0700");
}

//Входит в интервал полночь
// Current time: 2021-06-17T00:00:00-03:00
// Config interval [23:00, 01:00)
// Calculated interval [2021-06-16T23:00:00-07:00, 2021-06-17T01:00:00-07:00)
TEST(GetTimeIntervalFromFormatHMTest24, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T00:00:00-0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("01:00"), Timezone("America/Los_Angeles"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "America/Los_Angeles"),
            "2021-06-16T23:00:00-0700");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "America/Los_Angeles"),
            "2021-06-17T01:00:00-0700");
}

//Входит в интервал следующий день
// Current time: 2021-06-17T00:30:00-03:00
// Config interval [23:00, 01:00)
// Calculated interval [2021-06-16T23:00:00-07:00, 2021-06-17T01:00:00-07:00)
TEST(GetTimeIntervalFromFormatHMTest25, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T00:30:00-0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("01:00"), Timezone("America/Los_Angeles"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "America/Los_Angeles"),
            "2021-06-16T23:00:00-0700");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "America/Los_Angeles"),
            "2021-06-17T01:00:00-0700");
}

//Не входит в интервал следующий день
// Current time: 2021-06-17T01:30:00-03:00
// Config interval [23:00, 01:00)
// Calculated interval [2021-06-16T23:00:00-07:00, 2021-06-17T01:00:00-07:00)
TEST(GetTimeIntervalFromFormatHMTest26, HappyPath) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T01:30:00-0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("01:00"), Timezone("America/Los_Angeles"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "America/Los_Angeles"),
            "2021-06-16T23:00:00-0700");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "America/Los_Angeles"),
            "2021-06-17T01:00:00-0700");
}

TEST(GetTimeIntervalFromFormatHMTest, NowTimeOnLeftBorder) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T01:00:00+0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("01:00"), RightBound("02:00"), Timezone("Europe/Moscow"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "Europe/Moscow"),
            "2021-06-17T01:00:00+0300");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "Europe/Moscow"),
            "2021-06-17T02:00:00+0300");
}

TEST(GetTimeIntervalFromFormatHMTest, NowTimeOnRightBorder) {
  auto mock_now = ::utils::datetime::Stringtime("2021-06-17T02:00:00+0300");
  ::utils::datetime::MockNowSet(mock_now);
  auto result = eats_performer_support::helpers::GetTimeIntervalFromFormatHM(
      LeftBound("23:00"), RightBound("02:00"), Timezone("Europe/Moscow"));
  ASSERT_EQ(utils::datetime::Timestring(result.start, "Europe/Moscow"),
            "2021-06-17T23:00:00+0300");
  ASSERT_EQ(utils::datetime::Timestring(result.end, "Europe/Moscow"),
            "2021-06-18T02:00:00+0300");
}

TEST(AddSecondsTest, HappyPath) {
  auto time = ::utils::datetime::Stringtime("2021-06-17T02:00:00+0300");
  auto result = eats_performer_support::helpers::AddSeconds(time, 3600);
  ASSERT_EQ(utils::datetime::Timestring(result, "Europe/Moscow"),
            "2021-06-17T03:00:00+0300");
}
