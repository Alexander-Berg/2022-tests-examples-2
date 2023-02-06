#include <userver/utest/utest.hpp>
#include <userver/utils/statistics/metadata.hpp>

#include <statistics/common_statistics_conversion.hpp>

namespace {

using JsonValueBuilder = formats::json::ValueBuilder;
using JsonValue = formats::json::Value;
using JsonType = formats::json::Type;
constexpr auto kJsonTag = formats::serialize::To<JsonValue>{};

using yaga_metrolog::statistics::ShardsStatistics;
using yaga_metrolog::statistics::SingleShardStatistics;

class StatisticsFixture : public ::testing::Test {
 public:
  static SingleShardStatistics ShardStatisticsSample1() {
    return CreateShardStatistics(5u, 10u);
  }
  static JsonValue ShardStatisticsSample1Json() {
    return CreateShardStatisticsJson(5u, 10u);
  }

  static SingleShardStatistics ShardStatisticsSample2() {
    return CreateShardStatistics(13u, 666u);
  }
  static JsonValue ShardStatisticsSample2Json() {
    return CreateShardStatisticsJson(13u, 666u);
  }

  static void FillShardsStatistics(ShardsStatistics& stats) {
    stats.Clear();
    stats.Emplace(0u, ShardStatisticsSample1());
    stats.Emplace(1u, ShardStatisticsSample2());
  }
  static JsonValue ShardsStatisticsSampleJson() {
    JsonValueBuilder builder{JsonType::kObject};
    builder["0"] = ShardStatisticsSample1Json();
    builder["1"] = ShardStatisticsSample2Json();
    return builder.ExtractValue();
  }

  static JsonValue PositionsStatisticsSampleJson() {
    JsonValueBuilder builder{JsonType::kObject};
    builder["shards"] = ShardsStatisticsSampleJson();
    for (auto&& shard_stats : builder["shards"]) {
      AddLabelTo(shard_stats);
    }
    return builder.ExtractValue();
  }

 private:
  static SingleShardStatistics CreateShardStatistics(size_t messages,
                                                     size_t positions) {
    return {messages, positions};
  }

  static JsonValue CreateShardStatisticsJson(size_t messages,
                                             size_t positions) {
    JsonValueBuilder builder{JsonType::kObject};
    builder["messages"] = messages;
    builder["positions"] = positions;
    return builder.ExtractValue();
  }

  static void AddLabelTo(JsonValueBuilder& builder) {
    utils::statistics::SolomonLabelValue(builder, "positions-channel-shard");
  }
};

UTEST_F(StatisticsFixture, SimpleSingleShardStatistics) {
  const SingleShardStatistics stat = ShardStatisticsSample1();
  const JsonValue expected = ShardStatisticsSample1Json();

  ASSERT_EQ(expected, yaga_metrolog::statistics::ToJson(stat));
  ASSERT_EQ(expected, yaga_metrolog::statistics::Serialize(stat, kJsonTag));
}

UTEST_F(StatisticsFixture, SimpleShardsStatistics) {
  ShardsStatistics stat;
  // Can't return statistics object from function because copy and move ctors
  // are deleted
  FillShardsStatistics(stat);
  const JsonValue expected = ShardsStatisticsSampleJson();

  ASSERT_EQ(expected, yaga_metrolog::statistics::ToJson(stat));
  ASSERT_EQ(expected, yaga_metrolog::statistics::Serialize(stat, kJsonTag));
}

}  // namespace
