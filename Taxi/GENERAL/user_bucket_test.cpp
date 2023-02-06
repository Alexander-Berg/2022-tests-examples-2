#include <gtest/gtest.h>

#include "user_bucket.hpp"

TEST(UserBucket, RedisBucketName) {
  geohistory::utils::UserBucket bucket{"user_id", "20170102", 4};
  EXPECT_EQ(bucket.GetRedisBucketName(), "history:20170102:04:user_id");
  bucket.bucket_id = 0;
  EXPECT_EQ(bucket.GetRedisBucketName(), "history:20170102:00:user_id");
  bucket.bucket_id = 23;
  EXPECT_EQ(bucket.GetRedisBucketName(), "history:20170102:23:user_id");
}

TEST(UserBucket, S3BucketName) {
  geohistory::utils::UserBucket bucket{"user_id", "20170102", 4};
  EXPECT_EQ(bucket.GetS3BucketName(), "history/user_id/20170102/04");
  bucket.bucket_id = 0;
  EXPECT_EQ(bucket.GetS3BucketName(), "history/user_id/20170102/00");
  bucket.bucket_id = 23;
  EXPECT_EQ(bucket.GetS3BucketName(), "history/user_id/20170102/23");
}

TEST(UserBucket, ConvertRedisToS3BucketName) {
  EXPECT_EQ(geohistory::utils::UserBucket::ConvertRedisToS3BucketName(
                "history:20170102:04:user_id"),
            "history/user_id/20170102/04");
  EXPECT_EQ(geohistory::utils::UserBucket::ConvertRedisToS3BucketName(
                "history:20170102:00:user_id"),
            "history/user_id/20170102/00");
  EXPECT_EQ(geohistory::utils::UserBucket::ConvertRedisToS3BucketName(
                "history:20170102:23:user_id"),
            "history/user_id/20170102/23");
}
