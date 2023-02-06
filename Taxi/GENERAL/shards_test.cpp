#include <sharding/shards.hpp>

#include <userver/utest/utest.hpp>

namespace {

using Shards = geobus::sharding::Shards;

TEST(Shards, Empty) {
  Shards shards;

  ASSERT_TRUE(shards.empty());
  ASSERT_EQ(shards.size(), 0u);

  for ([[maybe_unused]] const auto shard : shards) {
    FAIL() << "Default constructed Shards should be empty";
  }
}

TEST(Shards, OnlyOne) {
  auto shards = Shards::OnlyOne(5);

  ASSERT_FALSE(shards.empty());
  ASSERT_EQ(shards.size(), 1u);
  ASSERT_EQ(shards[0], 5);
}

using TestParam = std::vector<int>;
struct TestShardsPushBack : public ::testing::TestWithParam<TestParam> {};

TEST_P(TestShardsPushBack, PushBack) {
  const auto& input = GetParam();
  const auto shards = [&input]() {
    Shards result;
    for (const auto shard : input) {
      result.push_back(shard);
    }
    return result;
  }();

  ASSERT_EQ(shards.size(), input.size());
  ASSERT_TRUE(std::equal(shards.begin(), shards.end(), input.begin()));
}

INSTANTIATE_TEST_SUITE_P(TestShardsPushBack, TestShardsPushBack,
                         ::testing::ValuesIn(std::vector<TestParam>{
                             {},
                             {1},
                             {1, 2},
                             {1, 2, 3},
                             {1, 2, 3, 4},
                             {1, 2, 3, 4, 5},
                             {1, 2, 3, 4, 5, 6},
                             {1, 2, 3, 4, 5, 6, 7}}));

}  // namespace
