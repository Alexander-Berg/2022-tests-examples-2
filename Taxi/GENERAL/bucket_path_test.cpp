#include <trackstory/bucket_path.hpp>
#include <trackstory/types.hpp>

#include <gtest/gtest.h>

using trackstory::RedisBucketPath;

TEST(trackstory, RedisBucketPathParseGood) {
  using namespace trackstory;
  using trackstory::TrackstoryRedisPrefix;
  const std::string redis_key = "raw/obj_id/19910102/01/02";
  const auto& bucket_path = RedisBucketPath::FromRedisKey(redis_key);
  RedisBucketPath exp_val{TrackstoryRedisPrefix{"raw"}, BucketObjId{"obj_id"},
                          BucketDate{"19910102"}, BucketHours{"01"},
                          BucketMinutes{"02"}};
  ASSERT_EQ(bucket_path.prefix, exp_val.prefix);
  ASSERT_EQ(bucket_path.obj_id, exp_val.obj_id);
  ASSERT_EQ(bucket_path.date, exp_val.date);
  ASSERT_EQ(bucket_path.bucket_hours_id, exp_val.bucket_hours_id);
  ASSERT_EQ(bucket_path.bucket_minutes_id, exp_val.bucket_minutes_id);
}

TEST(trackstory, RedisBucketPathBadDateLength) {
  const std::string redis_key = "raw/obj_id/1991012/01/02";
  EXPECT_THROW(RedisBucketPath::FromRedisKey(redis_key), std::runtime_error);
}

TEST(trackstory, RedisBucketPathBadDate) {
  const std::string redis_key = "raw/obj_id/19911312/01/02";
  EXPECT_THROW(RedisBucketPath::FromRedisKey(redis_key), std::runtime_error);
}

TEST(trackstory, RedisBucketPathNoMinutesBucket) {
  const std::string redis_key = "raw/obj_id/19910102/01";
  EXPECT_THROW(RedisBucketPath::FromRedisKey(redis_key), std::runtime_error);
}

TEST(trackstory, RedisBucketPathEmptyMinutesBucket) {
  const std::string redis_key = "raw/obj_id/19910102/01/";
  EXPECT_THROW(RedisBucketPath::FromRedisKey(redis_key), std::runtime_error);
}

TEST(trackstory, RedisBucketPathBadMinutesBucket) {
  const std::string redis_key = "raw/obj_id/19910102/01/as";
  EXPECT_THROW(RedisBucketPath::FromRedisKey(redis_key), std::invalid_argument);
}

TEST(trackstory, RedisBucketPathBadHoursBucket) {
  const std::string redis_key = "raw/obj_id/19910102/aa/02";
  EXPECT_THROW(RedisBucketPath::FromRedisKey(redis_key), std::invalid_argument);
}

TEST(trackstory, MdsDriverBucketPathParseGood) {
  using namespace trackstory;
  using trackstory::TrackstoryMdsPrefix;
  const std::string redis_key = "data/dbid/uuid/19910102/01";
  const auto& bucket_path = MdsDriverBucketPath::FromPathString(redis_key);
  MdsDriverBucketPath exp_val{TrackstoryMdsPrefix{"data"},
                              BucketDriverId{DriverId{"dbid_uuid"}},
                              BucketDate{"19910102"}, BucketHours{"01"}};
  ASSERT_EQ(bucket_path.prefix, exp_val.prefix);
  ASSERT_EQ(bucket_path.driver_id.GetUnderlying().GetDbidUndscrUuid(),
            exp_val.driver_id.GetUnderlying().GetDbidUndscrUuid());
  ASSERT_EQ(bucket_path.date, exp_val.date);
  ASSERT_EQ(bucket_path.bucket_hours_id, exp_val.bucket_hours_id);
}

TEST(trackstory, MdsDriverBucketPathParseGoodWithCompoundPrefix) {
  /// Test prefix with `/`
  using namespace trackstory;
  using trackstory::TrackstoryMdsPrefix;
  const std::string redis_key = "data/taxi/dbid/uuid/19910102/01";
  const auto& bucket_path = MdsDriverBucketPath::FromPathString(redis_key);
  MdsDriverBucketPath exp_val{TrackstoryMdsPrefix{"data/taxi"},
                              BucketDriverId{DriverId{"dbid_uuid"}},
                              BucketDate{"19910102"}, BucketHours{"01"}};
  ASSERT_EQ(bucket_path.prefix, exp_val.prefix);
  ASSERT_EQ(bucket_path.driver_id.GetUnderlying().GetDbidUndscrUuid(),
            exp_val.driver_id.GetUnderlying().GetDbidUndscrUuid());
  ASSERT_EQ(bucket_path.date, exp_val.date);
  ASSERT_EQ(bucket_path.bucket_hours_id, exp_val.bucket_hours_id);
}
