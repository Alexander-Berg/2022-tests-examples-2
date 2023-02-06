#include <userver/utest/utest.hpp>

#include <sharding/controller.hpp>
#include <sharding/rule.hpp>
#include <sharding/schema.hpp>

namespace processing::sharding {

class ControllerTester {
 public:
  static auto MakeSchema() {
    Schema schema;  // default ctor private
    schema.schema_parameters_.hash_sizes_["item_id"] = 4;
    return std::make_unique<Schema>(std::move(schema));
  }

  static void AddRule(Rule rule, Schema& schema) {
    schema.rules_.push_back(std::move(rule));
  }

  Schema& AddSchema(int weight, bool readonly) {
    auto schema = MakeSchema();
    schema->weight_ = weight;
    schema->readonly_ = readonly;
    controller_.schemas_.push_back(std::move(schema));
    return *controller_.schemas_.back();
  }

  const Controller& GetController() {
    controller_.Sort();
    return controller_;
  }

 private:
  Controller controller_;
};

TEST(ShardingController, ControllerEmpty) {
  ControllerTester tester;
  const Controller& controller = tester.GetController();

  EXPECT_THROW(controller.GetShardForWrite({}), std::runtime_error);
  EXPECT_THROW(controller.GetShardsForRead({}), std::runtime_error);
  EXPECT_THROW(controller.GetShardForWrite({{"foo", "bar"}}),
               std::runtime_error);
  EXPECT_THROW(controller.GetShardsForRead({{"foo", "bar"}}),
               std::runtime_error);
}

TEST(ShardingController, ControllerSingleSchema) {
  using Values = std::unordered_set<size_t>;

  ControllerTester tester;
  const Controller& controller = tester.GetController();

  Schema& schema = tester.AddSchema(0, false);
  Condition::List conditions;
  conditions.push_back(
      std::make_unique<conditions::ByUuid>("item_id", Values{0, 1, 2, 3}));
  ControllerTester::AddRule(
      Rule(std::move(conditions), nullptr, nullptr, "", 0), schema);

  for (const auto& item_id : {"1850c0962e00ccfeab5d5230363eec59",
                              "e0c92960e781fd5fa9f7ff8546e5e021"}) {
    std::string id(item_id);
    EXPECT_EQ(controller.GetShardForWrite({{"item_id", id}}).shard_, 0);
    EXPECT_EQ(controller.GetShardsForRead({{"item_id", id}}).front().shard_, 0);
  }
}

TEST(ShardingController, ControllerTwoSchemasPhase1) {
  using Values = std::unordered_set<size_t>;

  ControllerTester tester;

  {
    Condition::List conditions;
    conditions.push_back(
        std::make_unique<conditions::ByUuid>("item_id", Values{0, 1, 2, 3}));
    Schema& schema = tester.AddSchema(0, false);
    ControllerTester::AddRule(
        Rule(std::move(conditions), nullptr, nullptr, "", 0), schema);
  }

  {
    Schema& schema = tester.AddSchema(1, true);

    {
      Condition::List conditions;
      conditions.push_back(
          std::make_unique<conditions::ByUuid>("item_id", Values{0, 1}));
      ControllerTester::AddRule(
          Rule(std::move(conditions), nullptr, nullptr, "", 1), schema);
    }

    {
      Condition::List conditions;
      conditions.push_back(
          std::make_unique<conditions::ByUuid>("item_id", Values{2, 3}));
      ControllerTester::AddRule(
          Rule(std::move(conditions), nullptr, nullptr, "", 1), schema);
    }
  }

  const Controller& controller = tester.GetController();
  for (const auto& item_id : {"1850c0962e00ccfeab5d5230363eec59",
                              "e0c92960e781fd5fa9f7ff8546e5e021"}) {
    std::string id(item_id);
    EXPECT_EQ(controller.GetShardForWrite({{"item_id", id}}).shard_, 0);
    EXPECT_EQ(controller.GetShardsForRead({{"item_id", id}})[0].shard_, 1);
    EXPECT_EQ(controller.GetShardsForRead({{"item_id", id}})[1].shard_, 0);
  }
}

TEST(ShardingController, ControllerTwoSchemasPhase2) {
  using Values = std::unordered_set<size_t>;

  ControllerTester tester;

  {
    Schema& schema = tester.AddSchema(0, false);
    Condition::List conditions;
    conditions.push_back(
        std::make_unique<conditions::ByUuid>("item_id", Values{0, 1, 2, 3}));
    ControllerTester::AddRule(
        Rule(std::move(conditions), nullptr, nullptr, "", 0), schema);
  }

  {
    Schema& schema = tester.AddSchema(1, false);

    {
      Condition::List conditions;
      conditions.push_back(
          std::make_unique<conditions::ByUuid>("item_id", Values{0, 1}));
      ControllerTester::AddRule(
          Rule(std::move(conditions), nullptr, nullptr, "", 1), schema);
    }

    {
      Condition::List conditions;
      conditions.push_back(
          std::make_unique<conditions::ByUuid>("item_id", Values{2, 3}));
      ControllerTester::AddRule(
          Rule(std::move(conditions), nullptr, nullptr, "", 1), schema);
    }
  }

  const Controller& controller = tester.GetController();
  for (const auto& item_id : {"1850c0962e00ccfeab5d5230363eec59",
                              "e0c92960e781fd5fa9f7ff8546e5e021"}) {
    std::string id(item_id);
    EXPECT_EQ(controller.GetShardForWrite({{"item_id", id}}).shard_, 1);
    EXPECT_EQ(controller.GetShardsForRead({{"item_id", id}})[0].shard_, 1);
    EXPECT_EQ(controller.GetShardsForRead({{"item_id", id}})[1].shard_, 0);
  }
}

}  // namespace processing::sharding
