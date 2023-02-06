#include <gtest/gtest.h>
#include <chrono>

#include <cctz/time_zone.h>

#include <components/sending_component.hpp>
#include <db/crm_scheduler_pg_types.hpp>

namespace {

using namespace crm_scheduler;
using namespace crm_scheduler::components;
using namespace crm_scheduler::models;

std::chrono::system_clock::time_point buildTimePoint(int y, int m = 1,
                                                     int d = 1, int hh = 0,
                                                     int mm = 0, int ss = 0) {
  const auto civil_seconds = cctz::civil_second(y, m, d, hh, mm, ss);
  return cctz::convert(civil_seconds, cctz::utc_time_zone());
}

bool isInWorkingTime(const CampaignWorkingScope& campaign_working_scope,
                     std::chrono::system_clock::time_point time_point) {
  return crm_scheduler::isInWorkingTime(campaign_working_scope, time_point,
                                        "Etc/GMT+0");
}

bool isWorkingTimeExpired(const CampaignWorkingScope& campaign_working_scope,
                          std::chrono::system_clock::time_point time_point) {
  return crm_scheduler::isWorkingTimeExpired(campaign_working_scope, time_point,
                                             "Etc/GMT+0");
}

}  // namespace

const CampaignWorkingScope sending_working_time{
    CampaignId{},
    GroupId{},
    buildTimePoint(2021, 10, 1),
    buildTimePoint(2021, 10, 31, 23, 59),
    false,
    8 * 60 * 60,
    17 * 60 * 60,
    false};

TEST(SendingComponent, HappyPath) {
  const auto now = buildTimePoint(2021, 10, 1, 8, 0);
  EXPECT_FALSE(isWorkingTimeExpired(sending_working_time, now));
  EXPECT_TRUE(isInWorkingTime(sending_working_time, now));
}

TEST(SendingComponent, WorkPeriodExpired) {
  const auto now = buildTimePoint(2021, 11, 1, 8, 0);
  EXPECT_TRUE(isWorkingTimeExpired(sending_working_time, now));
  EXPECT_FALSE(isInWorkingTime(sending_working_time, now));
}

TEST(SendingComponent, WorkTimeExpired) {
  const auto now = buildTimePoint(2021, 10, 31, 17, 0);
  EXPECT_TRUE(isWorkingTimeExpired(sending_working_time, now));
  EXPECT_FALSE(isInWorkingTime(sending_working_time, now));
}

TEST(SendingComponent, WorkTimeIsNotExpired) {
  const auto now = buildTimePoint(2021, 10, 31, 16, 59);
  EXPECT_FALSE(isWorkingTimeExpired(sending_working_time, now));
  EXPECT_TRUE(isInWorkingTime(sending_working_time, now));
}

TEST(SendingComponent, WorkTimeIsExpiredButPeriodIsNot) {
  const auto now = buildTimePoint(2021, 10, 30, 17, 10);
  EXPECT_FALSE(isInWorkingTime(sending_working_time, now));
  EXPECT_FALSE(isWorkingTimeExpired(sending_working_time, now));
}

TEST(SendingComponent, WorkTimeAndPeriodExpired) {
  const auto work_time = CampaignWorkingScope{CampaignId{},
                                              GroupId{},
                                              buildTimePoint(2021, 10, 1),
                                              buildTimePoint(2021, 10, 31),
                                              false,
                                              8 * 60 * 60,
                                              17 * 60 * 60,
                                              false};
  const auto now = buildTimePoint(2021, 10, 30, 17, 10);
  EXPECT_TRUE(isWorkingTimeExpired(work_time, now));
  EXPECT_FALSE(isInWorkingTime(work_time, now));
}

const CampaignWorkingScope intersecting_sending_working_time{
    CampaignId{},
    GroupId{},
    buildTimePoint(2021, 10, 1, 12, 00),
    buildTimePoint(2021, 10, 31, 14, 59),
    false,
    10 * 60 * 60,
    18 * 60 * 60,
    false};

TEST(SendingComponent, FirstDay__MinuteBeforeDaytimeStarts__Intersecting) {
  const auto now = buildTimePoint(2021, 10, 1, 9, 59);
  EXPECT_FALSE(isWorkingTimeExpired(intersecting_sending_working_time, now));
  EXPECT_FALSE(isInWorkingTime(intersecting_sending_working_time, now));
}

TEST(SendingComponent, FirstDay__DaytimeStarts__Intersecting) {
  const auto now = buildTimePoint(2021, 10, 1, 10, 0);
  EXPECT_FALSE(isWorkingTimeExpired(intersecting_sending_working_time, now));
  EXPECT_FALSE(isInWorkingTime(intersecting_sending_working_time, now));
}

TEST(SendingComponent, FirstDay__MinuteBeforeScopeStarts__Intersecting) {
  const auto now = buildTimePoint(2021, 10, 1, 11, 59);
  EXPECT_FALSE(isWorkingTimeExpired(intersecting_sending_working_time, now));
  EXPECT_FALSE(isInWorkingTime(intersecting_sending_working_time, now));
}

TEST(SendingComponent, FirstDay__ScopeStarts__Intersecting) {
  const auto now = buildTimePoint(2021, 10, 1, 12, 00);
  EXPECT_FALSE(isWorkingTimeExpired(intersecting_sending_working_time, now));
  EXPECT_TRUE(isInWorkingTime(intersecting_sending_working_time, now));
}

TEST(SendingComponent, FirstDay__ScopeEndThatTimeInAMonth__Intersecting) {
  const auto now = buildTimePoint(2021, 10, 1, 15, 00);
  EXPECT_FALSE(isWorkingTimeExpired(intersecting_sending_working_time, now));
  EXPECT_TRUE(isInWorkingTime(intersecting_sending_working_time, now));
}

TEST(SendingComponent, FirstDay__LastSecondOfDaytime__Intersecting) {
  const auto now = buildTimePoint(2021, 10, 1, 17, 59, 59);
  EXPECT_FALSE(isWorkingTimeExpired(intersecting_sending_working_time, now));
  EXPECT_TRUE(isInWorkingTime(intersecting_sending_working_time, now));
}

TEST(SendingComponent, FirstDay__DaytimeEnds__Intersecting) {
  const auto now = buildTimePoint(2021, 10, 1, 18, 00);
  EXPECT_FALSE(isWorkingTimeExpired(intersecting_sending_working_time, now));
  EXPECT_FALSE(isInWorkingTime(intersecting_sending_working_time, now));
}

TEST(SendingComponent, LastDay__MinuteBeforeDaytimeStarts__Intersecting) {
  const auto now = buildTimePoint(2021, 10, 31, 9, 59);
  EXPECT_FALSE(isWorkingTimeExpired(intersecting_sending_working_time, now));
  EXPECT_FALSE(isInWorkingTime(intersecting_sending_working_time, now));
}

TEST(SendingComponent, LastDay__DaytimeStarts__Intersecting) {
  const auto now = buildTimePoint(2021, 10, 31, 10, 0);
  EXPECT_FALSE(isWorkingTimeExpired(intersecting_sending_working_time, now));
  EXPECT_TRUE(isInWorkingTime(intersecting_sending_working_time, now));
}

TEST(SendingComponent, LastDay__MinuteBeforeScopeStarts__Intersecting) {
  const auto now = buildTimePoint(2021, 10, 31, 11, 59);
  EXPECT_FALSE(isWorkingTimeExpired(intersecting_sending_working_time, now));
  EXPECT_TRUE(isInWorkingTime(intersecting_sending_working_time, now));
}

TEST(SendingComponent, LastDay__ScopeStartedMonthAgo__Intersecting) {
  const auto now = buildTimePoint(2021, 10, 31, 12, 00);
  EXPECT_FALSE(isWorkingTimeExpired(intersecting_sending_working_time, now));
  EXPECT_TRUE(isInWorkingTime(intersecting_sending_working_time, now));
}

TEST(SendingComponent, LastDay__ScopeEndsThatTimeInAMonth__Intersecting) {
  const auto now = buildTimePoint(2021, 10, 31, 15, 00);
  EXPECT_TRUE(isWorkingTimeExpired(intersecting_sending_working_time, now));
  EXPECT_FALSE(isInWorkingTime(intersecting_sending_working_time, now));
}

TEST(SendingComponent, LastSecondOfDaytime__Intersecting) {
  const auto now = buildTimePoint(2021, 10, 31, 17, 59, 59);
  EXPECT_TRUE(isWorkingTimeExpired(intersecting_sending_working_time, now));
  EXPECT_FALSE(isInWorkingTime(intersecting_sending_working_time, now));
}

TEST(SendingComponent, LastDay__DaytimeEnds__Intersecting) {
  const auto now = buildTimePoint(2021, 10, 31, 18, 00);
  EXPECT_TRUE(isWorkingTimeExpired(intersecting_sending_working_time, now));
  EXPECT_FALSE(isInWorkingTime(intersecting_sending_working_time, now));
}
