#include <userver/utest/utest.hpp>

#include <sharding/rule.hpp>
#include <sharding/schema.hpp>

namespace processing::sharding {

class SchemaTester {
 public:
  void AddRule(Rule rule) { schema_.rules_.push_back(std::move(rule)); }

  const Schema& GetSchema() const { return schema_; }

 private:
  Schema schema_;
};

TEST(ShardingSchema, SchemaEdgeCases) {
  SchemaTester tester;

  EXPECT_THROW(tester.GetSchema().SelectShard({}), std::runtime_error);
  EXPECT_THROW(tester.GetSchema().SelectShard({{"foo", "bar"}}),
               std::runtime_error);
}

TEST(ShardingSchema, SchemaHappyPath) {
  using Values = std::unordered_set<std::string>;
  SchemaTester tester;

  const std::string kCluster0("cluster0");
  const std::string kCluster1("cluster1");
  const std::string kCluster2("cluster2");

  {
    Condition::List conditions;
    conditions.push_back(
        std::make_unique<conditions::ByValues>("foo", Values{"bar"}));
    tester.AddRule(Rule(std::move(conditions), nullptr, nullptr, kCluster0, 0));
  }

  {
    Condition::List conditions;
    conditions.push_back(
        std::make_unique<conditions::ByValues>("foo", Values{"joe"}));
    tester.AddRule(Rule(std::move(conditions), nullptr, nullptr, kCluster1, 0));
  }

  {
    Condition::List conditions;
    conditions.push_back(
        std::make_unique<conditions::ByValues>("foo", Values{"doe"}));
    tester.AddRule(Rule(std::move(conditions), nullptr, nullptr, kCluster2, 0));
  }

  const Schema& schema = tester.GetSchema();

  EXPECT_EQ(schema.SelectShard({{"foo", "bar"}}).dbalias_, kCluster0);
  EXPECT_EQ(schema.SelectShard({{"foo", "joe"}}).dbalias_, kCluster1);
  EXPECT_EQ(schema.SelectShard({{"foo", "doe"}}).dbalias_, kCluster2);
  EXPECT_THROW(schema.SelectShard({{"foo", "baz"}}), std::runtime_error);
}

}  // namespace processing::sharding
