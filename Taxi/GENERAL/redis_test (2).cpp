#include <userver/utest/utest.hpp>

#include <fmt/format.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <initializer_list>
#include <iterator>
#include <list>
#include <memory>
#include <mutex>
#include <numeric>
#include <optional>
#include <random>
#include <string>
#include <tuple>
#include <type_traits>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <variant>
#include <vector>

#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/engine/mutex.hpp>
#include <userver/formats/json/string_builder.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/storages/redis/client.hpp>
#include <userver/storages/redis/command_options.hpp>
#include <userver/storages/redis/mock_client_base.hpp>
#include <userver/storages/redis/mock_transaction.hpp>
#include <userver/utils/assert.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/log.hpp>
#include <userver/utils/mock_now.hpp>
#include <userver/utils/overloaded.hpp>
#include <userver/utils/statistics/metrics_storage.hpp>
#include <userver/utils/strong_typedef.hpp>

#include <helpers/redis.hpp>
#include <helpers/redis_metrics.hpp>
#include <helpers/types.hpp>

#include <taxi_config/variables/GROCERY_COLD_STORAGE_REDIS_CACHE_TTL.hpp>
#include <taxi_config/variables/GROCERY_COLD_STORAGE_REDIS_COMMAND_CONTROL.hpp>

namespace helpers = grocery_cold_storage::helpers;

using helpers::ItemIds;
using helpers::ItemList;

namespace {

using namespace std::chrono_literals;

const std::string kTestScope = "test_scope";

const std::string kKey0 = "item_id0";
const std::string kKey1 = "item_id1";
const std::string kValue0 = "value0";
const std::string kValue1a = "value1a";
const std::string kValue1b = "value1b";

using StringSet = std::unordered_set<std::string>;
using Value = std::variant<std::string, StringSet>;
struct ValueTag;  // underlying type is tagged for PrintTo(Context::Storage) and
                  // operator<(TaggedValue) to be discoverable by ADL in gtest's
                  // assertion macros
using TaggedValue =
    utils::StrongTypedef<ValueTag, Value, utils::StrongTypedefOps::kNoCompare>;

enum class ClientOp {
  Mget,
};

enum class TransactionOp {
  Set,
  Sadd,
  Pexpire,
  Smembers,
};

std::string ToString(ClientOp op) {
  switch (op) {
    case ClientOp::Mget: {
      return "client_mget";
    }
  }
  UINVARIANT(false, "unreachable");
}

std::string ToString(TransactionOp op) {
  switch (op) {
    case TransactionOp::Set: {
      return "transaction_set";
    }
    case TransactionOp::Sadd: {
      return "transaction_sadd";
    }
    case TransactionOp::Pexpire: {
      return "transaction_pexpire";
    }
    case TransactionOp::Smembers: {
      return "transaction_smembers";
    }
  }
  UINVARIANT(false, "unreachable");
}

// actually both used in EXPECT_EQ for Context::Storage values ordering and
// pretty printing
bool operator<[[maybe_unused]](const TaggedValue& lhs, const TaggedValue& rhs);
bool operator==
    [[maybe_unused]](const TaggedValue& lhs, const TaggedValue& rhs);

template <typename C>
auto MakeOrderedView(const C& container) {
  using ElementType = typename C::value_type;
  std::vector<const ElementType*> ordered_view;
  ordered_view.reserve(container.size());
  for (auto& element : container) {
    ordered_view.push_back(&element);
  }
  std::sort(ordered_view.begin(), ordered_view.end(),
            [](auto* l, auto* r) { return *l < *r; });
  return ordered_view;
}

template <template <typename...> class Op>
bool Operator(const TaggedValue& lhs, const TaggedValue& rhs) {
  const auto& l = lhs.GetUnderlying();
  const auto& r = rhs.GetUnderlying();

  if (l.index() != r.index()) {
    return Op<std::size_t>{}(l.index(), r.index());
  }

  auto set_op = [](const StringSet& lhs, const StringSet& rhs) -> bool {
    if (lhs.size() != rhs.size()) {
      return Op<std::size_t>{}(lhs.size(), rhs.size());
    }
    auto l = MakeOrderedView(lhs);
    auto r = MakeOrderedView(rhs);
    return std::inner_product(l.cbegin(), l.cend(), r.cbegin(), true /* init */,
                              std::logical_and<bool>{}, [](auto* l, auto* r) {
                                return Op<std::string>{}(*l, *r);
                              });
  };

  auto heterogeneous_op = [](const auto&, const auto&) -> bool {
    UINVARIANT(false, "unreachable");
  };

  utils::Overloaded op{set_op, Op<std::string>{}, heterogeneous_op};
  return std::visit(op, l, r);
}

bool operator==(const TaggedValue& lhs, const TaggedValue& rhs) {
  return Operator<std::equal_to>(lhs, rhs);
}

bool operator<(const TaggedValue& lhs, const TaggedValue& rhs) {
  return Operator<std::less>(lhs, rhs);
}

using Op = std::variant<ClientOp, TransactionOp>;

using TtlType = std::optional<std::chrono::milliseconds>;
using TimestampType = std::optional<std::chrono::system_clock::time_point>;

using StringVector = std::vector<std::string>;
using LogKeys = std::variant<std::string, StringVector>;
using LogValues = std::variant<std::monostate, std::string, StringVector>;

using LogItem = std::tuple<Op, LogKeys, LogValues, TtlType>;

struct JsonBuilder {
  formats::json::StringBuilder& sb;

  template <typename... Ts>
  void operator()(const std::variant<Ts...>& value) const {
    std::visit(*this, value);
  }

  void operator()(std::monostate) const { sb.WriteNull(); }

  template <typename T>
  void operator()(const T& value) const {
    if constexpr (std::is_same_v<T, std::string>) {
      sb.WriteString(value);
    } else if constexpr (std::is_same_v<T, ClientOp> ||
                         std::is_same_v<T, TransactionOp>) {
      sb.WriteString(ToString(value));
    } else {
      static_assert(!sizeof(T), "Type is not yet handled");
    }
  }

  template <class Tag, class T, utils::StrongTypedefOps Ops>
  void operator()(const utils::StrongTypedef<Tag, T, Ops>& value) const {
    operator()(value.GetUnderlying());
  }

  template <typename T>
  void operator()(const std::optional<T>& value) const {
    if (!value) {
      sb.WriteNull();
      return;
    }
    operator()(*value);
  }

  template <typename T>
  void operator()(T* value) const {
    if (!value) {
      sb.WriteNull();
      return;
    }
    operator()(*value);
  }

  template <typename T>
  void operator()(const std::vector<T>& values) const {
    formats::json::StringBuilder::ArrayGuard array{sb};
    for (const auto& value : values) {
      operator()(value);
    }
  }

  template <typename T>
  void operator()(const std::unordered_set<T>& values) const {
    operator()(MakeOrderedView(values));
  }

  void operator()(std::chrono::milliseconds value) const {
    sb.WriteString(fmt::format("{}ms", value.count()));
  }

  void operator()(std::chrono::system_clock::time_point value) const {
    sb.WriteString(utils::datetime::Timestring(value));
  }

  void operator()(const LogItem& value) const {
    formats::json::StringBuilder::ObjectGuard object{sb};

    const auto& [op, keys, values, ttl] = value;

    sb.Key("op");
    operator()(op);

    sb.Key("keys");
    operator()(keys);

    sb.Key("values");
    operator()(values);

    sb.Key("ttl");
    operator()(ttl);
  }

  template <typename T>
  void operator()(const std::unordered_map<std::string, T>& values) const {
    formats::json::StringBuilder::ObjectGuard object{sb};
    for (auto* element : MakeOrderedView(values)) {
      const auto& [key, value] = *element;
      sb.Key(key);
      operator()(value);
    }
  }

  template <typename... Types>
  void operator()(const std::tuple<Types...>& tuple) const {
    VisitTuple(tuple, std::index_sequence_for<Types...>{});
  }

  template <typename... Types, std::size_t... Indices>
  void VisitTuple(const std::tuple<Types...>& tuple,
                  std::index_sequence<Indices...>) const {
    formats::json::StringBuilder::ArrayGuard array{sb};
    (operator()(std::get<Indices>(tuple)), ...);
  }
};

struct Context {
  using StorageValue = std::tuple<TaggedValue, TimestampType>;
  using Storage = std::unordered_map<std::string /* key */, StorageValue>;

  mutable engine::Mutex mutex;
  std::vector<LogItem> log;  // TODO(luxaeterna): replace log with gmock
  Storage redis;

  [[nodiscard]] auto MakeLockGuard() const {
    return std::lock_guard<engine::Mutex>{mutex};
  }

  void Reset() {
    log.clear();
    redis.clear();
  }
};

// actually used in EXPECT_EQ for pretty printing
void PrintTo
    [[maybe_unused]] (const std::vector<LogItem>& log, std::ostream* os) {
  formats::json::StringBuilder sb;
  JsonBuilder{sb}(log);
  *os << sb.GetString();
}

// actually used in EXPECT_EQ for pretty printing
void PrintTo
    [[maybe_unused]] (const Context::Storage& storage, std::ostream* os) {
  formats::json::StringBuilder sb;
  JsonBuilder{sb}(storage);
  *os << sb.GetString();
}

class TransactionMock : public storages::redis::MockTransactionImplBase {
 public:
  TransactionMock(Context& context) : context_{context} {}

  storages::redis::RequestSet Set(std::string key, std::string value,
                                  std::chrono::milliseconds ttl) override {
    auto lock = context_.MakeLockGuard();
    context_.log.emplace_back(TransactionOp::Set, key, value, ttl);

    context_.redis.insert_or_assign(
        std::move(key), std::forward_as_tuple(TaggedValue{std::move(value)},
                                              utils::datetime::Now() + ttl));
    return storages::redis::CreateMockRequest<storages::redis::RequestSet>();
  }

  storages::redis::RequestSadd Sadd(std::string key,
                                    std::vector<std::string> members) override {
    auto lock = context_.MakeLockGuard();
    context_.log.emplace_back(TransactionOp::Sadd, key, members, TtlType{});

    auto& value = std::get<0>(context_.redis[std::move(key)]).GetUnderlying();
    auto set = std::get_if<StringSet>(&value);
    if (!set) {
      set = &value.emplace<StringSet>();
    }
    set->insert(std::make_move_iterator(members.begin()),
                std::make_move_iterator(members.end()));

    return storages::redis::CreateMockRequest<storages::redis::RequestSadd>(
        set->size());
  }

  storages::redis::RequestPexpire Pexpire(
      std::string key, std::chrono::milliseconds ttl) override {
    auto lock = context_.MakeLockGuard();
    context_.log.emplace_back(TransactionOp::Pexpire, key, LogValues{}, ttl);

    std::int64_t result = 0;
    auto it = context_.redis.find(key);
    if (it != context_.redis.end()) {
      result = 1;
      std::get<1>(it->second) = utils::datetime::Now() + ttl;
    }
    storages::redis::ExpireReply reply{result};
    return storages::redis::CreateMockRequest<storages::redis::RequestPexpire>(
        std::move(reply));
  }

  storages::redis::RequestSmembers Smembers(std::string key) override {
    auto lock = context_.MakeLockGuard();
    context_.log.emplace_back(TransactionOp::Smembers, key, LogValues{},
                              TtlType{});

    storages::redis::RequestSmembers::Reply reply;
    auto it = context_.redis.find(key);
    if (it != context_.redis.end()) {
      const auto& value = std::get<0>(it->second).GetUnderlying();
      UASSERT(std::holds_alternative<StringSet>(value));
      reply = std::get<StringSet>(value);
    }
    return storages::redis::CreateMockRequest<storages::redis::RequestSmembers>(
        std::move(reply));
  }

 private:
  Context& context_;
};

class TransactionMockCreator
    : public storages::redis::MockClientBase::MockTransactionImplCreatorBase {
 public:
  TransactionMockCreator(Context& context) : context_{context} {}

  std::unique_ptr<storages::redis::MockTransactionImplBase> operator()()
      const override {
    return std::make_unique<TransactionMock>(context_);
  }

 private:
  Context& context_;
};

class ClientMock : public storages::redis::MockClientBase {
 public:
  ClientMock(Context& context) : context_{context} {
    SetMockTransactionImplCreator(
        std::make_shared<TransactionMockCreator>(context_));
  }

  storages::redis::RequestMget Mget(
      std::vector<std::string> keys,
      const storages::redis::CommandControl& command_control) override {
    static_cast<void>(command_control);

    auto lock = context_.MakeLockGuard();
    context_.log.emplace_back(ClientOp::Mget, keys, LogValues{}, TtlType{});

    storages::redis::RequestMget::Reply reply;
    for (const auto& key : keys) {
      auto it = context_.redis.find(key);
      if (it == context_.redis.end()) {
        reply.emplace_back();
        continue;
      }
      const auto& value = std::get<0>(it->second).GetUnderlying();
      if (!std::holds_alternative<std::string>(value)) {
        reply.emplace_back();
        continue;
      }
      reply.emplace_back(std::get<std::string>(value));
    }
    return storages::redis::CreateMockRequest<storages::redis::RequestMget>(
        std::move(reply));
  }

 private:
  Context& context_;
};

[[nodiscard]] auto MakeConfigStorage(std::chrono::seconds ttl) {
  using taxi_config::grocery_cold_storage_redis_command_control::TimeoutInfo;

  TimeoutInfo timeout_info;
  timeout_info.timeout_single_ms = 1s;
  timeout_info.timeout_all_ms = 3s;
  timeout_info.max_retries = 1;

  dynamic_config::StorageMock config_storage{{
      {taxi_config::GROCERY_COLD_STORAGE_REDIS_CACHE_TTL,
       {{dynamic_config::kValueDictDefaultName, ttl}}},
      {taxi_config::GROCERY_COLD_STORAGE_REDIS_COMMAND_CONTROL,
       {{dynamic_config::kValueDictDefaultName, timeout_info}}},
  }};

  return config_storage;
}

class Fixture : public ::testing::Test {
 protected:
  struct ExpectedMetrics {
    using Percentiles =
        std::array<std::size_t,
                   helpers::redis::kDefaultMetricPercentiles.size()>;

    std::int64_t puts = 0;
    std::int64_t gets = 0;

    std::int64_t put_key_counts = 0;
    std::int64_t get_key_counts = 0;

    Percentiles bulk_store_size = {};
    std::uint32_t bulk_store_size_count = 0;
    Percentiles bulk_load_size = {};
    std::uint32_t bulk_load_size_count = 0;

    Percentiles store_key_size = {};
    std::uint32_t store_key_size_count = 0;
    Percentiles store_value_size = {};
    std::uint32_t store_value_size_count = {};

    std::int64_t hits = 0;
    std::int64_t misses = 0;
  };

  std::chrono::system_clock::time_point now = utils::datetime::Now();
  std::chrono::seconds ttl = 3s;

  dynamic_config::StorageMock config_storage = MakeConfigStorage(ttl);
  dynamic_config::Snapshot config = config_storage.GetSnapshot();

  Context context;
  std::shared_ptr<storages::redis::MockClientBase> redis_client =
      std::make_shared<ClientMock>(context);

  utils::statistics::MetricsStorage metrics_storage;

  Fixture() { utils::datetime::MockNowSet(now); }

  void CheckMetrics(const ExpectedMetrics& expected_metrics,
                    int epochs_ago = 0) {
    auto get_counter = [this](const auto& metric) {
      return metrics_storage.GetMetric(metric)
          .GetCounter(kTestScope)
          .counter.Load();
    };
    auto get_pecentiles = [this, epochs_ago](const auto& metric) {
      const auto& counter = metrics_storage.GetMetric(metric)
                                .GetCounter(kTestScope)
                                .counter.GetPreviousCounter(epochs_ago);
      ExpectedMetrics::Percentiles percentiles = {};
      auto p = helpers::redis::kDefaultMetricPercentiles.begin();
      for (auto& percentile : percentiles) {
        percentile = counter.GetPercentile(*p++);
      }
      return std::make_pair(percentiles, counter.Count());
    };

    EXPECT_EQ(get_counter(helpers::redis::kRedisCachePuts),
              expected_metrics.puts);
    EXPECT_EQ(get_counter(helpers::redis::kRedisCacheGets),
              expected_metrics.gets);

    EXPECT_EQ(get_counter(helpers::redis::kRedisCachePutKeyCounts),
              expected_metrics.put_key_counts);
    EXPECT_EQ(get_counter(helpers::redis::kRedisCacheGetKeyCounts),
              expected_metrics.get_key_counts);

    EXPECT_EQ(get_pecentiles(helpers::redis::kRedisCacheBulkStoreSize),
              std::make_pair(expected_metrics.bulk_store_size,
                             expected_metrics.bulk_store_size_count));
    EXPECT_EQ(get_pecentiles(helpers::redis::kRedisCacheBulkLoadSize),
              std::make_pair(expected_metrics.bulk_load_size,
                             expected_metrics.bulk_load_size_count));

    EXPECT_EQ(get_pecentiles(helpers::redis::kRedisCacheStoreKeySize),
              std::make_pair(expected_metrics.store_key_size,
                             expected_metrics.store_key_size_count));
    EXPECT_EQ(get_pecentiles(helpers::redis::kRedisCacheStoreValueSize),
              std::make_pair(expected_metrics.store_value_size,
                             expected_metrics.store_value_size_count));

    EXPECT_EQ(get_counter(helpers::redis::kRedisCacheHits),
              expected_metrics.hits);
    EXPECT_EQ(get_counter(helpers::redis::kRedisCacheMisses),
              expected_metrics.misses);
  }

  void ResetMetrics() { metrics_storage.ResetMetrics(); }
};

formats::json::Value MakeTestValue(std::string_view value) {
  formats::json::ValueBuilder json{formats::common::Type::kObject};
  json.EmplaceNocheck("value", value);
  return json.ExtractValue();
}

}  // namespace

namespace handlers {

// actually used in EXPECT_EQ for pretty printing
static void PrintTo [[maybe_unused]] (const Item& item, std::ostream* os) {
  UASSERT(item.extra.IsObject());
  formats::json::ValueBuilder json{item.extra};
  UASSERT(!json.HasMember("item_id"));
  json.EmplaceNocheck("item_id", item.item_id);
  *os << helpers::redis::ToJson(json.ExtractValue());
}

}  // namespace handlers

UTEST(RedisUtil, ToJson) {
  const auto expected_json =
      R"json({"key1":"value1","key2":"value2","key3":"value3","key4":"value4","key5":"value5"})json";

  std::array<std::pair<std::string, std::string>, 5> kv{{
      {"key1", "value1"},
      {"key2", "value2"},
      {"key3", "value3"},
      {"key4", "value4"},
      {"key5", "value5"},
  }};

  formats::json::ValueBuilder forward{formats::common::Type::kObject};
  UASSERT(std::is_sorted(kv.begin(), kv.end()));
  for (const auto& [k, v] : kv) {
    forward.EmplaceNocheck(k, v);
  }
  EXPECT_EQ(helpers::redis::ToJson(forward.ExtractValue()), expected_json);

  formats::json::ValueBuilder reverse{formats::common::Type::kObject};
  std::sort(kv.rbegin(), kv.rend());
  for (const auto& [k, v] : kv) {
    reverse.EmplaceNocheck(k, v);
  }
  EXPECT_EQ(helpers::redis::ToJson(reverse.ExtractValue()), expected_json);

  std::mt19937 g;
  std::vector<std::size_t> indices(kv.size());
  for (std::mt19937::result_type i = 0; i < 10; ++i) {
    g.seed(i);

    std::iota(indices.begin(), indices.end(), 0);
    std::shuffle(std::begin(indices), std::end(indices), g);

    formats::json::ValueBuilder vb{formats::common::Type::kObject};
    for (std::size_t index : indices) {
      const auto& [k, v] = kv[index];
      vb.EmplaceNocheck(k, v);
    }
    EXPECT_EQ(helpers::redis::ToJson(vb.ExtractValue()), expected_json);
  }
}

using Redis = Fixture;

UTEST_F_MT(Redis, Basic, 2) {
  auto value0 = MakeTestValue(kValue0);
  ItemList item_list_sent = {
      {kKey0, value0},
  };

  helpers::redis::StoreItems(kTestScope, item_list_sent, config, *redis_client,
                             metrics_storage);

  auto key0_serialized = helpers::redis::MakeKey(kTestScope, kKey0);
  auto value0_serialized = helpers::redis::ToJson(value0);

  Context::Storage expected_state = {
      {key0_serialized, {TaggedValue{value0_serialized}, now + ttl}},
  };
  EXPECT_EQ(context.redis, expected_state);

  std::vector<LogItem> expected_log = {
      {TransactionOp::Set, key0_serialized, value0_serialized, ttl},
  };
  EXPECT_EQ(context.log, expected_log);

  {
    ExpectedMetrics expected_metrics;
    expected_metrics.puts = 1;
    expected_metrics.put_key_counts = 1;
    expected_metrics.store_key_size.fill(key0_serialized.size());
    expected_metrics.store_key_size_count = 1;
    expected_metrics.store_value_size.fill(value0_serialized.size());
    expected_metrics.store_value_size_count = 1;
    CheckMetrics(expected_metrics);
  }
  ResetMetrics();

  ItemIds item_ids = {kKey0};

  auto item_list_received = helpers::redis::LoadItems(
      kTestScope, item_ids, config, *redis_client, metrics_storage);

  EXPECT_EQ(context.redis, expected_state);

  expected_log.push_back({ClientOp::Mget,
                          StringVector{key0_serialized},
                          {} /* value */,
                          {} /* ttl */});
  EXPECT_EQ(context.log, expected_log);

  EXPECT_EQ(item_list_received, item_list_sent);

  {
    ExpectedMetrics expected_metrics;
    expected_metrics.gets = 1;
    expected_metrics.get_key_counts = 1;
    expected_metrics.hits = 1;
    CheckMetrics(expected_metrics);
  }
  ResetMetrics();
}

UTEST_F_MT(Redis, BasicLists, 2) {
  auto value0 = MakeTestValue(kValue0);
  auto value1a = MakeTestValue(kValue1a);
  auto value1b = MakeTestValue(kValue1b);
  std::vector<ItemList> item_lists_sent = {
      {
          {kKey0, value0},
      },
      {{kKey1, value1a}, {kKey1, value1b}},
  };

  helpers::redis::StoreItemLists(kTestScope, item_lists_sent, config,
                                 *redis_client, metrics_storage);

  auto key0_serialized = helpers::redis::MakeKey(kTestScope, kKey0);
  auto key1_serialized = helpers::redis::MakeKey(kTestScope, kKey1);
  auto value0_serialized = helpers::redis::ToJson(value0);
  auto value1a_serialized = helpers::redis::ToJson(value1a);
  auto value1b_serialized = helpers::redis::ToJson(value1b);

  Context::Storage expected_state = {
      {key0_serialized, {TaggedValue{StringSet{value0_serialized}}, now + ttl}},
      {key1_serialized,
       {TaggedValue{StringSet{value1a_serialized, value1b_serialized}},
        now + ttl}},
  };
  EXPECT_EQ(context.redis, expected_state);

  std::vector<LogItem> expected_log = {
      {TransactionOp::Sadd,
       key0_serialized,
       StringVector{value0_serialized},
       {} /* ttl */},
      {TransactionOp::Pexpire, key0_serialized, {} /* values */, ttl},
      {TransactionOp::Sadd,
       key1_serialized,
       StringVector{value1a_serialized, value1b_serialized},
       {} /* ttl */},
      {TransactionOp::Pexpire, key1_serialized, {} /* values */, ttl},
  };
  EXPECT_EQ(context.log, expected_log);

  {
    ExpectedMetrics expected_metrics;
    expected_metrics.puts = 1;
    expected_metrics.put_key_counts = 2;
    expected_metrics.bulk_store_size.fill(2);
    expected_metrics.bulk_store_size_count = 2;
    expected_metrics.store_key_size.fill(key0_serialized.size());
    expected_metrics.store_key_size_count = 2;
    expected_metrics.store_value_size.fill(value1b_serialized.size());
    expected_metrics.store_value_size_count = 3;
    CheckMetrics(expected_metrics);
  }
  ResetMetrics();

  ItemIds item_ids = {kKey0, kKey1};

  auto item_lists_received = helpers::redis::LoadItemLists(
      kTestScope, item_ids, config, *redis_client, metrics_storage);

  EXPECT_EQ(context.redis, expected_state);

  expected_log.push_back(
      {TransactionOp::Smembers, key0_serialized, {} /* value */, {} /* ttl */});
  expected_log.push_back(
      {TransactionOp::Smembers, key1_serialized, {} /* value */, {} /* ttl */});
  EXPECT_EQ(context.log, expected_log);

  // generally individual values in each item_list are not deterministically
  // ordered after a roundtrip
  auto make_ordered = [](std::vector<ItemList> item_lists) {
    auto value_less = [](const handlers::Item& lhs, const handlers::Item& rhs) {
      UASSERT(lhs.item_id == rhs.item_id);
      return helpers::redis::ToJson(lhs.extra) <
             helpers::redis::ToJson(rhs.extra);
    };
    for (auto& item_list : item_lists) {
      std::sort(item_list.begin(), item_list.end(), value_less);
    }
    return item_lists;
  };
  EXPECT_EQ(make_ordered(item_lists_received), make_ordered(item_lists_sent));

  {
    ExpectedMetrics expected_metrics;
    expected_metrics.gets = 1;
    expected_metrics.get_key_counts = 2;
    expected_metrics.bulk_load_size.fill(2);
    expected_metrics.bulk_load_size_count = 2;
    expected_metrics.hits = 2;
    CheckMetrics(expected_metrics);
  }
  ResetMetrics();
}

UTEST_F_MT(Redis, EmptyList, 2) {
  ItemList item_list_sent;
  helpers::redis::StoreItems(kTestScope, item_list_sent, config, *redis_client,
                             metrics_storage);

  Context::Storage expected_state{};
  EXPECT_EQ(context.redis, expected_state);

  std::vector<LogItem> expected_log{};
  EXPECT_EQ(context.log, expected_log);

  {
    ExpectedMetrics expected_metrics;
    expected_metrics.puts = 1;
    expected_metrics.put_key_counts = 0;
    expected_metrics.store_key_size.fill(0);
    expected_metrics.store_key_size_count = 0;
    expected_metrics.store_value_size.fill(0);
    expected_metrics.store_value_size_count = 0;
    CheckMetrics(expected_metrics);
  }
  ResetMetrics();

  ItemIds item_ids = {kKey0};

  auto item_list_received = helpers::redis::LoadItems(
      kTestScope, item_ids, config, *redis_client, metrics_storage);

  EXPECT_EQ(context.redis, expected_state);

  expected_log.push_back(
      {ClientOp::Mget,
       StringVector{helpers::redis::MakeKey(kTestScope, kKey0)},
       {} /* value */,
       {} /* ttl */});

  EXPECT_EQ(context.log, expected_log);
  EXPECT_TRUE(item_list_received.empty());

  {
    ExpectedMetrics expected_metrics;
    expected_metrics.gets = 1;
    expected_metrics.get_key_counts = 1;
    expected_metrics.hits = 0;
    expected_metrics.misses = 1;
    CheckMetrics(expected_metrics);
  }
  ResetMetrics();
}

UTEST_F_MT(Redis, EmptyLists, 2) {
  std::vector<ItemList> item_lists_sent;
  helpers::redis::StoreItemLists(kTestScope, item_lists_sent, config,
                                 *redis_client, metrics_storage);

  auto key0_serialized = helpers::redis::MakeKey(kTestScope, kKey0);
  auto key1_serialized = helpers::redis::MakeKey(kTestScope, kKey1);

  Context::Storage expected_state{};
  EXPECT_EQ(context.redis, expected_state);

  std::vector<LogItem> expected_log{};
  EXPECT_EQ(context.log, expected_log);

  {
    ExpectedMetrics expected_metrics;
    expected_metrics.puts = 1;
    CheckMetrics(expected_metrics);
  }
  ResetMetrics();

  ItemIds item_ids = {kKey0, kKey1};

  auto item_lists_received = helpers::redis::LoadItemLists(
      kTestScope, item_ids, config, *redis_client, metrics_storage);

  EXPECT_EQ(context.redis, expected_state);

  expected_log.push_back(
      {TransactionOp::Smembers, key0_serialized, {} /* value */, {} /* ttl */});
  expected_log.push_back(
      {TransactionOp::Smembers, key1_serialized, {} /* value */, {} /* ttl */});
  EXPECT_EQ(context.log, expected_log);

  size_t received_total_size = 0;
  for (const auto& item : item_lists_received) {
    received_total_size += item.size();
  }
  EXPECT_TRUE(received_total_size == 0);
  EXPECT_TRUE(item_lists_sent.empty());

  {
    ExpectedMetrics expected_metrics;
    expected_metrics.gets = 1;
    expected_metrics.get_key_counts = 2;
    expected_metrics.bulk_load_size_count = 2;
    expected_metrics.misses = 2;
    CheckMetrics(expected_metrics);
  }
  ResetMetrics();
}
