#include <gtest/gtest.h>

#include <ml/discounts/optimization/aggregators.hpp>
#include <ml/discounts/optimization/functions.hpp>
#include <ml/discounts/optimization/objects.hpp>

namespace {
using namespace ml::discounts::optimization;
}  // namespace

TEST(DiscountsOptimizationV1, aggregators) {
  std::vector<Item> items = {
      {false, 1., 1.},
      {false, 7., 4.},
      {true, 101., 2.},
      {true, 507., 9.},
  };
  auto aggregator = ReversedCostOfExtraTripAggregatorFactory().Create();
  for (const auto& item : items) {
    aggregator->AddItem(item);
  }
  ASSERT_DOUBLE_EQ(aggregator->GetValue(), -0.01);

  aggregator = TripsRelativeIncreaseAggregatorFactory().Create();
  for (const auto& item : items) {
    aggregator->AddItem(item);
  }
  ASSERT_DOUBLE_EQ(aggregator->GetValue(), -1.2);
}

TEST(DiscountsOptimizationV1, functions) {
  auto dataset = std::make_shared<Dataset>(2);
  dataset->AddItem({false, 1., 1.}, {0, 1});
  dataset->AddItem({false, 7., 4.}, {1, 0});
  dataset->AddItem({true, 101., 2.}, {0, 1});
  dataset->AddItem({true, 307., 10}, {1, 0});

  auto func = std::make_shared<FunctionV1>(
      FunctionV1Config{{{0.5, 2}, {1.0, 1}}, 0.1, 1, 1, 0},
      std::make_shared<ReversedCostOfExtraTripAggregatorFactory>(), dataset,
      42);
  ASSERT_DOUBLE_EQ(func->Eval(std::vector<double>{1, 0}), -0.0575);

  EvaluationPool pool(4);
  auto result =
      pool.Map(func, std::vector<std::vector<double>>{{1, 0}, {-1, 0}, {0, 1}});
  ASSERT_EQ(result.size(), 3ul);
  ASSERT_DOUBLE_EQ(result[0], -0.0575);
  ASSERT_DOUBLE_EQ(result[1], -0.0375);
  ASSERT_DOUBLE_EQ(result[2], -0.0375);
}
