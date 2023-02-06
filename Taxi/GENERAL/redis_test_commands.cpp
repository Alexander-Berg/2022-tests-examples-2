#include "redis_test_commands.hpp"

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/logging/log.hpp>
#include <userver/server/handlers/exceptions.hpp>
#include <userver/storages/redis/component.hpp>
#include <userver/storages/redis/transaction.hpp>

namespace {

const std::string kRedisClientName = "taxi-tmp";
const storages::redis::CommandControl kDefaultCc{};

storages::redis::CommandControl GetForceMasterCc() {
  storages::redis::CommandControl cc;
  cc.force_request_to_master = true;
  return cc;
}

// read from master
const storages::redis::CommandControl kForceMasterCc = GetForceMasterCc();

template <typename T>
void ExpectEq(T got, T expected, T delta) {
  if (got < expected - delta) {
    throw std::runtime_error("got < expected - delta (" + std::to_string(got) +
                             " < " + std::to_string(expected) + " - " +
                             std::to_string(delta) + ')');
  }
  if (got > expected + delta) {
    throw std::runtime_error("got > expected + delta (" + std::to_string(got) +
                             " > " + std::to_string(expected) + " + " +
                             std::to_string(delta) + ')');
  }
}

template <typename T>
void ExpectEq(std::optional<T> got, T expected, T delta) {
  if (!got)
    throw std::runtime_error("got (nil), expected " + std::to_string(expected) +
                             " with delta=" + std::to_string(delta));
  return ExpectEq(*got, expected, delta);
}

template <typename Got, typename Expected = Got>
void ExpectEq(const Got& got, const Expected& expected) {
  if (got != expected) {
    throw std::runtime_error("got != expected");
  }
}

template <>
void ExpectEq<std::optional<std::string>, std::string>(
    const std::optional<std::string>& got, const std::string& expected) {
  if (!got) std::runtime_error("got (nil), expected " + expected);
  if (*got != expected) {
    throw std::runtime_error("got != expected (" + *got + " != " + expected +
                             ')');
  }
}

#define EXPECT_EQ(...)                   \
  do {                                   \
    try {                                \
      ExpectEq(__VA_ARGS__);             \
    } catch (const std::exception& ex) { \
      LOG_ERROR() << ex.what();          \
      throw;                             \
    }                                    \
  } while (0)

#define EXPECT_NOTHROW(x)                \
  do {                                   \
    try {                                \
      x;                                 \
    } catch (const std::exception& ex) { \
      LOG_ERROR() << ex.what();          \
      throw;                             \
    }                                    \
  } while (0)

#define EXPECT_THROW(x, ex_t)                                    \
  do {                                                           \
    bool catched = false;                                        \
    try {                                                        \
      x;                                                         \
    } catch (const ex_t&) {                                      \
      catched = true;                                            \
    }                                                            \
    if (!catched) {                                              \
      auto msg = std::string("exception of type '") + #ex_t +    \
                 "' was not thrown in expression '" + #x + '\''; \
      LOG_ERROR() << msg;                                        \
      throw std::runtime_error(msg);                             \
    }                                                            \
  } while (0)

void TestPing(const storages::redis::ClientPtr& redis) {
  redis->Ping(0, kDefaultCc).Get();
  redis->Ping(0, "test msg", kDefaultCc).Get();
}

void TestDbsize(const storages::redis::ClientPtr& redis) {
  redis->Dbsize(0, kDefaultCc).Get();
}

void TestGetSetAppend(const storages::redis::ClientPtr& redis) {
  static const std::string kNewValue = "new_value";
  static const std::string kExistedValue = "existed_value";
  static const std::string kJoinedValue = kNewValue + kExistedValue;
  static const std::string kKey = "get_set_append_key";
  static const std::string kNotExistingKey = "not_existing_key";

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
  EXPECT_EQ(redis->Type(kKey, kForceMasterCc).Get(),
            storages::redis::KeyType::kNone);
  EXPECT_EQ(redis->Strlen(kKey, kForceMasterCc).Get(), 0u);
  EXPECT_EQ(redis->Exists(kKey, kForceMasterCc).Get(), 0u);

  // test empty requests
  EXPECT_EQ(redis->Exists(std::vector<std::string>{}, kForceMasterCc).Get(),
            0u);
  EXPECT_EQ(redis->Del(std::vector<std::string>{}, kDefaultCc).Get(), 0u);
  EXPECT_EQ(redis->Mget({}, kForceMasterCc).Get(),
            std::vector<std::optional<std::string>>{});

  EXPECT_NOTHROW(redis->Append(kKey, kNewValue, kDefaultCc).Get());
  EXPECT_EQ(redis->Exists(kKey, kForceMasterCc).Get(), 1u);
  EXPECT_EQ(
      redis->Exists({kNotExistingKey, kKey, kKey, kKey}, kForceMasterCc).Get(),
      3u);
  EXPECT_NOTHROW(redis->Append(kKey, kExistedValue, kDefaultCc).Get());
  EXPECT_EQ(redis->Get(kKey, kForceMasterCc).Get(), kJoinedValue);
  EXPECT_EQ(redis->Strlen(kKey, kForceMasterCc).Get(), kJoinedValue.size());
  EXPECT_EQ(redis->Type(kKey, kForceMasterCc).Get(),
            storages::redis::KeyType::kString);

  EXPECT_EQ(redis->Mget({kKey, kNotExistingKey}, kForceMasterCc).Get(),
            {std::make_optional(kJoinedValue), std::optional<std::string>{}});

  EXPECT_EQ(redis->Del(kKey, kDefaultCc).Get(), 1u);
  EXPECT_EQ(redis->Get(kKey, kForceMasterCc).Get(),
            std::optional<std::string>{});

  EXPECT_NOTHROW(redis->Set(kKey, kNewValue, kDefaultCc).Get());
  EXPECT_EQ(redis->Get(kKey, kForceMasterCc).Get(), kNewValue);
  EXPECT_NOTHROW(redis->Set(kKey, kExistedValue, kDefaultCc).Get());
  EXPECT_EQ(redis->Getset(kKey, kNewValue, kDefaultCc).Get(), kExistedValue);
  EXPECT_EQ(redis->Get(kKey, kForceMasterCc).Get(), kNewValue);
  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
  EXPECT_EQ(redis->Getset(kKey, kNewValue, kDefaultCc).Get(),
            std::optional<std::string>{});
  EXPECT_EQ(redis->Get(kKey, kForceMasterCc).Get(), kNewValue);

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
}

void TestIncr(const storages::redis::ClientPtr& redis) {
  static const std::string kKey = "incr_key";
  static const int64_t kNewValue = 123;

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
  EXPECT_EQ(redis->Incr(kKey, kDefaultCc).Get(), 1u);
  EXPECT_NOTHROW(redis->Set(kKey, std::to_string(kNewValue), kDefaultCc).Get());
  EXPECT_EQ(redis->Incr(kKey, kDefaultCc).Get(), kNewValue + 1);

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
}

void TestHgetHsetHdel(const storages::redis::ClientPtr& redis) {
  static const std::string kNewValue = "new_value";
  static const std::string kNewValue2 = "new_value2";
  static const std::string kExistedValue = "existed_value";
  static const std::string kKey = "hget_hset_key";
  static const std::string kField = "field";
  static const std::string kField2 = "field2";

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
  EXPECT_EQ(redis->Hgetall(kKey, kForceMasterCc).Get(),
            std::unordered_map<std::string, std::string>{});
  EXPECT_EQ(redis->Hkeys(kKey, kForceMasterCc).Get(),
            std::vector<std::string>{});
  EXPECT_EQ(redis->Hvals(kKey, kForceMasterCc).Get(),
            std::vector<std::string>{});
  EXPECT_EQ(redis->Hlen(kKey, kForceMasterCc).Get(), 0u);
  EXPECT_EQ(
      redis->Hmget(kKey, std::vector<std::string>{}, kForceMasterCc).Get(),
      std::vector<std::optional<std::string>>{});
  EXPECT_EQ(
      redis
          ->Hmget(kKey, std::vector<std::string>{kField, kField2},
                  kForceMasterCc)
          .Get(),
      std::vector<std::optional<std::string>>{std::nullopt, std::nullopt});

  EXPECT_EQ(redis->Hget(kKey, kField, kForceMasterCc).Get(),
            std::optional<std::string>{});
  EXPECT_EQ(redis->Hexists(kKey, kField, kForceMasterCc).Get(), 0u);

  EXPECT_EQ(redis->Hset(kKey, kField, kNewValue, kDefaultCc).Get(),
            storages::redis::HsetReply::kCreated);
  EXPECT_EQ(redis->Hset(kKey, kField, kExistedValue, kDefaultCc).Get(),
            storages::redis::HsetReply::kUpdated);
  EXPECT_EQ(redis->Type(kKey, kForceMasterCc).Get(),
            storages::redis::KeyType::kHash);
  EXPECT_EQ(redis->Hexists(kKey, kField, kForceMasterCc).Get(), 1u);

  EXPECT_EQ(redis->Hgetall(kKey, kForceMasterCc).Get(),
            {{kField, kExistedValue}});
  EXPECT_EQ(redis->Hget(kKey, kField, kForceMasterCc).Get(), kExistedValue);
  EXPECT_EQ(redis->Hdel(kKey, kField, kDefaultCc).Get(), 1u);
  EXPECT_EQ(redis->Hdel(kKey, kField, kDefaultCc).Get(), 0u);
  EXPECT_EQ(redis->Hdel(kKey, std::vector<std::string>{}, kDefaultCc).Get(),
            0u);

  EXPECT_NOTHROW(redis
                     ->Hmset(kKey, {{kField, kNewValue}, {kField2, kNewValue2}},
                             kDefaultCc)
                     .Get());
  EXPECT_NOTHROW(redis->Hmset(kKey, {}, kDefaultCc).Get());
  EXPECT_EQ(redis->Hgetall(kKey, kForceMasterCc).Get(),
            {{kField, kNewValue}, {kField2, kNewValue2}});
  EXPECT_EQ(redis
                ->Hmget(kKey, std::vector<std::string>{kField, kField2},
                        kForceMasterCc)
                .Get(),
            std::vector<std::optional<std::string>>{kNewValue, kNewValue2});

  EXPECT_EQ(redis->Hkeys(kKey, kForceMasterCc).Get(), {kField, kField2});
  EXPECT_EQ(redis->Hvals(kKey, kForceMasterCc).Get(), {kNewValue, kNewValue2});
  EXPECT_EQ(redis->Hlen(kKey, kForceMasterCc).Get(), 2u);

  EXPECT_EQ(
      redis->Hdel(kKey, std::vector<std::string>{kField, kField2}, kDefaultCc)
          .Get(),
      2u);

  EXPECT_EQ(redis->Hsetnx(kKey, kField, kNewValue, kDefaultCc).Get(), true);
  EXPECT_EQ(redis->Hsetnx(kKey, kField, kExistedValue, kDefaultCc).Get(),
            false);

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
}

void TestHincrby(const storages::redis::ClientPtr& redis) {
  static const std::string kKey = "hincrby_key";
  static const std::string kIntField = "int_field";
  static const std::string kFloatField = "float_field";
  static const int64_t kIncrValueInt1 = 123;
  static const int64_t kIncrValueInt2 = 234;
  static const double kIncrValueDouble1 = 45.6;
  static const double kIncrValueDouble2 = 5.67;
  static const double kEps = 1e-6;

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());

  EXPECT_EQ(redis->Hincrby(kKey, kIntField, kIncrValueInt1, kDefaultCc).Get(),
            kIncrValueInt1);
  EXPECT_EQ(redis->Hincrby(kKey, kIntField, kIncrValueInt2, kDefaultCc).Get(),
            kIncrValueInt1 + kIncrValueInt2);
  EXPECT_EQ(
      redis->Hincrbyfloat(kKey, kFloatField, kIncrValueDouble1, kDefaultCc)
          .Get(),
      kIncrValueDouble1, kEps);
  EXPECT_EQ(
      redis->Hincrbyfloat(kKey, kFloatField, kIncrValueDouble2, kDefaultCc)
          .Get(),
      kIncrValueDouble1 + kIncrValueDouble2, kEps);

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
}

void TestTtl(const storages::redis::ClientPtr& redis) {
  static const std::string kValue = "new_value";
  static const std::string kKey = "test_ttl_key";
  static const std::string kNotExistingKey = "not_existing_key";
  static const std::chrono::seconds kTtl{218};
  static const std::chrono::milliseconds kMilliTtl{218 * 1000};

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
  EXPECT_NOTHROW(redis->Setex(kKey, kTtl, kValue, kDefaultCc).Get());
  auto res_ttl = [&]() {
    EXPECT_NOTHROW(return redis->Ttl(kKey, kForceMasterCc).Get());
  }();
  EXPECT_EQ(res_ttl.KeyExists(), true);
  EXPECT_EQ(res_ttl.KeyHasExpiration(), true);
  size_t delta_sec = 10;
  EXPECT_EQ(res_ttl.GetExpireSeconds(),
            static_cast<size_t>(kTtl.count()) - delta_sec, delta_sec);

  EXPECT_EQ(redis->Persist(kKey, kDefaultCc).Get(),
            storages::redis::PersistReply::kTimeoutRemoved);
  EXPECT_EQ(redis->Persist(kKey, kDefaultCc).Get(),
            storages::redis::PersistReply::kKeyOrTimeoutNotFound);
  EXPECT_EQ(redis->Persist(kNotExistingKey, kDefaultCc).Get(),
            storages::redis::PersistReply::kKeyOrTimeoutNotFound);
  EXPECT_EQ(redis->Expire(kKey, kTtl, kDefaultCc).Get(),
            storages::redis::ExpireReply::kTimeoutWasSet);
  EXPECT_EQ(redis->Expire(kNotExistingKey, kTtl, kDefaultCc).Get(),
            storages::redis::ExpireReply::kKeyDoesNotExist);
  EXPECT_EQ(redis->Pexpire(kKey, kMilliTtl, kDefaultCc).Get(),
            storages::redis::ExpireReply::kTimeoutWasSet);
  EXPECT_EQ(redis->Pexpire(kNotExistingKey, kMilliTtl, kDefaultCc).Get(),
            storages::redis::ExpireReply::kKeyDoesNotExist);

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
}

void TestSortedSet(const storages::redis::ClientPtr& redis) {
  static const std::string kKey = "test_z_key";
  static const double kScore1 = 1.1;
  static const double kScore2 = 0.2;
  static const std::string kMember1 = "member1";
  static const std::string kMember2 = "member2";
  static const double kEps = 1e-6;

  using ZaddOptions = storages::redis::ZaddOptions;

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
  EXPECT_EQ(redis->Zcard(kKey, kForceMasterCc).Get(), 0u);
  EXPECT_EQ(redis->Zadd(kKey, kScore1, kMember1, kDefaultCc).Get(), 1u);
  EXPECT_EQ(redis->Type(kKey, kForceMasterCc).Get(),
            storages::redis::KeyType::kZset);
  EXPECT_EQ(redis->Zcard(kKey, kForceMasterCc).Get(), 1u);
  EXPECT_EQ(redis
                ->Zadd(kKey, kScore1, kMember1, ZaddOptions::Exist::kAddIfExist,
                       kDefaultCc)
                .Get(),
            0u);
  EXPECT_EQ(redis
                ->Zadd(kKey, kScore2, kMember1,
                       ZaddOptions::Exist::kAddIfNotExist, kDefaultCc)
                .Get(),
            0u);
  EXPECT_EQ(redis->Zadd(kKey, kScore2, kMember2, kDefaultCc).Get(), 1u);
  EXPECT_EQ(redis->Zadd(kKey, kScore1, kMember2, kDefaultCc).Get(), 0u);
  EXPECT_EQ(redis
                ->Zadd(kKey, kScore2, kMember2,
                       ZaddOptions::ReturnValue::kChangedCount, kDefaultCc)
                .Get(),
            1u);

  {
    std::vector<std::string> expected{kMember2, kMember1};
    auto result = [&]() {
      EXPECT_NOTHROW(return redis
                         ->Zrangebyscore(kKey, std::min(kScore1, kScore2),
                                         std::max(kScore1, kScore2),
                                         kForceMasterCc)
                         .Get());
    }();
    EXPECT_EQ(result.size(), expected.size());
    for (size_t idx = 0; idx < result.size(); idx++) {
      EXPECT_EQ(result.at(idx), expected.at(idx));
    }
  }

  {
    std::vector<std::string> expected{kMember2, kMember1};
    auto result = [&]() {
      EXPECT_NOTHROW(return redis->Zrange(kKey, 0, 1, kForceMasterCc).Get());
    }();
    EXPECT_EQ(result.size(), expected.size());
    for (size_t idx = 0; idx < result.size(); idx++) {
      EXPECT_EQ(result.at(idx), expected.at(idx));
    }
  }

  {
    std::vector<std::string> expected{kMember2};
    auto result = [&]() {
      EXPECT_NOTHROW(return redis->Zrange(kKey, -2, -2, kForceMasterCc).Get());
    }();
    EXPECT_EQ(result.size(), expected.size());
    for (size_t idx = 0; idx < result.size(); idx++) {
      EXPECT_EQ(result.at(idx), expected.at(idx));
    }
  }

  {
    std::vector<storages::redis::MemberScore> expected{{kMember2, kScore2},
                                                       {kMember1, kScore1}};
    auto result = [&]() {
      EXPECT_NOTHROW(
          return redis->ZrangeWithScores(kKey, -2, -1, kForceMasterCc).Get());
    }();
    EXPECT_EQ(result.size(), expected.size());
    for (size_t idx = 0; idx < result.size(); idx++) {
      EXPECT_EQ(result.at(idx), expected.at(idx));
    }
  }

  EXPECT_EQ(redis->ZaddIncr(kKey, kScore1, kMember1, kDefaultCc).Get(),
            kScore1 * 2, kEps);
  EXPECT_EQ(redis->ZaddIncrExisting(kKey, -kScore1, kMember1, kDefaultCc).Get(),
            kScore1, kEps);
  EXPECT_EQ(
      redis->ZaddIncrExisting(kKey, kScore1, "not_existing_member", kDefaultCc)
          .Get(),
      std::optional<double>{});

  {
    std::vector<storages::redis::MemberScore> expected{{kMember2, kScore2},
                                                       {kMember1, kScore1}};
    auto result = [&]() {
      EXPECT_NOTHROW(
          return redis
              ->ZrangebyscoreWithScores(kKey, "-inf", "+inf", kForceMasterCc)
              .Get());
    }();
    EXPECT_EQ(result.size(), expected.size());
    for (size_t idx = 0; idx < result.size(); idx++) {
      EXPECT_EQ(result.at(idx).member, expected.at(idx).member);
      EXPECT_EQ(result.at(idx).score, expected.at(idx).score, kEps);
    }
  }

  {
    storages::redis::RangeOptions range_options;
    range_options.offset = 1;
    std::vector<storages::redis::MemberScore> expected{{kMember1, kScore1}};
    auto result = [&]() {
      EXPECT_NOTHROW(return redis
                         ->ZrangebyscoreWithScores(kKey, "-inf", "+inf",
                                                   range_options,
                                                   kForceMasterCc)
                         .Get());
    }();
    EXPECT_EQ(result.size(), expected.size());
    for (size_t idx = 0; idx < result.size(); idx++) {
      EXPECT_EQ(result.at(idx).member, expected.at(idx).member);
      EXPECT_EQ(result.at(idx).score, expected.at(idx).score, kEps);
    }
  }

  {
    storages::redis::RangeOptions range_options;
    range_options.count = 1;
    std::vector<storages::redis::MemberScore> expected{{kMember2, kScore2}};
    auto result = [&]() {
      EXPECT_NOTHROW(return redis
                         ->ZrangebyscoreWithScores(kKey, "-inf", "+inf",
                                                   range_options,
                                                   kForceMasterCc)
                         .Get());
    }();
    EXPECT_EQ(result.size(), expected.size());
    for (size_t idx = 0; idx < result.size(); idx++) {
      EXPECT_EQ(result.at(idx).member, expected.at(idx).member);
      EXPECT_EQ(result.at(idx).score, expected.at(idx).score, kEps);
    }
  }

  EXPECT_EQ(redis->Zremrangebyrank(kKey, 1, 1, kDefaultCc).Get(), 1u);
  {
    std::vector<std::string> expected{kMember2};
    auto result = [&]() {
      EXPECT_NOTHROW(return redis->Zrange(kKey, 0, -1, kForceMasterCc).Get());
    }();
    EXPECT_EQ(result.size(), expected.size());
    for (size_t idx = 0; idx < result.size(); idx++) {
      EXPECT_EQ(result.at(idx), expected.at(idx));
    }
  }

  EXPECT_EQ(redis->Zremrangebyrank(kKey, -1, -1, kDefaultCc).Get(), 1u);
  EXPECT_EQ(redis->Zcard(kKey, kForceMasterCc).Get(), 0u);

  EXPECT_EQ(redis->Zadd(kKey, kScore1, kMember1, kDefaultCc).Get(), 1u);
  EXPECT_EQ(redis->Zadd(kKey, kScore2, kMember2, kDefaultCc).Get(), 1u);

  EXPECT_EQ(redis->Zrem(kKey, std::vector<std::string>{}, kDefaultCc).Get(),
            0u);
  EXPECT_EQ(redis->Zrem(kKey, kMember1, kDefaultCc).Get(), 1u);
  EXPECT_EQ(
      redis
          ->Zrem(kKey, std::vector<std::string>{kMember1, kMember2}, kDefaultCc)
          .Get(),
      1u);
}

void TestSortedSetVector(const storages::redis::ClientPtr& redis) {
  static const std::string kKey = "test_z_key_v";
  static const double kScore1 = 1.1;
  static const double kScore2 = 0.2;
  static const std::string kMember1 = "member1";
  static const std::string kMember2 = "member2";
  static const double kEps = 1e-6;

  using ZaddOptions = storages::redis::ZaddOptions;

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
  EXPECT_EQ(redis->Zcard(kKey, kForceMasterCc).Get(), 0u);
  EXPECT_EQ(
      redis->Zadd(kKey, {{kScore1, kMember1}, {kScore2, kMember2}}, kDefaultCc)
          .Get(),
      2u);
  EXPECT_EQ(redis->Type(kKey, kForceMasterCc).Get(),
            storages::redis::KeyType::kZset);
  EXPECT_EQ(redis->Zcard(kKey, kForceMasterCc).Get(), 2u);
  EXPECT_EQ(redis->Zadd(kKey, {}, kDefaultCc).Get(), 0u);
  EXPECT_EQ(redis
                ->Zadd(kKey, {{kScore2, kMember1}, {kScore1, kMember2}},
                       ZaddOptions::Exist::kAddIfNotExist, kDefaultCc)
                .Get(),
            0u);
  EXPECT_EQ(redis
                ->Zadd(kKey, {{kScore2, kMember1}, {kScore1, kMember2}},
                       ZaddOptions::Exist::kAddIfExist, kDefaultCc)
                .Get(),
            0u);
  EXPECT_EQ(redis
                ->Zadd(kKey, {{kScore2, kMember2}, {kScore1, kMember1}},
                       ZaddOptions::ReturnValue::kChangedCount, kDefaultCc)
                .Get(),
            2u);

  {
    std::vector<storages::redis::MemberScore> expected{{kMember2, kScore2},
                                                       {kMember1, kScore1}};
    auto result = [&]() {
      EXPECT_NOTHROW(
          return redis
              ->ZrangebyscoreWithScores(kKey, "-inf", "+inf", kForceMasterCc)
              .Get());
    }();
    EXPECT_EQ(result.size(), expected.size());
    for (size_t idx = 0; idx < result.size(); idx++) {
      EXPECT_EQ(result.at(idx).member, expected.at(idx).member);
      EXPECT_EQ(result.at(idx).score, expected.at(idx).score, kEps);
    }
  }

  EXPECT_EQ(redis->Zcard(kKey, kForceMasterCc).Get(), 2u);

  EXPECT_EQ(
      redis
          ->Zrem(kKey, std::vector<std::string>{kMember1, kMember2}, kDefaultCc)
          .Get(),
      2u);
  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
}

void TestList(const storages::redis::ClientPtr& redis) {
  static const std::string kKey = "test_list_key";
  static const std::string kElem0 = "elem0";
  static const std::string kElem1 = "elem1";
  static const std::string kElem2 = "elem2";

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());

  EXPECT_EQ(redis->Lindex(kKey, 0, kForceMasterCc).Get(),
            std::optional<std::string>{});
  EXPECT_EQ(redis->Lindex(kKey, 1, kForceMasterCc).Get(),
            std::optional<std::string>{});
  EXPECT_EQ(redis->Lindex(kKey, -1, kForceMasterCc).Get(),
            std::optional<std::string>{});
  EXPECT_EQ(redis->Llen(kKey, kForceMasterCc).Get(), 0u);
  EXPECT_EQ(redis->Lpop(kKey, kDefaultCc).Get(), std::optional<std::string>{});
  EXPECT_EQ(redis->Rpop(kKey, kDefaultCc).Get(), std::optional<std::string>{});

  EXPECT_EQ(redis->Lpush(kKey, kElem1, kDefaultCc).Get(), 1u);
  EXPECT_EQ(redis->Lpush(kKey, kElem0, kDefaultCc).Get(), 2u);
  EXPECT_EQ(redis->Rpush(kKey, kElem2, kDefaultCc).Get(), 3u);

  EXPECT_EQ(redis->Lindex(kKey, 0, kForceMasterCc).Get(), kElem0);
  EXPECT_EQ(redis->Lindex(kKey, 1, kForceMasterCc).Get(), kElem1);
  EXPECT_EQ(redis->Lindex(kKey, -1, kForceMasterCc).Get(), kElem2);
  EXPECT_EQ(redis->Lindex(kKey, -3, kForceMasterCc).Get(), kElem0);

  EXPECT_EQ(redis->Lpush(kKey, std::vector<std::string>{}, kDefaultCc).Get(),
            3u);
  EXPECT_EQ(redis->Rpush(kKey, std::vector<std::string>{}, kDefaultCc).Get(),
            3u);

  EXPECT_EQ(redis->Lrange(kKey, 0, -1, kForceMasterCc).Get(),
            {kElem0, kElem1, kElem2});
  EXPECT_EQ(redis->Lrange(kKey, 1, 2, kForceMasterCc).Get(), {kElem1, kElem2});
  EXPECT_EQ(redis->Lrange(kKey, -3, -2, kForceMasterCc).Get(),
            {kElem0, kElem1});

  EXPECT_NOTHROW(redis->Ltrim(kKey, 1, -1, kDefaultCc).Get());
  EXPECT_EQ(redis->Lpop(kKey, kDefaultCc).Get(), kElem1);
  EXPECT_EQ(redis->Lpop(kKey, kDefaultCc).Get(), kElem2);

  EXPECT_EQ(redis->Lpush(kKey, kElem2, kDefaultCc).Get(), 1u);
  EXPECT_EQ(
      redis->Lpush(kKey, std::vector<std::string>{kElem1, kElem0}, kDefaultCc)
          .Get(),
      3u);
  EXPECT_EQ(redis->Rpop(kKey, kDefaultCc).Get(), kElem2);
  EXPECT_EQ(redis->Rpop(kKey, kDefaultCc).Get(), kElem1);
  EXPECT_EQ(
      redis->Rpush(kKey, std::vector<std::string>{kElem1, kElem2}, kDefaultCc)
          .Get(),
      3u);

  EXPECT_EQ(redis->Llen(kKey, kForceMasterCc).Get(), 3u);
  EXPECT_EQ(redis->Lrange(kKey, 0, -1, kForceMasterCc).Get(),
            {kElem0, kElem1, kElem2});
  EXPECT_EQ(redis->Lindex(kKey, 3, kForceMasterCc).Get(),
            std::optional<std::string>{});
  EXPECT_EQ(redis->Lindex(kKey, -4, kForceMasterCc).Get(),
            std::optional<std::string>{});

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
}

void TestRename(const storages::redis::ClientPtr& redis) {
  static const std::string kValue = "value";
  static const std::string kKey = "rename_key";
  static const std::string kNewKey = "rename_new_key";

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());

  EXPECT_NOTHROW(redis->Set(kKey, kValue, kDefaultCc).Get());
  EXPECT_EQ(redis->Get(kKey, kForceMasterCc).Get(), kValue);
  EXPECT_EQ(redis->Get(kNewKey, kForceMasterCc).Get(),
            std::optional<std::string>{});
  EXPECT_NOTHROW(redis->Rename(kKey, kNewKey, kDefaultCc).Get());
  EXPECT_EQ(redis->Get(kKey, kForceMasterCc).Get(),
            std::optional<std::string>{});
  EXPECT_EQ(redis->Get(kNewKey, kForceMasterCc).Get(), kValue);

  EXPECT_NOTHROW(redis->Del(kNewKey, kDefaultCc).Get());
}

void TestUnorderedSet(const storages::redis::ClientPtr& redis) {
  static const std::string kKey = "test_unordered_set_key";
  static const std::string kElem0 = "elem0";
  static const std::string kElem1 = "elem1";
  static const std::string kElem2 = "elem2";

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());

  EXPECT_EQ(redis->Scard(kKey, kForceMasterCc).Get(), 0u);
  EXPECT_EQ(redis->Smembers(kKey, kForceMasterCc).Get(),
            std::unordered_set<std::string>{});
  EXPECT_EQ(redis->Srandmember(kKey, kForceMasterCc).Get(),
            std::optional<std::string>{});
  EXPECT_EQ(redis->Srandmembers(kKey, 2, kForceMasterCc).Get(),
            std::vector<std::string>{});
  EXPECT_EQ(redis->Srandmembers(kKey, -2, kForceMasterCc).Get(),
            std::vector<std::string>{});
  EXPECT_EQ(redis->Srem(kKey, kElem0, kDefaultCc).Get(), 0u);
  EXPECT_EQ(redis
                ->Srem(kKey, std::vector<std::string>{kElem0, kElem1, kElem2},
                       kDefaultCc)
                .Get(),
            0u);

  EXPECT_EQ(redis->Sadd(kKey, kElem1, kDefaultCc).Get(), 1u);
  EXPECT_EQ(redis->Srandmember(kKey, kForceMasterCc).Get(), kElem1);

  EXPECT_EQ(redis
                ->Sadd(kKey, std::vector<std::string>{kElem0, kElem1, kElem2},
                       kDefaultCc)
                .Get(),
            2u);

  EXPECT_EQ(redis->Scard(kKey, kForceMasterCc).Get(), 3u);
  EXPECT_EQ(redis->Smembers(kKey, kForceMasterCc).Get(),
            std::unordered_set<std::string>{kElem0, kElem1, kElem2});
  EXPECT_EQ(redis->Srandmembers(kKey, 2, kForceMasterCc).Get().size(), 2u);
  EXPECT_EQ(redis->Srandmembers(kKey, -2, kForceMasterCc).Get().size(), 2u);
  EXPECT_EQ(redis->Srandmembers(kKey, 4, kForceMasterCc).Get().size(), 3u);
  EXPECT_EQ(redis->Srandmembers(kKey, -4, kForceMasterCc).Get().size(), 4u);
  EXPECT_EQ(redis->Srem(kKey, kElem0, kDefaultCc).Get(), 1u);
  EXPECT_EQ(redis
                ->Srem(kKey, std::vector<std::string>{kElem0, kElem1, kElem2},
                       kDefaultCc)
                .Get(),
            2u);

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
}

void TestScan(const storages::redis::ClientPtr& redis) {
  static const std::string kKeyPrefix = "key_test_scan_";
  static const char kFilterChar = '1';
  static const std::string kValue = "value";
  const size_t kKeyCount = 500;

  std::unordered_set<std::string> keys;
  for (size_t i = 0; i < kKeyCount; i++) {
    keys.insert(kKeyPrefix + std::to_string(i));
  }

  std::unordered_set<std::string> keys_1;
  for (const auto& key : keys) {
    if (key[kKeyPrefix.size()] == kFilterChar) keys_1.insert(key);
  }

  for (const auto& key : keys) {
    EXPECT_NOTHROW(redis->Set(key, kValue, kDefaultCc).Get());
  }

  EXPECT_EQ(
      [&]() {
        std::unordered_set<std::string> keys_read;
        auto scan_request = redis->Scan(0, kForceMasterCc);
        scan_request.SetRequestDescription("test SCAN command");
        for (auto& key : scan_request) keys_read.insert(std::move(key));
        return keys_read;
      }(),
      keys);

  EXPECT_EQ(
      [&]() {
        std::unordered_set<std::string> keys_read;
        auto scan_request = redis->Scan(
            0, storages::redis::ScanOptions::Match("no_keys_will_be_matched"),
            kForceMasterCc);
        for (auto& key : scan_request) keys_read.insert(std::move(key));
        return keys_read;
      }(),
      std::unordered_set<std::string>{});

  EXPECT_EQ(
      [&]() {
        std::unordered_set<std::string> keys_read;
        std::vector<std::string> keys_vector =
            redis->Scan(0, kForceMasterCc).GetAll();
        for (auto& key : keys_vector) keys_read.insert(std::move(key));
        return keys_read;
      }(),
      keys);

  EXPECT_EQ(redis->Scan(0, kForceMasterCc)
                .GetAll<std::unordered_set<std::string>>("test SCAN command"),
            keys);

  EXPECT_EQ(redis
                ->Scan(0,
                       {storages::redis::ScanOptions::Match(kKeyPrefix +
                                                            kFilterChar + '*'),
                        storages::redis::ScanOptions::Count(42)},
                       kForceMasterCc)
                .GetAll<std::unordered_set<std::string>>("test SCAN command"),
            keys_1);

  EXPECT_EQ(
      redis->Scan(0, storages::redis::ScanOptions::Match(""), kForceMasterCc)
          .GetAll(),
      std::vector<std::string>{});

  EXPECT_NOTHROW(redis->Set("", kValue, kDefaultCc).Get());

  EXPECT_EQ(
      redis->Scan(0, storages::redis::ScanOptions::Match(""), kForceMasterCc)
          .GetAll(),
      {{""}});

  EXPECT_NOTHROW(redis->Del("", kDefaultCc).Get());

  for (const auto& key : keys) {
    EXPECT_NOTHROW(redis->Del(key, kDefaultCc).Get());
  }
}

void TestSscan(const storages::redis::ClientPtr& redis) {
  static const std::string kKey = "key_test_sscan";
  static const std::string kMemberPrefix = "member_test_sscan_";
  static const char kFilterChar = '1';
  const size_t kMemberCount = 500;

  std::unordered_set<std::string> members;
  for (size_t i = 0; i < kMemberCount; i++) {
    members.insert(kMemberPrefix + std::to_string(i));
  }

  std::unordered_set<std::string> members_1;
  for (const auto& member : members) {
    if (member[kMemberPrefix.size()] == kFilterChar) members_1.insert(member);
  }

  for (const auto& member : members) {
    EXPECT_EQ(redis->Sadd(kKey, member, kDefaultCc).Get(), 1u);
  }

  EXPECT_EQ(
      [&]() {
        std::unordered_set<std::string> members_read;
        auto sscan_request = redis->Sscan(kKey, kForceMasterCc);
        sscan_request.SetRequestDescription("test SSCAN command");
        for (auto& member : sscan_request)
          members_read.insert(std::move(member));
        return members_read;
      }(),
      members);

  EXPECT_EQ(
      [&]() {
        std::unordered_set<std::string> members_read;
        auto sscan_request = redis->Sscan(
            kKey,
            storages::redis::SscanOptions::Match("no_members_will_be_matched"),
            kForceMasterCc);
        for (auto& member : sscan_request)
          members_read.insert(std::move(member));
        return members_read;
      }(),
      std::unordered_set<std::string>{});

  EXPECT_EQ(
      [&]() {
        std::unordered_set<std::string> members_read;
        std::vector<std::string> members_vector =
            redis->Sscan(kKey, kForceMasterCc).GetAll();
        for (auto& member : members_vector)
          members_read.insert(std::move(member));
        return members_read;
      }(),
      members);

  EXPECT_EQ(redis->Sscan(kKey, kForceMasterCc)
                .GetAll<std::unordered_set<std::string>>("test SSCAN command"),
            members);

  EXPECT_EQ(redis
                ->Sscan(kKey,
                        storages::redis::SscanOptions::Match(kMemberPrefix +
                                                             kFilterChar + '*'),
                        kForceMasterCc)
                .GetAll<std::unordered_set<std::string>>(
                    "test SSCAN command with MATCH filter"),
            members_1);

  EXPECT_EQ(redis
                ->Sscan(kKey, storages::redis::SscanOptions::Match(""),
                        kForceMasterCc)
                .GetAll(),
            std::vector<std::string>{});

  EXPECT_EQ(redis->Sadd(kKey, "", kDefaultCc).Get(), 1u);

  EXPECT_EQ(
      redis
          ->Sscan(kKey, storages::redis::ScanOptions::Match(""), kForceMasterCc)
          .GetAll(),
      {{""}});

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
}

void TestHscan(const storages::redis::ClientPtr& redis) {
  static const std::string kKey = "key_test_hscan";
  static const std::string kFieldPrefix = "field_test_hscan_";
  static const std::string kValuePrefix = "value_test_hscan_";
  static const char kFilterChar = '1';
  const size_t kFieldCount = 500;

  std::unordered_map<std::string, std::string> fields;
  for (size_t i = 0; i < kFieldCount; i++) {
    fields[kFieldPrefix + std::to_string(i)] = kValuePrefix + std::to_string(i);
  }

  std::unordered_map<std::string, std::string> fields_1;
  for (const auto& elem : fields) {
    if (elem.first[kFieldPrefix.size()] == kFilterChar) fields_1.emplace(elem);
  }

  for (const auto& elem : fields) {
    EXPECT_EQ(redis->Hset(kKey, elem.first, elem.second, kDefaultCc).Get(),
              storages::redis::HsetReply::kCreated);
  }

  EXPECT_EQ(
      [&]() {
        std::unordered_map<std::string, std::string> fields_read;
        auto hscan_request = redis->Hscan(kKey, kForceMasterCc);
        hscan_request.SetRequestDescription("test HSCAN command");
        for (auto& elem : hscan_request) fields_read.emplace(std::move(elem));
        return fields_read;
      }(),
      fields);

  EXPECT_EQ(
      [&]() {
        std::unordered_map<std::string, std::string> fields_read;
        auto hscan_request = redis->Hscan(
            kKey,
            storages::redis::HscanOptions::Match("no_fields_will_be_matched"),
            kForceMasterCc);
        for (auto& elem : hscan_request) fields_read.emplace(std::move(elem));
        return fields_read;
      }(),
      std::unordered_map<std::string, std::string>{});

  EXPECT_EQ(
      [&]() {
        std::unordered_map<std::string, std::string> fields_read;
        std::vector<std::pair<std::string, std::string>> elem_vector =
            redis->Hscan(kKey, kForceMasterCc).GetAll();
        for (auto& elem : elem_vector) fields_read.emplace(std::move(elem));
        return fields_read;
      }(),
      fields);

  EXPECT_EQ(redis->Hscan(kKey, kForceMasterCc)
                .GetAll<std::unordered_map<std::string, std::string>>(
                    "test HSCAN command"),
            fields);

  EXPECT_EQ(redis
                ->Hscan(kKey,
                        storages::redis::HscanOptions::Match(kFieldPrefix +
                                                             kFilterChar + '*'),
                        kForceMasterCc)
                .GetAll<std::unordered_map<std::string, std::string>>(
                    "test HSCAN command with MATCH filter"),
            fields_1);

  EXPECT_EQ(redis
                ->Hscan(kKey, storages::redis::HscanOptions::Match(""),
                        kForceMasterCc)
                .GetAll(),
            std::vector<std::pair<std::string, std::string>>{});

  EXPECT_EQ(redis->Hset(kKey, "", kValuePrefix, kDefaultCc).Get(),
            storages::redis::HsetReply::kCreated);

  EXPECT_EQ(
      redis
          ->Hscan(kKey, storages::redis::ScanOptions::Match(""), kForceMasterCc)
          .GetAll(),
      {{"", kValuePrefix}});

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
}

void TestZscan(const storages::redis::ClientPtr& redis) {
  static const std::string kKey = "key_test_zscan";
  static const std::string kMemberPrefix = "member_test_zscan_";
  static const char kFilterChar = '1';
  const size_t kMemberCount = 500;

  std::unordered_map<std::string, double> members;
  for (size_t i = 0; i < kMemberCount; i++) {
    members[kMemberPrefix + std::to_string(i)] = i * 0.25;
  }

  std::unordered_map<std::string, double> members_1;
  for (const auto& elem : members) {
    if (elem.first[kMemberPrefix.size()] == kFilterChar)
      members_1.emplace(elem);
  }

  for (const auto& elem : members) {
    EXPECT_EQ(redis->Zadd(kKey, elem.second, elem.first, kDefaultCc).Get(), 1u);
  }

  EXPECT_EQ(
      [&]() {
        std::unordered_map<std::string, double> members_read;
        auto zscan_request = redis->Zscan(kKey, kForceMasterCc);
        zscan_request.SetRequestDescription("test ZSCAN command");
        for (auto& elem : zscan_request)
          members_read.emplace(std::move(elem.member), elem.score);
        return members_read;
      }(),
      members);

  EXPECT_EQ(
      [&]() {
        std::unordered_map<std::string, double> members_read;
        auto zscan_request = redis->Zscan(
            kKey,
            storages::redis::ZscanOptions::Match("no_members_will_be_matched"),
            kForceMasterCc);
        for (auto& elem : zscan_request)
          members_read.emplace(std::move(elem.member), elem.score);
        return members_read;
      }(),
      std::unordered_map<std::string, double>{});

  EXPECT_EQ(
      [&]() {
        std::unordered_map<std::string, double> members_read;
        std::vector<storages::redis::MemberScore> elem_vector =
            redis->Zscan(kKey, kForceMasterCc).GetAll();
        for (auto& elem : elem_vector)
          members_read.emplace(std::move(elem.member), elem.score);
        return members_read;
      }(),
      members);

  EXPECT_EQ(redis->Zscan(kKey, kForceMasterCc)
                .GetAll<std::unordered_map<std::string, double>>(
                    "test ZSCAN command"),
            members);

  EXPECT_EQ(redis
                ->Zscan(kKey,
                        storages::redis::ZscanOptions::Match(kMemberPrefix +
                                                             kFilterChar + '*'),
                        kForceMasterCc)
                .GetAll<std::unordered_map<std::string, double>>(
                    "test ZSCAN command with MATCH filter"),
            members_1);

  EXPECT_EQ(redis
                ->Zscan(kKey, storages::redis::ZscanOptions::Match(""),
                        kForceMasterCc)
                .GetAll(),
            std::vector<storages::redis::MemberScore>{});

  EXPECT_EQ(redis->Zadd(kKey, -1.0, "", kDefaultCc).Get(), 1u);

  EXPECT_EQ(
      redis
          ->Zscan(kKey, storages::redis::ScanOptions::Match(""), kForceMasterCc)
          .GetAll(),
      {{"", -1.0}});

  EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
}

void TestTransaction(const storages::redis::ClientPtr& redis) {
  static const std::string kKey1 = "transaction_test_key1";
  static const std::string kKey2 = "transaction_test_key2";
  static const std::string kValue1 = "transaction_test_value_1";
  static const std::string kValue2 = "transaction_test_value_2";

  auto transaction = redis->Multi();
  auto req_set1 = transaction->Set(kKey1, kValue1);
  auto req_get1 = transaction->Get(kKey1);
  auto req_get2 = transaction->Get(kKey2);
  auto req_set2 = transaction->Set(kKey2, kValue2);
  auto req_get3 = transaction->Get(kKey2);
  auto req_getset1 = transaction->Getset(kKey2, kValue1);
  auto req_getset2 = transaction->Getset(kKey2, kValue2);

  auto request = transaction->Exec(kDefaultCc);

  // entire transaction
  EXPECT_NOTHROW(request.Get("test transaction"));

  // subcommands
  EXPECT_NOTHROW(req_set1.Get());
  EXPECT_EQ(req_get1.Get(), kValue1);
  EXPECT_EQ(req_get2.Get(), std::optional<std::string>{});
  EXPECT_NOTHROW(req_set2.Get());
  EXPECT_EQ(req_get3.Get(), kValue2);
  EXPECT_EQ(req_getset1.Get(), kValue2);
  EXPECT_EQ(req_getset2.Get(), kValue1);

  EXPECT_EQ(
      redis->Del(std::vector<std::string>{kKey1, kKey2}, kDefaultCc).Get(), 2u);
}

void TestTransactionNotStarted(const storages::redis::ClientPtr& redis) {
  static const std::string kKey1 = "transaction_test_key1";
  static const std::string kKey2 = "transaction_test_key2";

  auto transaction = redis->Multi();
  auto req1_key2 = transaction->Get(kKey2);
  auto req2_key1 = transaction->Get(kKey1);
  auto req3_key2 = transaction->Get(kKey2);
  auto req4_key1 = transaction->Get(kKey1);

  EXPECT_THROW(req1_key2.Wait(),
               storages::redis::NotStartedTransactionException);
  EXPECT_THROW(req2_key1.Get(),
               storages::redis::NotStartedTransactionException);

  auto request = transaction->Exec(kDefaultCc);

  EXPECT_THROW(req3_key2.Get(),
               storages::redis::NotStartedTransactionException);
  EXPECT_THROW(req4_key1.Wait(),
               storages::redis::NotStartedTransactionException);

  EXPECT_NOTHROW(request.Get());
}

void TestForceShardIdx(const storages::redis::ClientPtr& redis) {
  static const std::string kKey = "force_shard_idx_test_key";
  static const std::string kValue = "force_shard_idx_test_value";

  {
    storages::redis::CommandControl cc;
    cc.force_shard_idx = 0;
    EXPECT_NOTHROW(redis->Set(kKey, kValue, cc).Get());
    EXPECT_EQ(redis->Get(kKey, cc).Get(), kValue);

    EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
  }

  {
    storages::redis::CommandControl cc;
    cc.force_shard_idx = 99;
    EXPECT_THROW([[maybe_unused]] auto request = redis->Set(kKey, kValue, cc),
                 redis::InvalidArgumentException);
    EXPECT_THROW([[maybe_unused]] auto request = redis->Get(kKey, cc),
                 redis::InvalidArgumentException);

    EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
  }

  {
    storages::redis::CommandControl cc;
    cc.force_shard_idx = 1;
    EXPECT_THROW([[maybe_unused]] auto request = redis->Ping(0, cc),
                 redis::InvalidArgumentException);
    cc.force_shard_idx = 0;
    EXPECT_THROW([[maybe_unused]] auto request = redis->Ping(1, cc),
                 redis::InvalidArgumentException);
  }

  {
    auto transaction = redis->Multi();
    auto req_set = transaction->Set(kKey, kValue);
    auto req_get = transaction->Get(kKey);
    storages::redis::CommandControl cc;
    cc.force_shard_idx = 0;
    auto request = transaction->Exec(cc);

    // entire transaction
    EXPECT_NOTHROW(request.Get("test transaction"));
    // subcommands
    EXPECT_NOTHROW(req_set.Get());
    EXPECT_EQ(req_get.Get(), kValue);

    EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
  }

  {
    auto transaction = redis->Multi();
    auto req_set = transaction->Set(kKey, kValue);
    auto req_get = transaction->Get(kKey);
    storages::redis::CommandControl cc;
    cc.force_shard_idx = 99;

    EXPECT_THROW([[maybe_unused]] auto request = transaction->Exec(cc),
                 redis::InvalidArgumentException);

    EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
  }
}

void TestGetClientForShard(const storages::redis::ClientPtr& redis) {
  static const std::string kKey = "get_client_for_shard_test_key";
  static const std::string kValue = "get_client_for_shard_test_value";

  {
    auto client = redis->GetClientForShard(0);
    EXPECT_NOTHROW(client->Set(kKey, kValue, kDefaultCc).Get());
    EXPECT_EQ(client->Get(kKey, kDefaultCc).Get(), kValue);

    EXPECT_NOTHROW(client->Del(kKey, kDefaultCc).Get());
  }

  {
    auto client = redis->GetClientForShard(99);
    EXPECT_THROW(
        [[maybe_unused]] auto request = client->Set(kKey, kValue, kDefaultCc),
        redis::InvalidArgumentException);
    EXPECT_THROW([[maybe_unused]] auto request = client->Get(kKey, kDefaultCc),
                 redis::InvalidArgumentException);

    EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
  }

  {
    auto client1 = redis->GetClientForShard(1);
    EXPECT_THROW([[maybe_unused]] auto request = client1->Ping(0, kDefaultCc),
                 redis::InvalidArgumentException);
  }
  {
    auto client0 = redis->GetClientForShard(0);
    EXPECT_THROW([[maybe_unused]] auto request = client0->Ping(1, kDefaultCc),
                 redis::InvalidArgumentException);
  }

  {
    auto client = redis->GetClientForShard(0);
    auto transaction = client->Multi();
    auto req_set = transaction->Set(kKey, kValue);
    auto req_get = transaction->Get(kKey);
    auto request = transaction->Exec(kDefaultCc);

    // entire transaction
    EXPECT_NOTHROW(request.Get("test transaction"));
    // subcommands
    EXPECT_NOTHROW(req_set.Get());
    EXPECT_EQ(req_get.Get(), kValue);

    EXPECT_NOTHROW(client->Del(kKey, kDefaultCc).Get());
  }

  {
    auto client = redis->GetClientForShard(99);
    auto transaction = client->Multi();
    auto req_set = transaction->Set(kKey, kValue);
    auto req_get = transaction->Get(kKey);

    EXPECT_THROW([[maybe_unused]] auto request = transaction->Exec(kDefaultCc),
                 redis::InvalidArgumentException);

    EXPECT_NOTHROW(redis->Del(kKey, kDefaultCc).Get());
  }
}

}  // namespace

namespace samples {
namespace handlers {

RedisTestCommands::RedisTestCommands(
    const components::ComponentConfig& config,
    const components::ComponentContext& context)
    : server::handlers::HttpHandlerBase(config, context) {
  auto& redis_component = context.FindComponent<components::Redis>();
  redis_ptr_ = redis_component.GetClient(kRedisClientName);
}

const std::string& RedisTestCommands::HandlerName() const {
  static const std::string kHandlerName = kName;
  return kHandlerName;
}

std::string RedisTestCommands::HandleRequestThrow(
    const server::http::HttpRequest&, server::request::RequestContext&) const {
  TestPing(redis_ptr_);
  TestDbsize(redis_ptr_);
  TestGetSetAppend(redis_ptr_);
  TestIncr(redis_ptr_);
  TestHgetHsetHdel(redis_ptr_);
  TestHincrby(redis_ptr_);
  TestTtl(redis_ptr_);
  TestSortedSet(redis_ptr_);
  TestSortedSetVector(redis_ptr_);
  TestList(redis_ptr_);
  TestRename(redis_ptr_);
  TestUnorderedSet(redis_ptr_);
  TestScan(redis_ptr_);
  TestSscan(redis_ptr_);
  TestHscan(redis_ptr_);
  TestZscan(redis_ptr_);

  TestTransaction(redis_ptr_);
  TestTransactionNotStarted(redis_ptr_);

  // *Shard* tests check functionality partly because testsuite support only
  // 1-shard redis server.
  TestForceShardIdx(redis_ptr_);
  TestGetClientForShard(redis_ptr_);

  return {};
}

}  // namespace handlers
}  // namespace samples
