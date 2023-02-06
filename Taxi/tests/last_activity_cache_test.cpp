#include <userver/utest/utest.hpp>

#include <models/last_activity_cache.hpp>
#include "last_activity_cache_mock.hpp"

namespace testing {

using ::eats_partners::models::last_activity::Cache;

struct LastActivityCacheFixture {
  std::shared_ptr<LastActivityCacheMock> cache_mock;
  Cache cache;

  const std::chrono::milliseconds delay = std::chrono::milliseconds(10);
  const PartnerId partner_id{42};

  LastActivityCacheFixture()
      : cache_mock(std::make_shared<LastActivityCacheMock>()),
        cache(cache_mock) {}

  decltype(auto) MakeResult(const Cache::State state,
                            const std::chrono::system_clock::time_point point =
                                utils::datetime::Now()) {
    return MakeFoundItem(state, delay, point);
  }
};

struct StatisticsResult {
  size_t hits{0};
  size_t misses{0};
  size_t stale{0};
};

using StatisticsTestParams = std::tuple<Cache::State, StatisticsResult>;

struct StatisticsTest : public LastActivityCacheFixture,
                        public TestWithParam<StatisticsTestParams> {};

INSTANTIATE_TEST_SUITE_P(
    LastActivityCacheTest, StatisticsTest,
    Values(StatisticsTestParams{Cache::State::kHit, StatisticsResult{1, 0, 0}},
           StatisticsTestParams{Cache::State::kMiss, StatisticsResult{0, 1, 0}},
           StatisticsTestParams{Cache::State::kStale,
                                StatisticsResult{0, 0, 1}}));

TEST_P(StatisticsTest, should_increase_cache_statistics) {
  const auto [state, expected] = GetParam();
  const auto result = MakeResult(state);

  EXPECT_CALL(*cache_mock, Get(partner_id)).WillOnce(Return(result.second));

  ASSERT_EQ(cache.Get(partner_id, delay), result);

  auto& statistics = cache.GetStatistics();
  const auto& total = statistics.total;
  auto& recent = statistics.recent.GetCurrentCounter();

  ASSERT_EQ(total.hits, expected.hits);
  ASSERT_EQ(total.misses, expected.misses);
  ASSERT_EQ(total.stale, expected.stale);

  ASSERT_EQ(recent.hits, expected.hits);
  ASSERT_EQ(recent.misses, expected.misses);
  ASSERT_EQ(recent.stale, expected.stale);
}

}  // namespace testing
