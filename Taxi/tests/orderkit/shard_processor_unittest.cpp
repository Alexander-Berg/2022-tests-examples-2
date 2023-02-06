#include <functional>

#include <mongo/mongo.hpp>
#include <sharding/shard_processor.hpp>

#include <gtest/gtest.h>
#include <memory>

using ProcProcessor = orderkit::mongo::OrderProcShardProcessor;
using OrdersProcessor = orderkit::mongo::OrdersShardProcessor;
using GetShardProcessorFunc =
    std::function<std::shared_ptr<utils::mongo::ShardProcessor>(bool, bool)>;

struct OrderShardProcessorTestData {
  mongo::BSONObj original_query;
  mongo::BSONObj expected_query;
  bool enable;
  bool throws;
  GetShardProcessorFunc get_shard_processor;
};

class OrderShardProcessorTest
    : public ::testing::TestWithParam<OrderShardProcessorTestData> {};

namespace {
template <typename T>
std::shared_ptr<utils::mongo::ShardProcessor> GetProcessor(bool enabled,
                                                           bool throws) {
  auto processor = std::make_shared<T>();
  processor->SetEnabled(enabled);
  processor->SetThrowErrors(throws);
  return processor;
}
}  // namespace

TEST_P(OrderShardProcessorTest, test_modify_query) {
  auto processor = GetParam().get_shard_processor(GetParam().enable, false);
  ASSERT_EQ(GetParam().expected_query,
            processor->ModifySearchQuery(GetParam().original_query));
  ASSERT_EQ(GetParam().expected_query,
            processor->ModifyUpdateQuery(GetParam().original_query, false));
}

TEST_P(OrderShardProcessorTest, test_modify_query_complex) {
  auto processor = GetParam().get_shard_processor(GetParam().enable, false);
  mongo::Query original_query = GetParam().original_query;
  original_query.readPref(mongo::ReadPreference_SecondaryPreferred, {});
  original_query.sort("srt", utils::mongo::kDesc);
  original_query.hint(BSON("hnt" << 1));
  original_query.maxTimeMs(1001);

  const auto& result = processor->ModifySearchQuery(original_query);
  ASSERT_EQ(GetParam().expected_query, result.getFilter());
  ASSERT_EQ(BSON("mode"
                 << "secondaryPreferred"),
            result.getReadPref());
  ASSERT_EQ(BSON("srt" << utils::mongo::kDesc), result.getSort());
  ASSERT_EQ(BSON("hnt" << 1), result.getHint().Obj());
  ASSERT_EQ(1001, result.getMaxTimeMs());
}

TEST_P(OrderShardProcessorTest, test_modify_query_throws) {
  auto processor = GetParam().get_shard_processor(false, true);
  ASSERT_NO_THROW(processor->ModifySearchQuery(GetParam().original_query));
  if (GetParam().throws) {
    ASSERT_THROW(processor->ModifyUpdateQuery(GetParam().original_query, false),
                 orderkit::mongo::ModifyQueryError);
  } else {
    ASSERT_NO_THROW(
        processor->ModifyUpdateQuery(GetParam().original_query, false));
  }
}

static const std::string uuid_1 = "5cb681209766550190ace379d97b1ce4";
static const std::string uuid_0 = "5cb681209766450190ace379d97b1ce4";

namespace {
template <typename T>
OrderShardProcessorTestData TestForAlias(const std::string& field,
                                         int shard_id) {
  bool throws = true;
  const std::string& uuid = (shard_id == 0) ? uuid_0 : uuid_1;
  const auto& original = BSON(field << uuid);
  mongo::BSONObjBuilder expected_builder;
  if (shard_id == 1) {
    // only for non special shards
    expected_builder.append("_shard_id", 1);
    throws = false;
  }
  expected_builder.append(field, uuid);
  return {original, expected_builder.obj(), true, throws, GetProcessor<T>};
}
}  // namespace

// Looks like you cannot compare BSONs without sort order, so this test is
// a bit miserable
INSTANTIATE_TEST_CASE_P(
    OrderProcTests, OrderShardProcessorTest,
    ::testing::Values(
        // 0. disabled
        OrderShardProcessorTestData{BSON("_id" << uuid_1),
                                    BSON("_id" << uuid_1), false, false,
                                    GetProcessor<ProcProcessor>},

        // 1. shard 0 id
        OrderShardProcessorTestData{BSON("_id" << uuid_0),
                                    BSON("_shard_id" << 0 << "_id" << uuid_0),
                                    true, false, GetProcessor<ProcProcessor>},

        // 2. shard 1 id
        OrderShardProcessorTestData{BSON("_id" << uuid_1),
                                    BSON("_shard_id" << 1 << "_id" << uuid_1),
                                    true, false, GetProcessor<ProcProcessor>},

        // 3. shard 0 reorder id
        OrderShardProcessorTestData{
            BSON("$or" << BSON_ARRAY(BSON("reorder.id" << uuid_0)
                                     << BSON("_id" << uuid_0))),
            BSON("_shard_id" << 0 << "$or"
                             << BSON_ARRAY(BSON("reorder.id" << uuid_0)
                                           << BSON("_id" << uuid_0))),
            true, false, GetProcessor<ProcProcessor>},

        // 4. does not select if contradictory shard ids
        OrderShardProcessorTestData{
            BSON("$or" << BSON_ARRAY(BSON("reorder.id" << uuid_1)
                                     << BSON("_id" << uuid_0))),
            BSON("$or" << BSON_ARRAY(BSON("reorder.id" << uuid_1)
                                     << BSON("_id" << uuid_0))),
            true, true, GetProcessor<ProcProcessor>},

        // 5. shard 1 reorder id
        OrderShardProcessorTestData{
            BSON("$or" << BSON_ARRAY(BSON("reorder.id" << uuid_1)
                                     << BSON("_id" << uuid_1))),
            BSON("_shard_id" << 1 << "$or"
                             << BSON_ARRAY(BSON("reorder.id" << uuid_1)
                                           << BSON("_id" << uuid_1))),
            true, false, GetProcessor<ProcProcessor>},

        // 6. id & alias id shard 1
        OrderShardProcessorTestData{
            BSON("$or" << BSON_ARRAY(BSON("aliases.id" << uuid_1)
                                     << BSON("_id" << uuid_1))),
            BSON("_shard_id" << 1 << "$or"
                             << BSON_ARRAY(BSON("aliases.id" << uuid_1)
                                           << BSON("_id" << uuid_1))),
            true, false, GetProcessor<ProcProcessor>},

        // 7. id & alias id shard 0 => secondary
        OrderShardProcessorTestData{
            BSON("$or" << BSON_ARRAY(BSON("aliases.id" << uuid_0)
                                     << BSON("_id" << uuid_0))),
            BSON("$or" << BSON_ARRAY(BSON("aliases.id" << uuid_0)
                                     << BSON("_id" << uuid_0))),
            true, true, GetProcessor<ProcProcessor>},

        // 8. id & some other info
        OrderShardProcessorTestData{
            BSON("$or" << BSON_ARRAY(BSON("user_id" << uuid_1)
                                     << BSON("_id" << uuid_1))),
            BSON("$or" << BSON_ARRAY(BSON("user_id" << uuid_1)
                                     << BSON("_id" << uuid_1))),
            true, true, GetProcessor<ProcProcessor>},

        TestForAlias<ProcProcessor>("aliases.id", 0),
        TestForAlias<ProcProcessor>("aliases.id", 1),
        TestForAlias<ProcProcessor>("performer.alias_id", 0),
        TestForAlias<ProcProcessor>("performer.alias_id", 1),
        TestForAlias<ProcProcessor>("candidates.alias_id", 0),
        TestForAlias<ProcProcessor>("candidates.alias_id", 1)), );

// Looks like you cannot compare BSONs without sort order, so this test is
// a bit miserable
INSTANTIATE_TEST_CASE_P(
    OrdersTests, OrderShardProcessorTest,
    ::testing::Values(
        // 0. disabled
        OrderShardProcessorTestData{BSON("_id" << uuid_1),
                                    BSON("_id" << uuid_1), false, false,
                                    GetProcessor<OrdersProcessor>},

        // 1. shard 0 id
        OrderShardProcessorTestData{BSON("_id" << uuid_0),
                                    BSON("_shard_id" << 0 << "_id" << uuid_0),
                                    true, false, GetProcessor<OrdersProcessor>},

        // 2. shard 1 id
        OrderShardProcessorTestData{BSON("_id" << uuid_1),
                                    BSON("_shard_id" << 1 << "_id" << uuid_1),
                                    true, false, GetProcessor<OrdersProcessor>},

        // 3. shard 0 reorder id
        OrderShardProcessorTestData{
            BSON("$or" << BSON_ARRAY(BSON("reorder.id" << uuid_0)
                                     << BSON("_id" << uuid_0))),
            BSON("_shard_id" << 0 << "$or"
                             << BSON_ARRAY(BSON("reorder.id" << uuid_0)
                                           << BSON("_id" << uuid_0))),
            true, false, GetProcessor<OrdersProcessor>},

        // 4. does not select if contradictory shard ids
        OrderShardProcessorTestData{
            BSON("$or" << BSON_ARRAY(BSON("reorder.id" << uuid_1)
                                     << BSON("_id" << uuid_0))),
            BSON("$or" << BSON_ARRAY(BSON("reorder.id" << uuid_1)
                                     << BSON("_id" << uuid_0))),
            true, true, GetProcessor<OrdersProcessor>},

        // 5. shard 1 reorder id
        OrderShardProcessorTestData{
            BSON("$or" << BSON_ARRAY(BSON("reorder.id" << uuid_1)
                                     << BSON("_id" << uuid_1))),
            BSON("_shard_id" << 1 << "$or"
                             << BSON_ARRAY(BSON("reorder.id" << uuid_1)
                                           << BSON("_id" << uuid_1))),
            true, false, GetProcessor<OrdersProcessor>},

        // 6. id & alias id shard 1
        OrderShardProcessorTestData{
            BSON("$or" << BSON_ARRAY(BSON("performer.taxi_alias.id" << uuid_1)
                                     << BSON("_id" << uuid_1))),
            BSON("_shard_id"
                 << 1 << "$or"
                 << BSON_ARRAY(BSON("performer.taxi_alias.id" << uuid_1)
                               << BSON("_id" << uuid_1))),
            true, false, GetProcessor<OrdersProcessor>},

        // 7. id & alias id shard 0 => secondary
        OrderShardProcessorTestData{
            BSON("$or" << BSON_ARRAY(BSON("performer.taxi_alias.id" << uuid_0)
                                     << BSON("_id" << uuid_0))),
            BSON("$or" << BSON_ARRAY(BSON("performer.taxi_alias.id" << uuid_0)
                                     << BSON("_id" << uuid_0))),
            true, true, GetProcessor<OrdersProcessor>},

        // 8. id & some other info
        OrderShardProcessorTestData{
            BSON("$or" << BSON_ARRAY(BSON("user_id" << uuid_1)
                                     << BSON("_id" << uuid_1))),
            BSON("$or" << BSON_ARRAY(BSON("user_id" << uuid_1)
                                     << BSON("_id" << uuid_1))),
            true, true, GetProcessor<OrdersProcessor>},

        TestForAlias<OrdersProcessor>("performer.taxi_alias.id", 0),
        TestForAlias<OrdersProcessor>("performer.taxi_alias.id", 1)), );
