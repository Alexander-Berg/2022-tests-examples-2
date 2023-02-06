#include "redis.hpp"

#include <gtest/gtest.h>

using eats_eta::utils::impl::MyMakeRedisKey;

TEST(MakeRedisKeyTemplate, SimpleArgs) {
  ASSERT_EQ(MyMakeRedisKey("one_part"), "one_part");
  ASSERT_EQ(MyMakeRedisKey("a", 12, "c"), "a:12:c");
}

TEST(MakeRedisKeyTemplate, RedisKeyMacro) {
  int user_id = 134;
  std::string place_id = "896";
  ASSERT_EQ(
      MyMakeRedisKey(REDIS_KEY_PART(user_id), REDIS_KEY_PART(place_id), "cart"),
      "user_id:134:place_id:896:cart");
}
