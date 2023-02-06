#include "bucket_path.hpp"

#include <chrono>

#include <gtest/gtest.h>

#include "driver-id/types.hpp"
#include "types.hpp"

using internal_trackstory::track::MdsBucketPath;

TEST(internal_trackstory, BucketPathParseGood) {
  using namespace internal_trackstory;
  using namespace internal_trackstory::track;

  const std::string key = "raw/taxi/obj/id/19910102/2";
  const auto& bucket_path = RedisBucketPath::FromString(key);
  MdsBucketPath exp_val{
      Prefix{"raw"}, Pipeline{"taxi"},
      ObjectId{driver_id::DriverDbid{"obj"}, driver_id::DriverUuid{"id"}},
      BucketDate{"19910102"}, BucketTime{"2"}};
  ASSERT_EQ(bucket_path.prefix, exp_val.prefix);
  ASSERT_EQ(bucket_path.object, exp_val.object);
  ASSERT_EQ(bucket_path.date, exp_val.date);
  ASSERT_EQ(bucket_path.time, exp_val.time);
  ASSERT_EQ(bucket_path.pipeline, exp_val.pipeline);
}

TEST(internal_trackstory, BucketPathBadDateLength) {
  const std::string key = "raw/taxi/obj/id/1991012/2";
  EXPECT_THROW(MdsBucketPath::FromString(key), std::runtime_error);
}

TEST(internal_trackstory, BucketPathBadDate) {
  const std::string key = "raw/taxi/obj/id/19911312/2";
  EXPECT_THROW(MdsBucketPath::FromString(key), std::runtime_error);
}

TEST(internal_trackstory, BucketPathNoTime) {
  const std::string key = "raw/taxi/obj/id/19910102";
  EXPECT_THROW(MdsBucketPath::FromString(key), std::runtime_error);
}

TEST(internal_trackstory, BucketPathEmptyTime) {
  const std::string key = "raw/taxi/obj/id/19910102/";
  EXPECT_THROW(MdsBucketPath::FromString(key), std::runtime_error);
}

TEST(internal_trackstory, BucketPathBadTime) {
  const std::string key = "raw/taxi/obj/id/19910102/as";
  EXPECT_THROW(MdsBucketPath::FromString(key), std::invalid_argument);
}

TEST(internal_trackstory, BucketPathGenerateBucketsSingleDay) {
  using namespace internal_trackstory;
  using namespace internal_trackstory::track;

  // 2022-01-01 21:00:05
  TimePoint from{std::chrono::seconds{1641070805}};

  // 2022-01-01 23:00:05
  TimePoint to = from + std::chrono::hours{2};

  auto buckets = MdsBucketPath::GenerateBuckets(
      from, to, Prefix{"raw"}, Pipeline{"taxi"},
      ObjectId{driver_id::DriverDbid{"obj"}, driver_id::DriverUuid{"id"}});

  ASSERT_EQ(buckets.size(), 3);
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/21"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/22"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/23"), buckets.end());
}

TEST(internal_trackstory, BucketPathGenerateBucketsTwoDays) {
  using namespace internal_trackstory;

  // 2022-01-01 22:00:05
  TimePoint from{std::chrono::seconds{1641070805}};

  // 2022-01-02 01:00:05
  TimePoint to = from + std::chrono::hours{4};

  auto buckets = MdsBucketPath::GenerateBuckets(
      from, to, Prefix{"raw"}, Pipeline{"taxi"},
      ObjectId{driver_id::DriverDbid{"obj"}, driver_id::DriverUuid{"id"}});

  ASSERT_EQ(buckets.size(), 5);
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/21"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/22"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/23"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/0"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/1"), buckets.end());
}

TEST(internal_trackstory, BucketPathGenerateBucketsThreeDays) {
  using namespace internal_trackstory;
  using namespace internal_trackstory::track;

  // 2022-01-01 22:00:05
  TimePoint from{std::chrono::seconds{1641070805}};

  // 2022-01-02 01:00:05
  TimePoint to = from + std::chrono::hours{28};

  auto buckets = MdsBucketPath::GenerateBuckets(
      from, to, Prefix{"raw"}, Pipeline{"taxi"},
      ObjectId{driver_id::DriverDbid{"obj"}, driver_id::DriverUuid{"id"}});

  ASSERT_EQ(buckets.size(), 29);
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/21"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/22"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/23"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/0"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/1"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/2"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/3"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/4"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/5"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/6"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/7"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/8"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/9"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/10"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/11"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/12"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/13"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/14"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/15"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/16"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/17"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/18"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/19"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/20"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/21"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/22"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220102/23"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220103/0"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220103/1"), buckets.end());
}

TEST(internal_trackstory, BucketPathGenerateRedisBucketsSingleDay) {
  using namespace internal_trackstory;
  using namespace internal_trackstory::track;

  // 2022-01-01 21:00:05
  TimePoint from{std::chrono::seconds{1641070805}};

  // 2022-01-01 22:00:05
  TimePoint to = from + std::chrono::hours{1};

  auto buckets = RedisBucketPath::GenerateBuckets(
      from, to, Prefix{"raw"}, Pipeline{"taxi"},
      ObjectId{driver_id::DriverDbid{"obj"}, driver_id::DriverUuid{"id"}});

  ASSERT_EQ(buckets.size(), 13);

  // 24 hours * 12 per hour = 288 per day
  // 21:00:05 is in bucket 21 * 12 = 252
  // 22:00:05 is in bucket 22 * 12 = 264 = 252 + 12
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/252"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/253"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/254"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/255"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/256"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/257"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/258"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/259"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/260"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/261"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/262"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/263"), buckets.end());
  ASSERT_NE(buckets.find("raw/taxi/obj/id/20220101/264"), buckets.end());
}
