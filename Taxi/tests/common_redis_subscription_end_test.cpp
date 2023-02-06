#include <userver/utest/utest.hpp>

#include <userver/utils/datetime.hpp>

#include "common/redis/subscription_end.hpp"

TEST(SubscriptionEndTest, RedisKeyBuiltCorrectly) {
  using namespace billing_time_events;
  auto key_from_doc_id = common::redis::subscription_end::RedisKey(123);
  EXPECT_EQ(key_from_doc_id, "sub:123");
  auto key_from_subscription_ref =
      common::redis::subscription_end::RedisKey("subscription/doc_id/234");
  EXPECT_EQ(key_from_subscription_ref, "sub:234");
}

TEST(SubscriptionEndTest, RedisValueBuiltCorrectly) {
  using namespace billing_time_events;
  auto sub_end =
      utils::datetime::GuessStringtime("2020-10-06T23:52:00Z", "UTC");
  auto value = common::redis::subscription_end::RedisValue(sub_end);
  ASSERT_EQ(value, "2020-10-06T23:52:00.000000+00:00");
}

TEST(SubscriptionEndTest, RedisValueParsedCorrectly) {
  using namespace billing_time_events;
  auto sub_end = common::redis::subscription_end::FromRedisValue(
      "2020-10-06T23:52:00+00:00");
  auto expected =
      utils::datetime::GuessStringtime("2020-10-06T23:52:00Z", "UTC");
  ASSERT_EQ(sub_end, expected);
}
