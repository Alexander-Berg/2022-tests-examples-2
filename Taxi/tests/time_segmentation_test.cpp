#ifdef USERVER
#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>
#else
#include <gtest/gtest.h>       // Y_IGNORE
#include <utils/datetime.hpp>  // Y_IGNORE
#endif

#include <experiments3_common/models/errors.hpp>
#include <experiments3_common/models/kwargs.hpp>
#include <experiments3_common/models/predicates.hpp>

const auto kTimestamp =
    experiments3::models::default_kwargs::kRequestTimestampMinutes;

size_t ToMinutes(std::chrono::system_clock::time_point tp) {
  return std::chrono::duration_cast<std::chrono::minutes>(tp.time_since_epoch())
      .count();
}

auto MakeTimestampKwargs(experiments3::models::KwargTypeInt value) {
  namespace exp3 = experiments3::models;
  auto pair = std::make_pair(kTimestamp, value);
#ifdef USERVER
  return exp3::KwargsMap(exp3::KwargsMap::Map{pair});
#else
  return exp3::Kwargs{pair};
#endif
}

auto MakeTimestampKwargs(std::chrono::system_clock::time_point tp) {
  return MakeTimestampKwargs(experiments3::models::KwargTypeInt(ToMinutes(tp)));
}

// precalculated offset for "test_salt"
const uint32_t kTestOffset = 2052342303;
const auto kMinutesInDay = std::chrono::minutes(60) * 24;

TEST(TimeSegmentationPredicate, SegmentationWithoutSalt) {
  auto range_from = std::chrono::minutes(0);
  auto range_to = std::chrono::minutes(30);
  auto period = std::chrono::minutes(90);

  auto start = utils::datetime::Stringtime("2022-02-19T12:00:00.0000Z");
  experiments3::models::TimeSegmentation predicate(
      kTimestamp, start, range_from.count(), range_to.count(), period.count());

  // if argument is less than start time, predicate is false
  ASSERT_FALSE(predicate(MakeTimestampKwargs(0)));
  EXPECT_THROW(predicate(MakeTimestampKwargs(-10)),
               experiments3::models::ProtocolError);

  auto i = 1;
  std::set matched_checks = {1, 2, 3, 10, 11, 12};
  for (auto ts = start; ts < start + 2 * period;
       ts += std::chrono::minutes(10)) {
    if (matched_checks.count(i)) {
      ASSERT_TRUE(predicate(MakeTimestampKwargs(ts)));
    } else {
      ASSERT_FALSE(predicate(MakeTimestampKwargs(ts)));
    }
    i++;
  }
}

TEST(TimeSegmentationPredicate, SegmentationWithSalt) {
  auto range_from = std::chrono::minutes(0);
  auto range_to = std::chrono::minutes(20);
  auto period = std::chrono::minutes(120);

  auto start = utils::datetime::Stringtime("2022-02-19T12:00:00.0000Z");
  const auto offset_in_period = kTestOffset % period.count();

  experiments3::models::TimeSegmentation predicate(
      kTimestamp, start, range_from.count(), range_to.count(), period.count(),
      "test_salt");

  auto i = 1;
  std::set matched_checks = {1, 2, 13, 14};
  // subtract kOffsetInPeriodMinutes to compensate salt offset
  auto shifted_start = start - std::chrono::minutes(offset_in_period) + period;
  for (auto ts = shifted_start; ts < shifted_start + 2 * period;
       ts += std::chrono::minutes(10)) {
    if (matched_checks.count(i)) {
      ASSERT_TRUE(predicate(MakeTimestampKwargs(ts)));
    } else {
      ASSERT_FALSE(predicate(MakeTimestampKwargs(ts)));
    }
    i++;
  }
}

TEST(TimeSegmentationPredicate, BadDailyTimestampIncrement) {
  // daily_ts_increment is bigger than period
  EXPECT_THROW(
      experiments3::models::TimeSegmentation predicate(
          kTimestamp, std::chrono::system_clock::now(), 0, 15, 100, "test_salt",
          110  // daily_ts_increment
          ),
      experiments3::models::ProtocolError);
}

TEST(TimeSegmentationPredicate, CheckDailyIncrementThreshold) {
  auto range_from = std::chrono::minutes(0);
  auto range_to = std::chrono::minutes(20);
  auto period = std::chrono::minutes(60);

  auto start = utils::datetime::Stringtime("2022-02-19T23:00:00.0000Z");

  experiments3::models::TimeSegmentation predicate(
      kTimestamp, start, range_from.count(), range_to.count(), period.count(),
      "",  // empty salt
      20   // daily_ts_increment
  );

  // predicate works as usual
  ASSERT_TRUE(predicate(MakeTimestampKwargs(start)));
  ASSERT_TRUE(predicate(MakeTimestampKwargs(start + std::chrono::minutes(10))));
  ASSERT_FALSE(
      predicate(MakeTimestampKwargs(start + std::chrono::minutes(20))));
  ASSERT_FALSE(
      predicate(MakeTimestampKwargs(start + std::chrono::minutes(40))));

  // new day starts and timestamp is shifted for 20 minutes forward,
  // now period is [40, 60)
  ASSERT_FALSE(
      predicate(MakeTimestampKwargs(start + std::chrono::minutes(60))));
  ASSERT_FALSE(
      predicate(MakeTimestampKwargs(start + std::chrono::minutes(80))));
  ASSERT_FALSE(
      predicate(MakeTimestampKwargs(start + std::chrono::minutes(90))));
  ASSERT_TRUE(
      predicate(MakeTimestampKwargs(start + std::chrono::minutes(100))));
  ASSERT_TRUE(
      predicate(MakeTimestampKwargs(start + std::chrono::minutes(110))));
  ASSERT_FALSE(
      predicate(MakeTimestampKwargs(start + std::chrono::minutes(120))));
}

TEST(TimeSegmentationPredicate, DailyTimestampIncrement) {
  auto range_from = std::chrono::minutes(0);
  auto range_to = std::chrono::minutes(40);
  auto period = std::chrono::minutes(120);
  auto interval_len = range_to - range_from;

  auto start = utils::datetime::Stringtime("2022-02-19T12:00:00.0000Z");
  const auto offset_in_period = kTestOffset % period.count();

  experiments3::models::TimeSegmentation predicate(
      kTimestamp, start, range_from.count(), range_to.count(), period.count(),
      "test_salt",
      40  // daily_ts_increment
  );

  std::set matched_checks_at_first_day = {0, 1, 2, 3, 12, 13, 14, 15};

  for (auto day = 0; day < 8; ++day) {
    std::set<int> matched_checks;
    for (auto index : matched_checks_at_first_day) {
      // every day predicate shifts to left (condition is satisfied earlier)
      matched_checks.insert(
          (2 * period.count() + index - interval_len.count() / 10 * day) %
          (2 * period.count() / 10));
    }
    auto i = 0;
    auto shifted_start = start - std::chrono::minutes(offset_in_period) +
                         period + day * kMinutesInDay;
    for (auto ts = shifted_start; ts < shifted_start + 2 * period;
         ts += std::chrono::minutes(10)) {
      if (matched_checks.count(i)) {
        ASSERT_TRUE(predicate(MakeTimestampKwargs(ts)));
      } else {
        ASSERT_FALSE(predicate(MakeTimestampKwargs(ts)));
      }
      i++;
    }
  }
}
