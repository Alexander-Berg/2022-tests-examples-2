#include <userver/utest/utest.hpp>

#include <components/last_activity.hpp>
#include "last_activity_cache_mock.hpp"
#include "partner_activity_storage_mock.hpp"

namespace testing {

using ::eats_partners::components::last_activity::ComponentImpl;
using ::eats_partners::models::last_activity::Cache;
using ::eats_partners::models::partner_activity::Storage;

struct LastActivityComponentFixture {
  std::shared_ptr<LastActivityCacheMock> cache_mock =
      std::make_shared<LastActivityCacheMock>();
  std::shared_ptr<PartnerActivityStorageMock> storage_mock =
      std::make_shared<PartnerActivityStorageMock>();

  ComponentImpl component;

  const std::chrono::milliseconds delay = std::chrono::milliseconds(10);
  const PartnerId partner_id{42};

  LastActivityComponentFixture()
      : component(std::make_shared<Storage>(storage_mock),
                  std::make_shared<Cache>(cache_mock)) {
    component.UpdateDelay(delay);
  }

  decltype(auto) MakeResult(const CacheState state,
                            const std::chrono::system_clock::time_point point =
                                utils::datetime::Now()) {
    return MakeFoundItem(state, delay, point);
  }
};

using TimesCalled = int;
using UpdateTestParams = std::tuple<Cache::State, TimesCalled>;

struct UpdateTest : public LastActivityComponentFixture,
                    public TestWithParam<UpdateTestParams> {};

INSTANTIATE_TEST_SUITE_P(LastActivityComponentTest, UpdateTest,
                         Values(UpdateTestParams{Cache::State::kHit, 0},
                                UpdateTestParams{Cache::State::kMiss, 1},
                                UpdateTestParams{Cache::State::kStale, 1}));

TEST_P(UpdateTest, should_call_Update_and_Put_depending_on_state) {
  const auto [state, times] = GetParam();

  const auto cache_result = MakeResult(state);
  const auto now = utils::datetime::Now();
  partner::LastActivityAt act_at{now};
  {
    InSequence seq;
    EXPECT_CALL(*cache_mock, Get(partner_id))
        .WillOnce(Return(cache_result.second));
    EXPECT_CALL(*storage_mock, UpsertActivity(partner_id))
        .Times(times)
        .WillRepeatedly(Return(act_at));
    EXPECT_CALL(*cache_mock, Put(partner_id, Cache::Item{act_at, now}))
        .Times(times);
  }

  component.UpdateActivity(partner_id);
}

struct LastActivityComponentGetTest : public LastActivityComponentFixture,
                                      public Test {};

TEST_F(LastActivityComponentGetTest,
       should_not_get_activity_from_storage_on_cache_hit) {
  const auto point = utils::datetime::Now() - std::chrono::hours(1);
  const auto cache_result = MakeResult(Cache::State::kHit, point);
  const std::vector<partner::Activity> expected{
      {partner_id, cache_result.second->last_activity_at}};

  EXPECT_CALL(*cache_mock, Get(partner_id))
      .WillOnce(Return(cache_result.second));
  const auto result = component.GetActivity({partner_id}, std::nullopt);
  ASSERT_EQ(result, expected);
}

TEST_F(LastActivityComponentGetTest,
       should_get_activity_from_storage_only_on_stale_or_miss_cache) {
  const auto now = utils::datetime::Now();
  const std::vector<partner::Activity> expected{
      {PartnerId{1}, partner::LastActivityAt{now - std::chrono::hours(1)}},
      {PartnerId{2}, partner::LastActivityAt{now - std::chrono::hours(2)}},
      {PartnerId{3}, partner::LastActivityAt{now - std::chrono::hours(3)}}};

  {
    InSequence seq;
    EXPECT_CALL(*cache_mock, Get(PartnerId{2}))
        .WillOnce(Return(MakeResult(Cache::State::kMiss).second));
    EXPECT_CALL(*cache_mock, Get(PartnerId{1}))
        .WillOnce(
            Return(MakeResult(Cache::State::kHit, now - std::chrono::hours(1))
                       .second));
    EXPECT_CALL(*cache_mock, Get(PartnerId{3}))
        .WillOnce(Return(MakeResult(Cache::State::kStale).second));

    EXPECT_CALL(*storage_mock,
                GetActivity(std::vector<PartnerId>{PartnerId{2}, PartnerId{3}}))
        .WillOnce(
            Return(std::vector<partner::Activity>{expected[1], expected[2]}));

    EXPECT_CALL(
        *cache_mock,
        Put(PartnerId{2},
            Cache::Item{partner::LastActivityAt{now - std::chrono::hours(2)},
                        now}))
        .Times(1);
    EXPECT_CALL(
        *cache_mock,
        Put(PartnerId{3},
            Cache::Item{partner::LastActivityAt{now - std::chrono::hours(3)},
                        now}))
        .Times(1);
  }
  const auto result = component.GetActivity(
      {PartnerId{2}, PartnerId{1}, PartnerId{3}}, std::nullopt);
  ASSERT_EQ(result, expected);
}

}  // namespace testing
