#include <gtest/gtest.h>

#include "prices.hpp"

using namespace eats_picker_orders::models;

namespace {

OrderItemFull MakeOrderItemFull(
    const std::string& eats_item_id, double price, float quantity,
    int32_t measure_value,
    const std::optional<std::string>& is_deleted_by = std::nullopt,
    const std::optional<AuthorType>& deleted_by_type = std::nullopt,
    double quantum_price = 0.0, double quantum_quantity = 0.0,
    int64_t measure_quantum = 0) {
  OrderItem order_item;
  order_item.eats_item_id = eats_item_id;
  order_item.price = Money::FromFloatInexact(price);
  order_item.quantity = quantity;
  order_item.measure_value = measure_value;
  order_item.is_deleted_by = is_deleted_by;
  order_item.deleted_by_type = deleted_by_type;
  order_item.quantum_price = Money::FromFloatInexact(quantum_price);
  order_item.quantum_quantity = quantum_quantity;
  order_item.measure_quantum = measure_quantum;
  return OrderItemFull{std::move(order_item), {}};
}

PickedItem MakePickedItem(const std::string eats_item_id,
                          const std::optional<int>& count,
                          const std::optional<int>& weight) {
  PickedItem picked_item;
  picked_item.eats_item_id = eats_item_id;
  picked_item.count = count;
  picked_item.weight = weight;
  return picked_item;
}

}  // namespace

TEST(ComputeOrderTotal, NoItems) {
  std::unordered_map<std::string, OrderItemFull> order_items_map;
  std::unordered_map<std::string, PickedItem> picked_items_map;
  auto result = eats_picker_orders::utils::prices::ComputeOrderTotal(
      order_items_map, picked_items_map, "0", std::nullopt);
  Money expected;
  ASSERT_EQ(result, expected);
}

TEST(ComputeOrderTotal, NoOrderItems) {
  std::string picker_id = "picker_0";
  std::unordered_map<std::string, OrderItemFull> order_items_map;
  std::unordered_map<std::string, PickedItem> picked_items_map = {
      {"0", MakePickedItem("0", 2, std::nullopt)},
      {"1", MakePickedItem("1", 3, std::nullopt)}};
  auto result = eats_picker_orders::utils::prices::ComputeOrderTotal(
      order_items_map, picked_items_map, picker_id, std::nullopt);
  Money expected;
  ASSERT_EQ(result, expected);
}

TEST(ComputeOrderTotal, NoPickedItems) {
  std::string picker_id = "picker_0";
  std::unordered_map<std::string, OrderItemFull> order_items_map = {
      {"0", MakeOrderItemFull("0", 10.0, 1.0, 100)},
      {"1", MakeOrderItemFull("1", 20.0, 2.0, 100)}};
  std::unordered_map<std::string, PickedItem> picked_items_map;
  auto result = eats_picker_orders::utils::prices::ComputeOrderTotal(
      order_items_map, picked_items_map, picker_id, std::nullopt);
  auto expected = Money::FromFloatInexact(50.0);
  ASSERT_EQ(result, expected);
}

TEST(ComputeOrderTotal, NoPickedItemsMeasureQuantumMeasureV2) {
  std::string picker_id = "picker_0";
  std::unordered_map<std::string, OrderItemFull> order_items_map = {
      {"0", MakeOrderItemFull("0", 10.0, 1.0, 100, std::nullopt, std::nullopt,
                              30.0, 3.0, 200)},
      {"1", MakeOrderItemFull("1", 20.0, 2.0, 100, std::nullopt, std::nullopt,
                              60.0, 6.0, 200)}};
  std::unordered_map<std::string, PickedItem> picked_items_map;
  auto result = eats_picker_orders::utils::prices::ComputeOrderTotal(
      order_items_map, picked_items_map, picker_id,
      handlers::MeasureVersion::kX2);
  auto expected = Money::FromFloatInexact(450.0);
  ASSERT_EQ(result, expected);
}

TEST(ComputeOrderTotal, NoPickedItemsDeleted) {
  std::string picker_id = "picker_0";
  std::unordered_map<std::string, OrderItemFull> order_items_map = {
      {"0", MakeOrderItemFull("0", 10.0, 1.0, 100, picker_id)},
      {"0",
       MakeOrderItemFull("0", 15.0, 1.5, 100, picker_id, AuthorType::kPicker)},
      {"1", MakeOrderItemFull("2", 20.0, 2.0, 100)}};
  std::unordered_map<std::string, PickedItem> picked_items_map;
  auto result = eats_picker_orders::utils::prices::ComputeOrderTotal(
      order_items_map, picked_items_map, picker_id, std::nullopt);
  auto expected = Money::FromFloatInexact(40.0);
  ASSERT_EQ(result, expected);
}

TEST(ComputeOrderTotal, NoPickedItemsDeletedBySystem) {
  std::string picker_id = "picker_0";
  std::unordered_map<std::string, OrderItemFull> order_items_map = {
      {"0",
       MakeOrderItemFull("0", 10.0, 1.0, 100, order_items::authors::kSystem,
                         AuthorType::kSystem)},
      {"1", MakeOrderItemFull("1", 20.0, 2.0, 100)}};
  std::unordered_map<std::string, PickedItem> picked_items_map;
  auto result = eats_picker_orders::utils::prices::ComputeOrderTotal(
      order_items_map, picked_items_map, picker_id, std::nullopt);
  auto expected = Money::FromFloatInexact(40.0);
  ASSERT_EQ(result, expected);
}

TEST(ComputeOrderTotal, NoPickedItemsDeletedByCustomer) {
  std::string picker_id = "picker_0";
  std::unordered_map<std::string, OrderItemFull> order_items_map = {
      {"0", MakeOrderItemFull("0", 10.0, 1.0, 100, "customer_id",
                              AuthorType::kCustomer)},
      {"1", MakeOrderItemFull("1", 20.0, 2.0, 100)}};
  std::unordered_map<std::string, PickedItem> picked_items_map;
  auto result = eats_picker_orders::utils::prices::ComputeOrderTotal(
      order_items_map, picked_items_map, picker_id, std::nullopt);
  auto expected = Money::FromFloatInexact(40.0);
  ASSERT_EQ(result, expected);
}

TEST(ComputeOrderTotal, NoPickedItemsDeletedByAnotherPicker) {
  std::string picker_id = "picker_0";
  std::unordered_map<std::string, OrderItemFull> order_items_map = {
      {"0", MakeOrderItemFull("0", 10.0, 1.0, 100, "unknown_picker")},
      {"1", MakeOrderItemFull("1", 20.0, 2.0, 100, "unknown_picker",
                              AuthorType::kPicker)}};
  std::unordered_map<std::string, PickedItem> picked_items_map;
  auto result = eats_picker_orders::utils::prices::ComputeOrderTotal(
      order_items_map, picked_items_map, picker_id, std::nullopt);
  auto expected = Money::FromFloatInexact(50.0);
  ASSERT_EQ(result, expected);
}

TEST(ComputeOrderTotal, PickedItems) {
  std::string picker_id = "picker_0";
  std::unordered_map<std::string, OrderItemFull> order_items_map = {
      {"0", MakeOrderItemFull("0", 10.0, 1.0, 100)},
      {"1", MakeOrderItemFull("1", 20.0, 2.0, 100)}};
  std::unordered_map<std::string, PickedItem> picked_items_map = {
      {"0", MakePickedItem("0", 2, std::nullopt)},
      {"1", MakePickedItem("1", 3, std::nullopt)}};
  auto result = eats_picker_orders::utils::prices::ComputeOrderTotal(
      order_items_map, picked_items_map, picker_id, std::nullopt);
  auto expected = Money::FromFloatInexact(80.0);
  ASSERT_EQ(result, expected);
}

TEST(ComputeOrderTotal, PickedItemsMeasureQuantumMeasureV2) {
  std::string picker_id = "picker_0";
  std::unordered_map<std::string, OrderItemFull> order_items_map = {
      {"0", MakeOrderItemFull("0", 10.0, 1.0, 100, std::nullopt, std::nullopt,
                              30.0, 3.0, 200)},
      {"1", MakeOrderItemFull("1", 20.0, 2.0, 100, std::nullopt, std::nullopt,
                              60.0, 6.0, 200)}};
  std::unordered_map<std::string, PickedItem> picked_items_map = {
      {"0", MakePickedItem("0", 2, std::nullopt)},
      {"1", MakePickedItem("1", 3, std::nullopt)}};
  auto result = eats_picker_orders::utils::prices::ComputeOrderTotal(
      order_items_map, picked_items_map, picker_id,
      handlers::MeasureVersion::kX2);
  auto expected = Money::FromFloatInexact(240.0);
  ASSERT_EQ(result, expected);
}

TEST(ComputeOrderTotal, PickedItemsWeight) {
  std::string picker_id = "picker_0";
  std::unordered_map<std::string, OrderItemFull> order_items_map = {
      {"0", MakeOrderItemFull("0", 10.0, 1.0, 100)},
      {"1", MakeOrderItemFull("1", 20.0, 2.0, 200)}};
  std::unordered_map<std::string, PickedItem> picked_items_map = {
      {"0", MakePickedItem("0", std::nullopt, 200)},
      {"1", MakePickedItem("1", std::nullopt, 500)}};
  auto result = eats_picker_orders::utils::prices::ComputeOrderTotal(
      order_items_map, picked_items_map, picker_id, std::nullopt);
  auto expected = Money::FromFloatInexact(70.0);
  ASSERT_EQ(result, expected);
}

TEST(ComputeOrderTotal, PickedItemsWeightMeasureVersionMeasureV2) {
  std::string picker_id = "picker_0";
  std::unordered_map<std::string, OrderItemFull> order_items_map = {
      {"0", MakeOrderItemFull("0", 10.0, 1.0, 100, std::nullopt, std::nullopt,
                              30.0, 3.0, 200)},
      {"1", MakeOrderItemFull("1", 20.0, 2.0, 200, std::nullopt, std::nullopt,
                              60.0, 6.0, 400)}};
  std::unordered_map<std::string, PickedItem> picked_items_map = {
      {"0", MakePickedItem("0", std::nullopt, 200)},
      {"1", MakePickedItem("1", std::nullopt, 500)}};
  auto result = eats_picker_orders::utils::prices::ComputeOrderTotal(
      order_items_map, picked_items_map, picker_id,
      handlers::MeasureVersion::kX2);
  auto expected = Money::FromFloatInexact(105.0);
  ASSERT_EQ(result, expected);
}

TEST(ComputeOrderTotal, UltimateEdition) {
  std::string picker_id = "picker_0";
  std::unordered_map<std::string, OrderItemFull> order_items_map = {
      {"0", MakeOrderItemFull("0", 10.0, 1.0, 100)},                    // 20
      {"1", MakeOrderItemFull("1", 20.0, 2.0, 200)},                    // 40
      {"2", MakeOrderItemFull("2", 30.0, 3.0, 300)},                    // 50.01
      {"3", MakeOrderItemFull("3", 40.0, 1.0, 400, picker_id)},         // 0
      {"4", MakeOrderItemFull("4", 50.0, 2.0, 200, "unknown_picker")},  // 150
  };
  std::unordered_map<std::string, PickedItem> picked_items_map = {
      {"0", MakePickedItem("0", std::nullopt, 200)},
      {"2", MakePickedItem("2", std::nullopt, 500)},
      {"4", MakePickedItem("4", 3.0, std::nullopt)}};
  auto result = eats_picker_orders::utils::prices::ComputeOrderTotal(
      order_items_map, picked_items_map, picker_id, std::nullopt);
  auto expected = Money::FromFloatInexact(260.01);
  ASSERT_EQ(result, expected);
}
