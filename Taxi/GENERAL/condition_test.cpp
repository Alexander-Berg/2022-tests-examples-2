#include <userver/utest/utest.hpp>

#include <sharding/condition.hpp>

namespace processing::sharding {

TEST(ShardingCondition, UuidEdgeCases) {
  conditions::ByUuid condition("foo", {0});

  SchemaParameters sp{
      {{"foo", 1}},
  };

  EXPECT_THROW(condition.DoesMatch({}, sp), std::runtime_error);
  EXPECT_THROW(condition.DoesMatch({{"foo", ""}}, sp), std::runtime_error);
  EXPECT_THROW(condition.DoesMatch({{"foo", "  "}}, sp), std::runtime_error);
  EXPECT_THROW(condition.DoesMatch({{"foo", "z"}}, sp), std::runtime_error);
  EXPECT_THROW(condition.DoesMatch({{"foo", "#$%#$%"}}, sp),
               std::runtime_error);

  EXPECT_TRUE(condition.DoesMatch({{"foo", "0"}}, sp));
  EXPECT_TRUE(condition.DoesMatch({{"foo", "1"}}, sp));
  EXPECT_TRUE(condition.DoesMatch({{"foo", "2"}}, sp));
  EXPECT_TRUE(condition.DoesMatch({{"foo", "3"}}, sp));
  EXPECT_TRUE(condition.DoesMatch({{"foo", "e"}}, sp));
  EXPECT_TRUE(condition.DoesMatch({{"foo", "f"}}, sp));
  EXPECT_TRUE(condition.DoesMatch({{"foo", "acff"}}, sp));
}

TEST(ShardingCondition, UuidHappyPath) {
  conditions::ByUuid condition01("foo", {0, 1});
  conditions::ByUuid condition23("foo", {2, 3});

  SchemaParameters sp{
      {{"foo", 4}},
  };

  EXPECT_TRUE(
      condition01.DoesMatch({{"foo", "0000000000000000000000000"}}, sp));
  EXPECT_TRUE(
      condition01.DoesMatch({{"foo", "0000000000000000000000001"}}, sp));
  EXPECT_FALSE(
      condition01.DoesMatch({{"foo", "0000000000000000000000002"}}, sp));
  EXPECT_FALSE(
      condition01.DoesMatch({{"foo", "0000000000000000000000003"}}, sp));
  EXPECT_TRUE(
      condition01.DoesMatch({{"foo", "0000000000000000000000004"}}, sp));
  EXPECT_TRUE(
      condition01.DoesMatch({{"foo", "0000000000000000000000005"}}, sp));

  EXPECT_FALSE(
      condition23.DoesMatch({{"foo", "0000000000000000000000000"}}, sp));
  EXPECT_FALSE(
      condition23.DoesMatch({{"foo", "0000000000000000000000001"}}, sp));
  EXPECT_TRUE(
      condition23.DoesMatch({{"foo", "0000000000000000000000002"}}, sp));
  EXPECT_TRUE(
      condition23.DoesMatch({{"foo", "0000000000000000000000003"}}, sp));
  EXPECT_FALSE(
      condition23.DoesMatch({{"foo", "0000000000000000000000004"}}, sp));
  EXPECT_FALSE(
      condition23.DoesMatch({{"foo", "0000000000000000000000005"}}, sp));
}

TEST(ShardingCondition, ValuesCases) {
  conditions::ByValues condition("test-field", {"foo", "bar"});

  EXPECT_TRUE(condition.DoesMatch({{"test-field", "foo"}}, {}));
  EXPECT_TRUE(condition.DoesMatch({{"test-field", "bar"}}, {}));
  EXPECT_FALSE(condition.DoesMatch({{"test-field", "baz"}}, {}));

  EXPECT_THROW(condition.DoesMatch({}, {}), std::runtime_error);
}

}  // namespace processing::sharding
