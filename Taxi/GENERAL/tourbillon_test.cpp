#include <gtest/gtest.h>
#include <userver/storages/redis/mock_client_base.hpp>
#include <userver/utils/mock_now.hpp>
#include "tourbillon_impl.hpp"

using TourbillonImpl = tourbillon::TourbillonImpl;
using TourbillonSettings = tourbillon::TourbillonSettings;
using RedisShardSelector = tourbillon::RedisShardSelector;

using namespace std::chrono_literals;

namespace {

class RedisMock : public storages::redis::MockClientBase {
 public:
  size_t ShardsCount() const { return shards_count_; }

  storages::redis::RequestTime Time(size_t,
                                    const storages::redis::CommandControl&) {
    return storages::redis::CreateMockRequest<storages::redis::RequestTime>(
        now_);
  }

  void MockNowSet(const std::chrono::system_clock::time_point& now) {
    now_ = now;
  }

 private:
  size_t shards_count_;
  std::chrono::system_clock::time_point now_;
};

void MockNow(std::shared_ptr<RedisMock> redis,
             const std::chrono::system_clock::time_point& local_time,
             const std::chrono::system_clock::time_point& redis_time) {
  utils::datetime::MockNowSet(local_time);
  redis->MockNowSet(redis_time);
}

}  // unnamed namespace

TEST(tourbillon, Empty) {
  auto redis = std::make_shared<RedisMock>();
  auto tourbillon = TourbillonImpl{TourbillonSettings{}, redis};
  EXPECT_EQ(0ms, tourbillon.Adjustment());
  auto mma = tourbillon.GetMinMaxAverage();
  EXPECT_EQ(0, mma.GetCurrent().minimum);
  EXPECT_EQ(0, mma.GetCurrent().maximum);
  EXPECT_EQ(0, mma.GetCurrent().average);
}

TEST(tourbillon, SingleRedisSync) {
  auto redis = std::make_shared<RedisMock>();
  auto tourbillon = TourbillonImpl{TourbillonSettings{}, redis};
  auto local_time = std::chrono::system_clock::time_point();
  ::MockNow(redis, local_time, local_time - 5ms);
  tourbillon.RequestRedisTime();
  EXPECT_EQ(-5ms, tourbillon.Adjustment());
  auto mma = tourbillon.GetMinMaxAverage();
  EXPECT_EQ(-5, mma.GetCurrent().minimum);
  EXPECT_EQ(-5, mma.GetCurrent().maximum);
  EXPECT_EQ(-5, mma.GetCurrent().average);
}

TEST(tourbillon, History) {
  auto history_size = 3u;
  auto settings =
      TourbillonSettings{history_size, tourbillon::kDefaultShardSelector};
  auto redis = std::make_shared<RedisMock>();
  auto tourbillon = TourbillonImpl{std::move(settings), redis};
  auto local_time = std::chrono::system_clock::time_point();
  // expected deltas: 0, -1, -2, -3
  // remain in history: -1, -2, -3
  for (auto i = 0u; i < history_size + 1; ++i) {
    ::MockNow(redis, local_time - std::chrono::milliseconds(i),
              local_time - std::chrono::milliseconds(2 * i));
    tourbillon.RequestRedisTime();
  }
  EXPECT_EQ(-2ms, tourbillon.Adjustment());
  auto mma = tourbillon.GetMinMaxAverage();
  EXPECT_EQ(-3, mma.GetCurrent().minimum);
  EXPECT_EQ(-1, mma.GetCurrent().maximum);
  EXPECT_EQ(-2, mma.GetCurrent().average);
}

TEST(tourbillon, Rounding) {
  auto history_size = 4u;
  auto settings =
      TourbillonSettings{history_size, tourbillon::kDefaultShardSelector};
  auto redis = std::make_shared<RedisMock>();
  auto tourbillon = TourbillonImpl{std::move(settings), redis};
  auto local_time = std::chrono::system_clock::time_point();
  // expected deltas: 0, 1, 2, 3 (all remain in history)
  for (auto i = 0u; i < history_size; ++i) {
    ::MockNow(redis, local_time + std::chrono::milliseconds(i),
              local_time + std::chrono::milliseconds(2 * i));
    tourbillon.RequestRedisTime();
  }
  EXPECT_EQ(1ms, tourbillon.Adjustment());
  auto mma = tourbillon.GetMinMaxAverage();
  EXPECT_EQ(0, mma.GetCurrent().minimum);
  EXPECT_EQ(3, mma.GetCurrent().maximum);
  EXPECT_EQ(1, mma.GetCurrent().average);
}
