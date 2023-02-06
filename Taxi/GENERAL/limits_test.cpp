#include "limits.hpp"

#include <gtest/gtest.h>

TEST(Limits, Serialize) {
  {
    models::Limits limits;
    EXPECT_EQ(models::ParseLimits(models::SerializeLimits(limits)), limits);
  }
  {
    models::Limits limits;
    limits.version = 1;
    EXPECT_EQ(models::ParseLimits(models::SerializeLimits(limits)), limits);
  }
  {
    models::Limits limits;
    limits.version = 1;
    limits.limits["path.1"]["client.1"] = models::Limit{};
    limits.limits["path.1"]["client.2"] =
        models::Limit{1, 2, std::chrono::seconds(3)};
    limits.limits["path.2"]["client.1"] =
        models::Limit{3, 4, std::chrono::seconds(5)};
    EXPECT_EQ(models::ParseLimits(models::SerializeLimits(limits)), limits);
  }
}

TEST(Limits, Select) {
  models::Limits limits;
  EXPECT_FALSE(limits.Select("path", "client").has_value());
  EXPECT_FALSE(limits.Select("", "client").has_value());
  EXPECT_FALSE(limits.Select("path", "").has_value());
  EXPECT_FALSE(limits.Select("", "").has_value());

  limits.limits["path1"]["client1"] = models::Limit{1};
  limits.limits["path1"]["client2"] = models::Limit{2};
  limits.limits["path1"][""] = models::Limit{3};
  limits.limits[""]["client3"] = models::Limit{4};

  auto limit = limits.Select("path1", "client1");
  ASSERT_TRUE(limit.has_value());
  EXPECT_EQ(limit->rate, 1);
  limit = limits.Select("path1", "client2");
  ASSERT_TRUE(limit.has_value());
  EXPECT_EQ(limit->rate, 2);
  limit = limits.Select("path1", "client4");
  ASSERT_TRUE(limit.has_value());
  EXPECT_EQ(limit->rate, 3);
  limit = limits.Select("path2", "client3");
  ASSERT_TRUE(limit.has_value());
  EXPECT_EQ(limit->rate, 4);
}
