#include <gtest/gtest.h>

#include "common.hpp"
#include "models/original_order_items.hpp"

using namespace eats_retail_order_history;

struct Param {
  double original_cost_for_customer;
  std::optional<int> original_count;
  std::optional<models::Weight> original_weight;
  double final_cost_for_customer;
  std::optional<int> final_count;
  std::optional<models::Weight> final_weight;
  bool updated;
};

class IsPriceUpdatedTest : public testing::TestWithParam<Param> {};
class IsPriceUpdatedTestException : public testing::TestWithParam<Param> {};

auto MakeItems(const Param& param) {
  models::OrderItem original_item;
  original_item.cost_for_customer =
      models::Money::FromFloatInexact(param.original_cost_for_customer);
  original_item.count = param.original_count;
  original_item.weight = param.original_weight;
  models::OrderItem final_item;
  final_item.cost_for_customer =
      models::Money::FromFloatInexact(param.final_cost_for_customer);
  final_item.count = param.final_count;
  final_item.weight = param.final_weight;
  return std::make_pair(std::move(original_item), std::move(final_item));
}

TEST_P(IsPriceUpdatedTest, TestsOK) {
  const auto param = GetParam();
  const auto [original_item, final_item] = MakeItems(param);
  ASSERT_EQ(IsPriceUpdated(original_item, final_item), param.updated);
}

TEST_P(IsPriceUpdatedTestException, TestsException) {
  const auto [original_item, final_item] = MakeItems(GetParam());
  EXPECT_THROW(IsPriceUpdated(original_item, final_item), std::runtime_error);
}

INSTANTIATE_TEST_SUITE_P(SameCostForCount, IsPriceUpdatedTest,
                         testing::Values(Param{100, 3, {}, 100, 3, {}, false},
                                         Param{100, 10, {}, 100, 5, {}, true},
                                         Param{1, 33, {}, 1, 34, {}, true},
                                         // округление до 4 знака:
                                         Param{1, 333, {}, 1, 334, {}, false},
                                         Param{
                                             1, 3333, {}, 1, 3334, {}, false}));
INSTANTIATE_TEST_SUITE_P(
    SameCostForWeight, IsPriceUpdatedTest,
    testing::Values(
        Param{100, {}, {{200, "GRM"}}, 100, {}, {{200, "GRM"}}, false},
        Param{100, {}, {{100, "GRM"}}, 100, {}, {{500, "GRM"}}, true},
        Param{10, {}, {{333, "GRM"}}, 10, {}, {{334, "GRM"}}, true},
        // округление до 4 знака:
        Param{10, {}, {{3333, "GRM"}}, 10, {}, {{3334, "GRM"}}, false}));
INSTANTIATE_TEST_SUITE_P(DifferentCostForCount, IsPriceUpdatedTest,
                         testing::Values(Param{100, 3, {}, 200, 3, {}, true},
                                         Param{100, 2, {}, 200, 4, {}, false},
                                         Param{100, 2, {}, 200, 5, {}, true}));
INSTANTIATE_TEST_SUITE_P(
    DifferentCostForWeight, IsPriceUpdatedTest,
    testing::Values(
        Param{100, {}, {{100, "GRM"}}, 200, {}, {{100, "GRM"}}, true},
        Param{100, {}, {{100, "GRM"}}, 200, {}, {{200, "GRM"}}, false},
        Param{100, {}, {{100, "GRM"}}, 200, {}, {{300, "GRM"}}, true}));
INSTANTIATE_TEST_SUITE_P(
    DifferentType, IsPriceUpdatedTest,
    testing::Values(Param{100, 1, {}, 1000, {}, {{100, "GRM"}}, {}},
                    Param{100, {}, {{100, "GRM"}}, 1000, 1, {}, {}}));
INSTANTIATE_TEST_SUITE_P(RuntimeError, IsPriceUpdatedTestException,
                         testing::Values(Param{{}, {}, {}, {}, {}, {}, {}},
                                         Param{{}, 1, {}, {}, {}, {}, {}},
                                         Param{{}, {}, {}, {}, 1, {}, {}}));

models::OrderItem MakeOrderItem(std::string&& origin_id,
                                std::string&& cost_for_customer) {
  models::OrderItem item;
  item.origin_id = std::move(origin_id);
  item.cost_for_customer = models::Money(cost_for_customer);
  return item;
}

models::OrderItemsMap MakeOrderItemsMap(
    std::vector<models::OrderItem>&& order_items) {
  models::OrderItemsMap order_items_map;
  for (auto&& order_item : order_items) {
    order_items_map[order_item.origin_id] = std::move(order_item);
  }
  return order_items_map;
}

PickerItem MakePickerItem(std::string&& id, std::string&& quantum_price,
                          double quantum_quantity) {
  PickerItem item;
  item.id = std::move(id);
  item.measure_v2.quantum_price = quantum_price;
  item.measure_v2.quantum_quantity = quantum_quantity;
  return item;
}

using ItemsChanged = defs::internal::cart_diff::ItemsChangedA;

TEST(TestCalculateFinalCost, NoChanges) {
  auto original_items = MakeOrderItemsMap({
      MakeOrderItem("no_changes_0", "10"),
      MakeOrderItem("no_changes_1", "20"),
  });
  OrderCartDiff cart_diff;
  auto final_cost = CalculateFinalCost(original_items, cart_diff);
  ASSERT_EQ(final_cost, models::Money("30"));

  cart_diff.picked_items = {"no_changes_0", "no_changes_1"};
  final_cost = CalculateFinalCost(original_items, cart_diff);
  ASSERT_EQ(final_cost, models::Money("30"));
}

TEST(TestCalculateFinalCost, Add) {
  auto original_items = MakeOrderItemsMap({
      MakeOrderItem("no_changes_0", "10"),
      MakeOrderItem("no_changes_1", "20"),
  });
  OrderCartDiff cart_diff;
  cart_diff.add = {
      MakePickerItem("add_0", "30", 1),
      MakePickerItem("add_1", "10", 2),
  };
  auto final_cost = CalculateFinalCost(original_items, cart_diff);
  ASSERT_EQ(final_cost, models::Money("30"));

  cart_diff.picked_items = {"no_changes_0", "no_changes_1", "add_0", "add_1"};
  final_cost = CalculateFinalCost(original_items, cart_diff);
  ASSERT_EQ(final_cost, models::Money("80"));
}

TEST(TestCalculateFinalCost, Remove) {
  auto original_items = MakeOrderItemsMap({
      MakeOrderItem("no_changes_0", "10"),
      MakeOrderItem("remove_0", "20"),
  });
  OrderCartDiff cart_diff;
  cart_diff.remove = {
      MakePickerItem("remove_0", "10", 2),
  };
  auto final_cost = CalculateFinalCost(original_items, cart_diff);
  ASSERT_EQ(final_cost, models::Money("10"));

  cart_diff.picked_items = {"no_changes_0", "remove_0"};
  final_cost = CalculateFinalCost(original_items, cart_diff);
  ASSERT_EQ(final_cost, models::Money("30"));
}

TEST(TestCalculateFinalCost, Replace) {
  auto original_items = MakeOrderItemsMap({
      MakeOrderItem("no_changes_0", "10"),
      MakeOrderItem("replace_0", "20"),
  });
  OrderCartDiff cart_diff;
  cart_diff.replace = {
      {MakePickerItem("replace_0", "10", 2),
       MakePickerItem("replacement_0", "50", 2)},
  };
  auto final_cost = CalculateFinalCost(original_items, cart_diff);
  ASSERT_EQ(final_cost, models::Money("30"));

  cart_diff.picked_items = {"no_changes_0", "replacement_0"};
  final_cost = CalculateFinalCost(original_items, cart_diff);
  ASSERT_EQ(final_cost, models::Money("110"));
}

TEST(TestCalculateFinalCost, ReplaceThenAdd) {
  auto original_items = MakeOrderItemsMap({
      MakeOrderItem("replace_then_add_0", "10"),
  });
  OrderCartDiff cart_diff;
  cart_diff.replace = {
      {MakePickerItem("replace_then_add_0", "10", 1),
       MakePickerItem("replacement_0", "50", 2)},
  };
  cart_diff.picked_items = {"replace_then_add_0", "replacement_0"};
  auto final_cost = CalculateFinalCost(original_items, cart_diff);
  ASSERT_EQ(final_cost, models::Money("110"));
}

TEST(TestCalculateFinalCost, Update) {
  auto original_items = MakeOrderItemsMap({
      MakeOrderItem("no_changes_0", "10"),
      MakeOrderItem("update_0", "20"),
  });
  OrderCartDiff cart_diff;
  cart_diff.update = {
      {MakePickerItem("update_0", "10", 2),
       MakePickerItem("update_0", "50", 2)},
  };
  auto final_cost = CalculateFinalCost(original_items, cart_diff);
  ASSERT_EQ(final_cost, models::Money("30"));

  cart_diff.picked_items = {"no_changes_0", "update_0"};
  final_cost = CalculateFinalCost(original_items, cart_diff);
  ASSERT_EQ(final_cost, models::Money("110"));
}

TEST(TestCalculateFinalCost, SoftDelete) {
  auto original_items = MakeOrderItemsMap({
      MakeOrderItem("no_changes_0", "10"),
      MakeOrderItem("soft_delete_0", "20"),
  });
  OrderCartDiff cart_diff;
  cart_diff.soft_delete = {
      MakePickerItem("soft_delete_0", "10", 2),
  };
  auto final_cost = CalculateFinalCost(original_items, cart_diff);
  ASSERT_EQ(final_cost, models::Money("10"));

  cart_diff.picked_items = {"no_changes_0", "soft_delete_0"};
  final_cost = CalculateFinalCost(original_items, cart_diff);
  ASSERT_EQ(final_cost, models::Money("30"));
}

TEST(TestCalculateFinalCost, AllTogether) {
  auto original_items = MakeOrderItemsMap({
      MakeOrderItem("no_changes_0", "10"),
      MakeOrderItem("no_changes_1", "20"),
      MakeOrderItem("no_changes_picked_0", "30"),
      MakeOrderItem("remove_0", "20"),
      MakeOrderItem("replace_0", "10"),
      MakeOrderItem("update_0", "30"),
      MakeOrderItem("soft_delete_0", "40"),
  });
  OrderCartDiff cart_diff;
  cart_diff.add = {
      MakePickerItem("add_0", "30", 1),
      MakePickerItem("add_1", "10", 2),
  };
  cart_diff.remove = {
      MakePickerItem("remove_0", "20", 1),
  };
  cart_diff.replace = {
      {MakePickerItem("replace_0", "10", 1),
       MakePickerItem("replacement_0", "20", 3)},
  };
  cart_diff.update = {
      {MakePickerItem("update_0", "30", 1),
       MakePickerItem("update_0", "20", 2)},
  };
  cart_diff.soft_delete = {
      MakePickerItem("soft_delete_0", "40", 1),
  };
  auto final_cost = CalculateFinalCost(original_items, cart_diff);
  ASSERT_EQ(final_cost, models::Money("100"));

  cart_diff.picked_items = {"remove_0", "soft_delete_0"};
  final_cost = CalculateFinalCost(original_items, cart_diff);
  ASSERT_EQ(final_cost, models::Money("160"));

  cart_diff.picked_items = {"no_changes_picked_0", "add_0", "add_1",
                            "replacement_0", "update_0"};
  final_cost = CalculateFinalCost(original_items, cart_diff);
  ASSERT_EQ(final_cost, models::Money("210"));
}
