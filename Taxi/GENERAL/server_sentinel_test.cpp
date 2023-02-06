#include "server_common_sentinel_test.hpp"

#include <testing/utest/in_env_test.hpp>

namespace {
// 100ms should be enough, but valgrind is too slow
const auto kSentinelChangeHostsWaitingTime = std::chrono::milliseconds(500);

}  // namespace

#define EXPECT_FOR(count, duration, expect)  \
  do {                                       \
    for (int i = 0; i < (count); i++) {      \
      expect;                                \
      std::this_thread::sleep_for(duration); \
    }                                        \
  } while (false)

TEST(Redis, SentinelSingleMaster) {
  TestInEnv([]() {
    const size_t master_count = 1;
    const size_t slave_count = 0;
    const size_t sentinel_count = 1;
    const int magic_value = 2;

    SentinelTest sentinel_test(sentinel_count, master_count, slave_count,
                               magic_value);
    auto& sentinel = sentinel_test.SentinelClient();

    EXPECT_TRUE(sentinel_test.Master().WaitForFirstPingReply(kSmallPeriod));

    auto res = sentinel.Get("value").Get();
    ASSERT_TRUE(res->data.IsInt());
    EXPECT_TRUE(res->data.GetInt() == magic_value);
  });
}

TEST(Redis, SentinelMastersChanging) {
  TestInEnv([]() {
    const size_t master_count = 3;
    const size_t slave_count = 0;
    const size_t sentinel_count = 1;
    const int magic_value_add = 98;
    size_t redis_idx{0};

    SentinelTest sentinel_test(sentinel_count, master_count, slave_count,
                               magic_value_add);
    auto& sentinel = sentinel_test.SentinelClient();

    const size_t req_count = master_count;
    for (size_t i = 0; i < req_count; i++) {
      auto old_redis_idx = redis_idx;
      redis_idx = i * master_count / req_count;
      if (redis_idx != old_redis_idx) {
        sentinel_test.Sentinel().RegisterSentinelMastersHandler(
            {{sentinel_test.RedisName(), kLocalhost,
              sentinel_test.Master(redis_idx).GetPort()}});
        sentinel.ForceUpdateHosts();
        EXPECT_TRUE(sentinel_test.Master(redis_idx).WaitForFirstPingReply(
            kSentinelChangeHostsWaitingTime));
      }
      auto res = sentinel.Get("value").Get();
      LOG_DEBUG() << "got reply with type=" << res->data.GetTypeString()
                  << " data=" << res->data.ToDebugString();
      ASSERT_TRUE(res->data.IsInt());
      EXPECT_EQ(redis_idx,
                static_cast<size_t>(res->data.GetInt() - magic_value_add))
          << " i=" << i;
    }
  });
}

TEST(Redis, SentinelMastersChangingErrors) {
  TestInEnv([]() {
    const size_t master_count = 5;
    const size_t slave_count = 0;
    const size_t sentinel_count = 3;
    const size_t bad_redis_idx = 3;
    const int magic_value_add = 132;
    const size_t redis_thread_count = 3;
    size_t redis_idx{0};

    SentinelTest sentinel_test(sentinel_count, master_count, slave_count,
                               magic_value_add, 0, redis_thread_count);
    auto& sentinel = sentinel_test.SentinelClient();

    const size_t req_count = master_count;
    size_t expected_redis_idx_reply_from = redis_idx;
    for (size_t i = 0; i < req_count; i++) {
      auto old_redis_idx = redis_idx;
      redis_idx = i * master_count / req_count;
      if (redis_idx != old_redis_idx) {
        for (size_t sentinel_idx = 0; sentinel_idx < sentinel_count;
             sentinel_idx++) {
          size_t quorum = sentinel_count / 2 + 1;
          if (redis_idx == bad_redis_idx && sentinel_idx < quorum) {
            sentinel_test.Sentinel(sentinel_idx)
                .RegisterErrorReplyHandler(
                    "SENTINEL", {"MASTERS"},
                    "some incorrect SENTINEL MASTERS reply");
          } else {
            sentinel_test.Sentinel(sentinel_idx)
                .RegisterSentinelMastersHandler(
                    {{sentinel_test.RedisName(), kLocalhost,
                      sentinel_test.Master(redis_idx).GetPort()}});
          }
        }
        sentinel.ForceUpdateHosts();
        if (redis_idx == bad_redis_idx) {
          EXPECT_FOR(1, kSentinelChangeHostsWaitingTime,
                     EXPECT_FALSE(
                         sentinel_test.Master(redis_idx).WaitForFirstPingReply(
                             kSentinelChangeHostsWaitingTime)));
        } else {
          EXPECT_TRUE(sentinel_test.Master(redis_idx).WaitForFirstPingReply(
              kSentinelChangeHostsWaitingTime));
          expected_redis_idx_reply_from = redis_idx;
        }
      }
      auto res = sentinel.Get("value").Get();
      LOG_DEBUG() << "got reply with type=" << res->data.GetTypeString()
                  << " data=" << res->data.ToDebugString();
      ASSERT_TRUE(res->data.IsInt());
      EXPECT_EQ(expected_redis_idx_reply_from,
                static_cast<size_t>(res->data.GetInt() - magic_value_add))
          << " i=" << i;
    }
  });
}

TEST(Redis, SentinelMasterAndSlave) {
  TestInEnv([]() {
    const size_t master_count = 1;
    const size_t slave_count = 1;
    const size_t sentinel_count = 1;
    const int magic_value_master = 238;
    const int magic_value_slave = -238;

    SentinelTest sentinel_test(sentinel_count, master_count, slave_count,
                               magic_value_master, magic_value_slave);
    auto& sentinel = sentinel_test.SentinelClient();

    EXPECT_TRUE(sentinel_test.Master().WaitForFirstPingReply(kSmallPeriod));
    EXPECT_TRUE(sentinel_test.Slave().WaitForFirstPingReply(kSmallPeriod));

    {
      auto res = sentinel.Get("value").Get();
      ASSERT_TRUE(res->data.IsInt());
      EXPECT_TRUE(res->data.GetInt() == magic_value_slave);
    }

    {
      redis::CommandControl force_master_cc;
      force_master_cc.force_request_to_master = true;
      auto res = sentinel.Get("value", force_master_cc).Get();
      ASSERT_TRUE(res->data.IsInt());
      EXPECT_TRUE(res->data.GetInt() == magic_value_master);
    }
  });
}

TEST(Redis, SentinelCcRetryToMasterOnNilReply) {
  TestInEnv([]() {
    const size_t master_count = 1;
    const size_t slave_count = 1;
    const size_t sentinel_count = 1;
    const int magic_value_master = 238;

    SentinelTest sentinel_test(sentinel_count, master_count, slave_count,
                               magic_value_master);
    auto& sentinel = sentinel_test.SentinelClient();

    EXPECT_TRUE(sentinel_test.Master().WaitForFirstPingReply(kSmallPeriod));
    EXPECT_TRUE(sentinel_test.Slave().WaitForFirstPingReply(kSmallPeriod));

    sentinel_test.Slave().RegisterNilReplyHandler("GET");

    {
      auto res = sentinel.Get("slave_nil").Get();
      EXPECT_TRUE(res->data.IsNil());
    }
    {
      redis::CommandControl force_master_cc;
      force_master_cc.max_retries = 1;
      force_master_cc.force_request_to_master = true;
      auto res = sentinel.Get("slave_nil", force_master_cc).Get();
      EXPECT_TRUE(res->data.IsInt());
      EXPECT_TRUE(res->data.GetInt() == magic_value_master);
    }
    {
      redis::CommandControl no_force_master_cc;
      no_force_master_cc.max_retries = 2;
      no_force_master_cc.force_request_to_master = false;
      auto res = sentinel.Get("slave_nil", no_force_master_cc).Get();
      EXPECT_TRUE(res->data.IsNil());
    }
    {
      redis::CommandControl cc;
      cc.max_retries = 1;
      auto res =
          sentinel.Get("slave_nil", redis::kRetryNilFromMaster, cc).Get();
      EXPECT_TRUE(res->data.IsNil());
    }
    {
      redis::CommandControl cc;
      cc.max_retries = 2;
      auto res =
          sentinel.Get("slave_nil", redis::kRetryNilFromMaster, cc).Get();
      EXPECT_TRUE(res->data.IsInt());
      EXPECT_TRUE(res->data.GetInt() == magic_value_master);
    }
    {
      redis::CommandControl cc;
      cc.max_retries = 2;
      auto res = sentinel.Get("slave_nil", cc).Get();
      EXPECT_TRUE(res->data.IsNil());
    }

    auto slave_nil_handler =
        sentinel_test.Slave().RegisterNilReplyHandler("GET", {"master_nil"});
    auto master_nil_handler =
        sentinel_test.Master().RegisterNilReplyHandler("GET", {"master_nil"});
    {
      redis::CommandControl cc;
      cc.max_retries = 5;
      auto res =
          sentinel.Get("master_nil", redis::kRetryNilFromMaster, cc).Get();
      EXPECT_TRUE(res->data.IsNil());
      EXPECT_EQ(slave_nil_handler->GetReplyCount(), 1ul);
      EXPECT_EQ(master_nil_handler->GetReplyCount(), 1ul);
    }
  });
}

TEST(Redis, SentinelForceShardIdx) {
  TestInEnv([]() {
    const size_t shard_count = 3;
    const size_t sentinel_count = 1;
    const int magic_value_add = 98;

    SentinelShardTest sentinel_test(sentinel_count, shard_count,
                                    magic_value_add, magic_value_add);
    auto& sentinel = sentinel_test.SentinelClient();

    for (size_t shard_idx = 0; shard_idx < shard_count; shard_idx++) {
      EXPECT_TRUE(sentinel_test.Master(shard_idx).WaitForFirstPingReply(
          kSentinelChangeHostsWaitingTime))
          << "shard_idx=" << shard_idx;
      redis::CommandControl cc;
      cc.force_shard_idx = shard_idx;
      auto res = sentinel.Get("value", cc).Get();
      LOG_DEBUG() << "got reply with type=" << res->data.GetTypeString()
                  << " data=" << res->data.ToDebugString();
      ASSERT_TRUE(res->data.IsInt());
      EXPECT_EQ(shard_idx,
                static_cast<size_t>(res->data.GetInt() - magic_value_add))
          << " shard_idx=" << shard_idx;
    }
  });
}