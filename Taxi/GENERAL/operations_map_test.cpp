#include <gtest/gtest.h>

#include <eats-picker-orders-utils/item_version.hpp>
#include <eats-picker-orders-utils/operations_map.hpp>

namespace {

struct OrderItem {
  std::int64_t id;
  std::string eats_item_id;
  std::int32_t version;
  float quantity;
  std::int32_t measure_quantum;
  float quantum_quantity;
  decimal64::Decimal<2> price;
  decimal64::Decimal<2> quantum_price;
  std::int32_t measure_value;
};

struct PickedItem {
  std::int64_t id;
  std::string eats_id;
  std::string eats_item_id;
  std::int32_t cart_version;
  std::optional<std::int32_t> weight;
  std::optional<std::int32_t> count;
};

struct OrderItemReplacement {
  std::int64_t order_item_id;
  std::string replacement_of;
  std::int64_t replacement_of_id;
};

struct OrderItemFull {
  OrderItem item;
  std::vector<OrderItemReplacement> replacements;
};

using OrderItemsFullMap = std::unordered_map<std::string, OrderItemFull>;

using PickedItemsMap = std::unordered_map<std::string, PickedItem>;

auto MakeOrderItems(
    const std::vector<std::vector<std::tuple<std::int64_t, std::string, double,
                                             std::vector<std::int64_t>>>>&
        items_by_version) {
  std::unordered_map<std::int64_t, OrderItemFull> items_map;
  for (size_t version = 0; version < items_by_version.size(); ++version) {
    for (const auto& [id, eats_item_id, quantity, replacements] :
         items_by_version[version]) {
      OrderItemFull item_full;
      item_full.item.id = id;
      item_full.item.eats_item_id = eats_item_id;
      item_full.item.version = version;
      item_full.item.quantity = quantity;
      for (const auto& replacement_of_id : replacements) {
        const auto& replacement_of =
            items_map.at(replacement_of_id).item.eats_item_id;
        item_full.replacements.push_back(
            {id, replacement_of, replacement_of_id});
      }
      if (!items_map.try_emplace(id, std::move(item_full)).second) {
        throw std::invalid_argument("Items ids should be different");
      }
    }
  }
  std::vector<OrderItemFull> items;
  for (const auto& [id, item] : items_map) {
    items.push_back({item.item, {}});
    if (!item.replacements.empty()) {
      for (const auto& replacement : item.replacements) {
        items.back().replacements.push_back(replacement);
      }
    }
  }
  return items;
}

auto MakePickedItems(
    const std::vector<std::tuple<std::int64_t, std::string, int32_t>>&
        picked_items) {
  std::vector<PickedItem> result;
  for (const auto& [id, eats_item_id, count] : picked_items) {
    PickedItem picked_item;
    picked_item.id = id;
    picked_item.eats_item_id = eats_item_id;
    picked_item.count = count;
    result.push_back(std::move(picked_item));
  }
  return result;
}

using Quantity = eats_picker_orders_utils::quantity::Quantity;
namespace item_version = eats_picker_orders_utils::item_version;

class TestDataContainer {
 public:
  void SetOrderItems(
      const std::vector<std::vector<std::tuple<
          std::int64_t, std::string, double, std::vector<std::int64_t>>>>&
          items_by_version) {
    auto order_items = MakeOrderItems(items_by_version);
    auto last_version_items =
        item_version::FilterByMaxValue<OrderItemFull, std::int32_t>(
            order_items, [](const auto& order_item_full) {
              return order_item_full.item.version;
            });
    for (const auto& item : last_version_items) {
      order_items_map.emplace(item.item.eats_item_id, item);
    }
    auto first_version_items =
        item_version::FilterByMinValue<OrderItemFull, std::int32_t>(
            std::move(order_items), [](const auto& order_item_full) {
              return order_item_full.item.version;
            });
    for (const auto& item : first_version_items) {
      original_items_map.emplace(item.item.eats_item_id, item);
    }
  }
  void SetPickedItems(
      const std::vector<std::tuple<std::int64_t, std::string, std::int32_t>>&
          picked_items) {
    for (const auto& item : MakePickedItems(picked_items)) {
      picked_items_map.emplace(item.eats_item_id, item);
    }
  }
  const auto& GetOrderItemsMap() const { return order_items_map; }
  const auto& GetOriginalItemsMap() const { return original_items_map; }
  const auto& GetPickedItemsMap() const { return picked_items_map; }

 private:
  OrderItemsFullMap order_items_map;
  OrderItemsFullMap original_items_map;
  PickedItemsMap picked_items_map;
};

using eats_picker_orders_utils::operations_map::Operation;
using eats_picker_orders_utils::operations_map::OperationsMap;
using eats_picker_orders_utils::operations_map::OperationType;
using eats_picker_orders_utils::price_aligner::Money;
using eats_picker_orders_utils::price_aligner::PriceAlignResult;

}  // namespace

TEST(MakeOperationsMap, NoParams) {
  TestDataContainer data;
  auto result = eats_picker_orders_utils::operations_map::MakeOperationsMap(
      data.GetOriginalItemsMap(), data.GetPickedItemsMap());
  OperationsMap expected = {};
  ASSERT_EQ(result, expected);
}

TEST(MakeOperationsMap, NoReplacementsPartiallyPicked) {
  TestDataContainer data;
  data.SetOrderItems(
      {{{1, "item-1", 1, {}}, {2, "item-2", 2, {}}, {3, "item-3", 3, {}}}});
  data.SetPickedItems({{1, "item-1", 1}, {3, "item-3", 1}});
  auto result = eats_picker_orders_utils::operations_map::MakeOperationsMap(
      data.GetOriginalItemsMap(), data.GetPickedItemsMap());
  OperationsMap expected = {{OperationType::kUpdate, {{"item-3"}}},
                            {OperationType::kRemove, {{"item-2"}}}};
}

TEST(MakeOperationsMap, Sample) {
  TestDataContainer data;
  data.SetOrderItems(
      {{{1, "item-1", 1, {}}, {2, "item-2", 2, {}}, {3, "item-3", 3, {}}},
       {{4, "item-4", 4, {1}}, {5, "item-2", 2, {}}, {6, "item-3", 3, {}}},
       {{7, "item-4", 4, {1}}, {8, "item-5", 8, {5}}, {9, "item-3", 3, {}}}});
  data.SetPickedItems({{7, "item-4", 7}, {9, "item-3", 9}});
  auto result = eats_picker_orders_utils::operations_map::MakeOperationsMap(
      data.GetOriginalItemsMap(), data.GetPickedItemsMap());
  OperationsMap expected = {
      {OperationType::kAdd, {{"item-4"}}},
      {OperationType::kUpdate, {{"item-3", Quantity::FromFloatInexact(9.0)}}},
      {OperationType::kRemove, {{"item-1"}, {"item-2"}}}};
  ASSERT_EQ(result, expected);
}

TEST(MakeOperationsMap, ReplaceManyToOne) {
  TestDataContainer data;
  data.SetOrderItems({{{1, "item-1", 1, {}},
                       {2, "item-2", 2, {}},
                       {3, "item-3", 3, {}},
                       {4, "item-4", 4, {}}},
                      {{5, "item-5", 5, {1, 2}}, {6, "item-6", 6, {3, 4}}},
                      {{7, "item-1", 7, {5, 6}}}});
  data.SetPickedItems({{7, "item-1", 7}});
  auto result = eats_picker_orders_utils::operations_map::MakeOperationsMap(
      data.GetOriginalItemsMap(), data.GetPickedItemsMap());
  OperationsMap expected = {
      {OperationType::kUpdate, {{"item-1", Quantity::FromFloatInexact(7.0)}}},
      {OperationType::kRemove, {{"item-2"}, {"item-3"}, {"item-4"}}}};
  ASSERT_EQ(result, expected);
}

TEST(MakeOperationsMap, ReplaceOneToMany) {
  TestDataContainer data;
  data.SetOrderItems(
      {{{1, "item-1", 1, {}}, {2, "item-2", 2, {}}, {3, "item-3", 3, {}}},
       {{4, "item-4", 4, {1}},
        {5, "item-5", 5, {1}},
        {6, "item-6", 6, {2}},
        {7, "item-2", 7, {2}},
        {8, "item-7", 8, {3}},
        {9, "item-3", 9, {3}}}});
  data.SetPickedItems({{4, "item-4", 4}, {6, "item-6", 6}, {9, "item-3", 9}});
  auto result = eats_picker_orders_utils::operations_map::MakeOperationsMap(
      data.GetOriginalItemsMap(), data.GetPickedItemsMap());
  OperationsMap expected = {
      {OperationType::kAdd, {{"item-4"}, {"item-6"}}},
      {OperationType::kUpdate, {{"item-3", Quantity::FromFloatInexact(9.0)}}},
      {OperationType::kRemove, {{"item-1"}, {"item-2"}}}};
  ASSERT_EQ(result, expected);
}

TEST(MakeOperationsMap, ReplaceManyToOneToMany) {
  TestDataContainer data;
  data.SetOrderItems({{{1, "item-1", 1, {}},
                       {2, "item-2", 2, {}},
                       {3, "item-3", 3, {}},
                       {4, "item-4", 4, {}}},
                      {{5, "item-5", 5, {1, 2}}, {6, "item-6", 6, {3, 4}}},
                      {{7, "item-1", 7, {5}},
                       {8, "item-2", 8, {5}},
                       {9, "item-9", 9, {6}},
                       {10, "item-10", 10, {6}}}});
  data.SetPickedItems({{7, "item-1", 7}, {9, "item-9", 9}});
  auto result = eats_picker_orders_utils::operations_map::MakeOperationsMap(
      data.GetOriginalItemsMap(), data.GetPickedItemsMap());
  OperationsMap expected = {
      {OperationType::kAdd, {{"item-9"}}},
      {OperationType::kUpdate, {{"item-1", Quantity::FromFloatInexact(7.0)}}},
      {OperationType::kRemove, {{"item-2"}, {"item-3"}, {"item-4"}}}};
  ASSERT_EQ(result, expected);
}

TEST(MakeOperationsMap, PartiallyOverlappingReplace) {
  TestDataContainer data;
  data.SetOrderItems(
      {{{1, "item-1", 1, {}}, {2, "item-2", 2, {}}, {3, "item-3", 3, {}}},
       {{4, "item-4", 4, {1, 2}}, {5, "item-5", 5, {2, 3}}},
       {{6, "item-6", 6, {4}}, {7, "item-7", 7, {5}}}});
  data.SetPickedItems({{7, "item-7", 7}});
  auto result = eats_picker_orders_utils::operations_map::MakeOperationsMap(
      data.GetOriginalItemsMap(), data.GetPickedItemsMap());
  OperationsMap expected = {
      {OperationType::kAdd, {{"item-7"}}},
      {OperationType::kRemove, {{"item-1"}, {"item-2"}, {"item-3"}}}};
  ASSERT_EQ(result, expected);
}

TEST(MakeOperationsMap, CrossReplacement) {
  TestDataContainer data;
  data.SetOrderItems({{{1, "item-1", 1, {}}, {2, "item-2", 2, {}}},
                      {{3, "item-2", 3, {1}}, {4, "item-1", 4, {1}}}});
  data.SetPickedItems({{3, "item-2", 3}});
  auto result = eats_picker_orders_utils::operations_map::MakeOperationsMap(
      data.GetOriginalItemsMap(), data.GetPickedItemsMap());
  OperationsMap expected = {
      {OperationType::kUpdate, {{"item-2", Quantity::FromFloatInexact(3.0)}}},
      {OperationType::kRemove, {{"item-1"}}}};
  ASSERT_EQ(result, expected);
}

TEST(MakeOperationsMap, AddItems) {
  TestDataContainer data;
  data.SetOrderItems(
      {{{1, "item-1", 1, {}}},
       {{2, "item-2", 2, {1}}, {3, "item-3", 3, {}}, {4, "item-4", 4, {}}}});
  data.SetPickedItems({{2, "item-2", 2}, {3, "item-3", 3}});
  auto result = eats_picker_orders_utils::operations_map::MakeOperationsMap(
      data.GetOriginalItemsMap(), data.GetPickedItemsMap());
  OperationsMap expected = {{OperationType::kAdd, {{"item-2"}, {"item-3"}}},
                            {OperationType::kRemove, {{"item-1"}}}};
  ASSERT_EQ(result, expected);
}

TEST(MakeOperationsMap, RemoveItem) {
  TestDataContainer data;
  data.SetOrderItems(
      {{{1, "item-1", 1, {}}, {2, "item-2", 2, {}}}, {{3, "item-3", 3, {1}}}});
  data.SetPickedItems({{3, "item-3", 3}});
  auto result = eats_picker_orders_utils::operations_map::MakeOperationsMap(
      data.GetOriginalItemsMap(), data.GetPickedItemsMap());
  OperationsMap expected = {{OperationType::kAdd, {{"item-3"}}},
                            {OperationType::kRemove, {{"item-1"}, {"item-2"}}}};
  ASSERT_EQ(result, expected);
}

TEST(MakeOperationsMap, AddItemsAlignResult) {
  TestDataContainer data;
  data.SetOrderItems(
      {{{1, "item-1", 1, {}}, {2, "item-2", 2, {}}},
       {{11, "item-1", 1, {}}, {22, "item-2", 2, {}}, {3, "item-3", 3, {}}}});
  data.SetPickedItems({{1, "item-1", 1}, {2, "item-2", 3}, {3, "item-3", 3}});
  const auto residual = Money::FromFloatInexact(0.01);
  PriceAlignResult align_result{true, residual};
  auto result = eats_picker_orders_utils::operations_map::MakeOperationsMap(
      data.GetOriginalItemsMap(), data.GetPickedItemsMap(),
      &data.GetOrderItemsMap(), &align_result);
  OperationsMap expected = {
      {OperationType::kAdd,
       {{"item-3"},
        {eats_picker_orders_utils::operations_map::kFakeItemIdentity,
         Quantity::FromFloatInexact(1.0), residual}}},
      {OperationType::kUpdate,
       {{"item-2", Quantity::FromFloatInexact(3.0), Money{}},
        {"item-1", {}, Money{}}}}};
  ASSERT_EQ(result, expected);
}

TEST(MakeOperationsMap, MeasureV2UpdateQuantity) {
  OrderItemFull original_item_full;
  original_item_full.item.id = 1;
  original_item_full.item.eats_item_id = "item-1";
  original_item_full.item.version = 0;
  original_item_full.item.quantity = 1;
  original_item_full.item.measure_quantum = 100;
  original_item_full.item.quantum_quantity = 2;
  PickedItem picked_item;
  picked_item.id = 1;
  picked_item.eats_item_id = original_item_full.item.eats_item_id;
  picked_item.count = 2;
  OrderItemsFullMap order_items{
      {original_item_full.item.eats_item_id, original_item_full}};
  PickedItemsMap picked_items{{picked_item.eats_item_id, picked_item}};
  auto result = eats_picker_orders_utils::operations_map::MakeOperationsMap(
      order_items, picked_items);
  OperationsMap expected = {
      {OperationType::kUpdate, {{"item-1", Quantity::FromFloatInexact(2.0)}}}};
  ASSERT_EQ(result, expected);
}

TEST(MakeOperationsMap, MeasureV2AlignResult) {
  OrderItemFull original_item_full;
  original_item_full.item.id = 1;
  original_item_full.item.eats_item_id = "item-1";
  original_item_full.item.version = 0;
  original_item_full.item.quantity = 1;
  original_item_full.item.measure_quantum = 100;
  original_item_full.item.quantum_quantity = 1;
  original_item_full.item.price = 100;
  original_item_full.item.quantum_price = 200;
  PickedItem picked_item;
  picked_item.id = 1;
  picked_item.eats_item_id = original_item_full.item.eats_item_id;
  picked_item.count = 1;
  const auto residual = Money::FromFloatInexact(0.01);
  PriceAlignResult align_result{true, residual};
  OrderItemsFullMap original_items = {
      {original_item_full.item.eats_item_id, original_item_full}};
  OrderItemsFullMap order_items{
      {original_item_full.item.eats_item_id, original_item_full}};
  PickedItemsMap picked_items{{picked_item.eats_item_id, picked_item}};
  auto result = eats_picker_orders_utils::operations_map::MakeOperationsMap(
      original_items, picked_items, &order_items, &align_result);
  OperationsMap expected = {
      {OperationType::kAdd,
       {{eats_picker_orders_utils::operations_map::kFakeItemIdentity,
         Quantity::FromFloatInexact(1.), residual}}},
      {OperationType::kUpdate,
       {{"item-1", {}, Money::FromFloatInexact(100.)}}}};
  ASSERT_EQ(result, expected);
}

TEST(MakeOperationsMap, UpdateQuantityAndPrice) {
  OrderItemFull original_item_full;
  original_item_full.item.id = 1;
  original_item_full.item.eats_item_id = "item-1";
  original_item_full.item.version = 0;
  original_item_full.item.quantity = 1;
  original_item_full.item.price = 150;
  OrderItemFull order_item_full = original_item_full;
  order_item_full.item.version = 1;
  order_item_full.item.price = 200;
  PickedItem picked_item;
  picked_item.id = 1;
  picked_item.eats_item_id = original_item_full.item.eats_item_id;
  picked_item.count = 2;
  OrderItemsFullMap original_items{
      {original_item_full.item.eats_item_id, original_item_full}};
  OrderItemsFullMap order_items{
      {order_item_full.item.eats_item_id, order_item_full}};
  PickedItemsMap picked_items{{picked_item.eats_item_id, picked_item}};
  auto result = eats_picker_orders_utils::operations_map::MakeOperationsMap(
      original_items, picked_items, &order_items);
  OperationsMap expected = {{OperationType::kUpdate,
                             {{"item-1", Quantity::FromFloatInexact(2.),
                               Money::FromFloatInexact(200.)}}}};
  ASSERT_EQ(result, expected);
}

TEST(MakeOperationsMap, MeasureV2UpdateQuantityAndPrice) {
  OrderItemFull original_item_full;
  original_item_full.item.id = 1;
  original_item_full.item.eats_item_id = "item-1";
  original_item_full.item.version = 0;
  original_item_full.item.quantity = 1;
  original_item_full.item.measure_quantum = 100;
  original_item_full.item.quantum_quantity = 2;
  original_item_full.item.price = 150;
  OrderItemFull order_item_full = original_item_full;
  order_item_full.item.version = 1;
  order_item_full.item.price = 200;
  PickedItem picked_item;
  picked_item.id = 1;
  picked_item.eats_item_id = original_item_full.item.eats_item_id;
  picked_item.count = 2;
  OrderItemsFullMap original_items{
      {original_item_full.item.eats_item_id, original_item_full}};
  OrderItemsFullMap order_items{
      {order_item_full.item.eats_item_id, order_item_full}};
  PickedItemsMap picked_items{{picked_item.eats_item_id, picked_item}};
  auto result = eats_picker_orders_utils::operations_map::MakeOperationsMap(
      original_items, picked_items, &order_items);
  OperationsMap expected = {{OperationType::kUpdate,
                             {{"item-1", Quantity::FromFloatInexact(2.),
                               Money::FromFloatInexact(200.)}}}};
  ASSERT_EQ(result, expected);
}
