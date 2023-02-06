#include <gtest/gtest.h>
#include <boost/uuid/random_generator.hpp>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <logging/log_extra.hpp>
#include <models/experiments3_cache_manager.hpp>
#include <orderkit/order_shards.hpp>
#include <orderkit/order_shards_impl.hpp>
#include <utils/uuid4.hpp>

TEST(OrderShard, get_set_shard_id) {
  boost::uuids::random_generator uuid_gen;
  boost::uuids::uuid uuid = uuid_gen();
  LogExtra log_extra;
  for (size_t shard_id = 0; shard_id <= 0x3f; ++shard_id) {
    auto uuid2 = uuid;
    order_shards::SetShardId(uuid2, shard_id, log_extra);
    auto uuid_str = utils::generators::ToHex(uuid2);
    ASSERT_EQ(shard_id, order_shards::GetShardId(uuid_str));
  }
}

TEST(OrderShard, get_set_shard_id_again) {
  boost::uuids::random_generator uuid_gen;
  boost::uuids::uuid uuid = uuid_gen();
  LogExtra log_extra;
  for (size_t shard_id = 0; shard_id <= 0x3f; ++shard_id) {
    auto uuid2 = uuid;
    order_shards::SetShardId(uuid2, shard_id, log_extra);
    if (shard_id == 0) {
      ASSERT_EQ(uuid, uuid2);
    } else {
      ASSERT_NE(uuid, uuid2);
    }
    order_shards::SetShardId(uuid2, 0u, log_extra);
    ASSERT_EQ(uuid, uuid2);
  }
}

TEST(OrderShard, compare_reference) {
  /*
   * Reference implementation
   * https://paste.yandex-team.ru/583724
   */
  std::vector<std::string> uuids = {
      "5cb681209766450190ace379d97b1ce4", "5cb681209766550190ace379d97b1ce4",
      "5cb681209766650190ace379d97b1ce4", "5cb681209766750190ace379d97b1ce4",
      "5cb681209766050190ace379d97b1ce4", "5cb681209766150190ace379d97b1ce4",
      "5cb681209766250190ace379d97b1ce4", "5cb681209766350190ace379d97b1ce4",
      "5cb681209766c50190ace379d97b1ce4", "5cb681209766d50190ace379d97b1ce4",
      "5cb681209766e50190ace379d97b1ce4", "5cb681209766f50190ace379d97b1ce4",
      "5cb681209766850190ace379d97b1ce4", "5cb681209766950190ace379d97b1ce4",
      "5cb681209766a50190ace379d97b1ce4", "5cb681209766b50190ace379d97b1ce4",
      "5cb6812097664501d0ace379d97b1ce4", "5cb6812097665501d0ace379d97b1ce4",
      "5cb6812097666501d0ace379d97b1ce4", "5cb6812097667501d0ace379d97b1ce4",
      "5cb6812097660501d0ace379d97b1ce4", "5cb6812097661501d0ace379d97b1ce4",
      "5cb6812097662501d0ace379d97b1ce4", "5cb6812097663501d0ace379d97b1ce4",
      "5cb681209766c501d0ace379d97b1ce4", "5cb681209766d501d0ace379d97b1ce4",
      "5cb681209766e501d0ace379d97b1ce4", "5cb681209766f501d0ace379d97b1ce4",
      "5cb6812097668501d0ace379d97b1ce4", "5cb6812097669501d0ace379d97b1ce4",
      "5cb681209766a501d0ace379d97b1ce4", "5cb681209766b501d0ace379d97b1ce4",
      "5cb681209766450110ace379d97b1ce4", "5cb681209766550110ace379d97b1ce4",
      "5cb681209766650110ace379d97b1ce4", "5cb681209766750110ace379d97b1ce4",
      "5cb681209766050110ace379d97b1ce4", "5cb681209766150110ace379d97b1ce4",
      "5cb681209766250110ace379d97b1ce4", "5cb681209766350110ace379d97b1ce4",
      "5cb681209766c50110ace379d97b1ce4", "5cb681209766d50110ace379d97b1ce4",
      "5cb681209766e50110ace379d97b1ce4", "5cb681209766f50110ace379d97b1ce4",
      "5cb681209766850110ace379d97b1ce4", "5cb681209766950110ace379d97b1ce4",
      "5cb681209766a50110ace379d97b1ce4", "5cb681209766b50110ace379d97b1ce4",
      "5cb681209766450150ace379d97b1ce4", "5cb681209766550150ace379d97b1ce4",
      "5cb681209766650150ace379d97b1ce4", "5cb681209766750150ace379d97b1ce4",
      "5cb681209766050150ace379d97b1ce4", "5cb681209766150150ace379d97b1ce4",
      "5cb681209766250150ace379d97b1ce4", "5cb681209766350150ace379d97b1ce4",
      "5cb681209766c50150ace379d97b1ce4", "5cb681209766d50150ace379d97b1ce4",
      "5cb681209766e50150ace379d97b1ce4", "5cb681209766f50150ace379d97b1ce4",
      "5cb681209766850150ace379d97b1ce4", "5cb681209766950150ace379d97b1ce4",
      "5cb681209766a50150ace379d97b1ce4", "5cb681209766b50150ace379d97b1ce4",

  };
  ASSERT_EQ(uuids.size(), 0x40U);
  for (uint8_t shard_id = 0; shard_id <= 0x3fU; ++shard_id) {
    ASSERT_EQ(shard_id, order_shards::GetShardId(uuids[shard_id]));
  }
}

struct GenerateOrderIdData {
  bool enabled;
  std::vector<uint8_t> shard_ids;
  uint8_t expected_shard_id;
};

class OrderShardId : public ::testing::TestWithParam<GenerateOrderIdData> {};

TEST_P(OrderShardId, generate_order_id) {
  const auto& params = GetParam();
  auto docs_map = config::DocsMapForTest();
  docs_map.Override("ORDER_SHARDS_ENABLED", params.enabled);
  docs_map.Override("ORDER_SHARDS", params.shard_ids);
  config::Config config(docs_map);
  LogExtra log_extra;
  const std::string& order_id =
      order_shards::GenerateOrderId(config, {}, {}, log_extra);
  ASSERT_EQ(32U, order_id.size());
  ASSERT_EQ(params.expected_shard_id, order_shards::GetShardId(order_id));
}

INSTANTIATE_TEST_CASE_P(Common, OrderShardId,
                        ::testing::Values(GenerateOrderIdData{false, {5}, 0},
                                          GenerateOrderIdData{true, {0}, 0},
                                          GenerateOrderIdData{true, {}, 0},
                                          GenerateOrderIdData{true, {5}, 5}), );

struct GenerateOrderShardId {
  std::string order_id;
  uint8_t shard_id;
};

class OrderShardIdGet : public ::testing::TestWithParam<GenerateOrderShardId> {
};

TEST_P(OrderShardIdGet, get_shard_id) {
  const auto& params = GetParam();
  ASSERT_EQ(params.shard_id, order_shards::GetShardId(params.order_id));
}

INSTANTIATE_TEST_CASE_P(
    Common, OrderShardIdGet,
    ::testing::Values(
        GenerateOrderShardId{"6b21bc4e88674b5588930c78eedb3722", 0},
        GenerateOrderShardId{"7864127d-99eb-4e1e-a2de-0eabf995b4b4", 0},
        GenerateOrderShardId{"invalid_uuid", 0},
        GenerateOrderShardId{"91fba762e1ce8410bef9fb73c4f018a0", 12},
        GenerateOrderShardId{"1bca80e551b7b9456229930eaf60175c", 63},
        GenerateOrderShardId{"2ca408b0-b4a5-311b-def0-ff82b429e8c3", 23}), );

struct WeightedTestParam {
  size_t generator_hint;
  uint8_t shard_id;
};

class WeightedGen : public ::testing::TestWithParam<WeightedTestParam> {};

class VeryRandomEngine {
 public:
  using result_type = size_t;
  constexpr size_t min() { return 0; }
  constexpr size_t max() {
    return 14;  // this should match total weight so distribution work correctly
  }
  size_t operator()() const { return hint_; }
  const size_t hint_;
};

TEST_P(WeightedGen, generate) {
  order_shards::Shards shards;
  shards.push_back({0, 0});
  shards.push_back({1, 3});
  shards.push_back({2, 1});
  shards.push_back({3, 10});
  // 0 + 3 + 1 + 10 == 14 = total weight

  const auto& params = GetParam();
  VeryRandomEngine rng{params.generator_hint};
  ASSERT_EQ(params.shard_id,
            order_shards::GenShardByWeightedConfig(rng, shards, {}));
}

INSTANTIATE_TEST_CASE_P(
    Common, WeightedGen,
    ::testing::Values(WeightedTestParam{0, 1}, WeightedTestParam{1, 1},
                      WeightedTestParam{2, 1}, WeightedTestParam{3, 2},
                      WeightedTestParam{4, 3}, WeightedTestParam{5, 3},
                      WeightedTestParam{13, 3}), );
