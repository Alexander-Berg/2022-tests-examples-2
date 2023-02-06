#include <gtest/gtest.h>

#include "retail_order_changes.hpp"

namespace {

using namespace eats_retail_order_history::models;
using namespace eats_retail_order_history::utils;

const handlers::PickingStatus kPicking = handlers::PickingStatus::kPicking;
const handlers::PickingStatus kPaid = handlers::PickingStatus::kPaid;

OrderItem MakeOrderItem(std::string&& origin_id,
                        std::optional<std::int32_t>&& count = 1,
                        std::optional<Weight>&& weight = {}) {
  OrderItem item;
  item.origin_id = std::move(origin_id);
  item.count = std::move(count);
  item.weight = std::move(weight);
  return item;
}

OrderItemsMap MakeOrderItemsMap(std::vector<OrderItem>&& order_items) {
  OrderItemsMap order_items_map;
  for (auto& order_item : order_items) {
    order_items_map[order_item.origin_id] = std::move(order_item);
  }
  return order_items_map;
}

CartItem MakeCartItem(std::string&& origin_id,
                      std::optional<std::int32_t>&& count = 1,
                      std::optional<handlers::Weight>&& weight = {}) {
  CartItem item;
  item.origin_id = std::move(origin_id);
  item.count = std::move(count);
  item.weight = std::move(weight);
  return item;
}

Cart MakeCart(std::vector<CartItem>&& cart_items) {
  Cart cart;
  for (auto& cart_item : cart_items) {
    cart.items.push_back(std::move(cart_item));
  }
  return cart;
}

}  // namespace

struct TestDisablingEventsParams {
  std::optional<bool> add;
  std::optional<bool> remove;
  std::optional<bool> update_count;
  std::optional<bool> update_weight;
};

class DisablingEventsTest
    : public testing::TestWithParam<TestDisablingEventsParams> {};

TEST_P(DisablingEventsTest, TestsOK) {
  stq_tasks::retail_first_order_changes_notification::OrderChanges events;
  events.add.emplace() = {{"add"}};
  events.remove.emplace() = {{"remove"}};
  events.update_count.emplace() = {{"update_count"}};
  events.update_weight.emplace() = {{"update_weight"}};
  experiments3::eats_retail_order_history_notifications::FirstRetailOrderChanges
      settings;
  const auto param = GetParam();
  if (param.add) {
    settings.events.add.emplace() = {*param.add};
  }
  if (param.remove) {
    settings.events.remove.emplace() = {*param.remove};
  }
  if (param.update_count) {
    settings.events.update_count.emplace() = {*param.update_count};
  }
  if (param.update_weight) {
    settings.events.update_weight.emplace() = {*param.update_weight};
  }
  FilterRetailOrderChanges(events, settings.events);
  if (param.add && *param.add) {
    ASSERT_TRUE(events.add);
    ASSERT_EQ(events.add->size(), 1);
  } else {
    ASSERT_FALSE(events.add);
  }
  if (param.remove && *param.remove) {
    ASSERT_TRUE(events.remove);
    ASSERT_EQ(events.remove->size(), 1);
  } else {
    ASSERT_FALSE(events.remove);
  }
  if (param.update_count && *param.update_count) {
    ASSERT_TRUE(events.update_count);
    ASSERT_EQ(events.update_count->size(), 1);
  } else {
    ASSERT_FALSE(events.update_count);
  }
  if (param.update_weight && *param.update_weight) {
    ASSERT_TRUE(events.update_weight);
    ASSERT_EQ(events.update_weight->size(), 1);
  } else {
    ASSERT_FALSE(events.update_weight);
  }
}

INSTANTIATE_TEST_SUITE_P(
    AllDisabled, DisablingEventsTest,
    testing::Values(TestDisablingEventsParams{{}, {}, {}, {}},
                    TestDisablingEventsParams{false, false, false, false}));
INSTANTIATE_TEST_SUITE_P(AllEnabled, DisablingEventsTest,
                         testing::Values(TestDisablingEventsParams{
                             true, true, true, true}));
INSTANTIATE_TEST_SUITE_P(
    OneDisabled, DisablingEventsTest,
    testing::Values(TestDisablingEventsParams{false, true, true, true},
                    TestDisablingEventsParams{true, false, true, true},
                    TestDisablingEventsParams{true, true, false, true},
                    TestDisablingEventsParams{true, true, true, false}));

TEST(TestFilterCustomerEvents, UpdateWeightNoWeightPercent) {
  stq_tasks::retail_first_order_changes_notification::OrderChanges events;
  events.update_weight.emplace() = {
      {"update_weight_id", "update_weight_name", {100}, {110}}};
  experiments3::eats_retail_order_history_notifications::FirstRetailOrderChanges
      settings;
  settings.events.update_weight.emplace() = {true};
  FilterRetailOrderChanges(events, settings.events);
  ASSERT_TRUE(events.update_weight);
  ASSERT_EQ(events.update_weight->size(), 1);
}

TEST(TestFilterCustomerEvents, UpdateWeightMoreThanWeightPercentSetting) {
  stq_tasks::retail_first_order_changes_notification::OrderChanges events;
  events.update_weight.emplace() = {
      {"update_weight_id", "update_weight_name", {100}, {110}}};
  experiments3::eats_retail_order_history_notifications::FirstRetailOrderChanges
      settings;
  settings.events.update_weight.emplace() = {true, 5};
  FilterRetailOrderChanges(events, settings.events);
  ASSERT_TRUE(events.update_weight);
  ASSERT_EQ(events.update_weight->size(), 1);
}

TEST(TestFilterCustomerEvents, UpdateWeightLessThanWeightPercentSetting) {
  stq_tasks::retail_first_order_changes_notification::OrderChanges events;
  events.update_weight.emplace() = {
      {"update_weight_id", "update_weight_name", {100}, {110}}};
  experiments3::eats_retail_order_history_notifications::FirstRetailOrderChanges
      settings;
  settings.events.update_weight.emplace() = {true, 20};
  FilterRetailOrderChanges(events, settings.events);
  ASSERT_FALSE(events.update_weight);
}

TEST(TestComputeCartChanges, NoChanges) {
  auto original_order_items = MakeOrderItemsMap(
      {MakeOrderItem("0"), MakeOrderItem("1", {}, Weight{100})});

  auto assert_events = [](const RetailOrderChanges& events) {
    ASSERT_FALSE(events.add);
    ASSERT_FALSE(events.remove);
    ASSERT_FALSE(events.update_count);
    ASSERT_FALSE(events.update_weight);
  };

  // корзина пуста (picking)
  Cart new_cart;
  auto events =
      ComputeRetailOrderChanges(original_order_items, new_cart, kPicking);
  assert_events(events);

  // в новой корзине появились товары из заказа (picking)
  new_cart = MakeCart(
      {MakeCartItem("0"), MakeCartItem("1", {}, handlers::Weight{100})});
  events = ComputeRetailOrderChanges(original_order_items, new_cart, kPicking);
  assert_events(events);

  // в новой корзине появились товары из заказа (paid)
  events = ComputeRetailOrderChanges(original_order_items, new_cart, kPaid);
  assert_events(events);
}

TEST(TestComputeCartChanges, AddItems) {
  auto original_order_items =
      MakeOrderItemsMap({MakeOrderItem("0"), MakeOrderItem("1")});

  auto assert_events = [](const RetailOrderChanges& events) {
    ASSERT_TRUE(events.add);
    ASSERT_EQ(events.add->size(), 2);
    std::unordered_set<std::string> actual;
    for (const auto& event : *events.add) {
      actual.insert(event.id);
    }
    std::unordered_set<std::string> expected{"2", "3"};
    ASSERT_EQ(actual, expected);
    ASSERT_FALSE(events.remove);
    ASSERT_FALSE(events.update_count);
    ASSERT_FALSE(events.update_weight);
  };

  // в новой корзине появились новые товары (picking)
  Cart new_cart = {{MakeCartItem("2"), MakeCartItem("3")}};
  auto events =
      ComputeRetailOrderChanges(original_order_items, new_cart, kPicking);
  assert_events(events);

  // в новой корзине появились новые товары + товары из заказа (picking)
  new_cart = {{MakeCartItem("0"), MakeCartItem("1"), MakeCartItem("2"),
               MakeCartItem("3")}};
  events = ComputeRetailOrderChanges(original_order_items, new_cart, kPicking);
  assert_events(events);

  // в новой корзине появились новые товары + товары из заказа (paid)
  events = ComputeRetailOrderChanges(original_order_items, new_cart, kPicking);
  assert_events(events);
}

TEST(TestComputeCartChanges, RemoveItems) {
  auto original_order_items =
      MakeOrderItemsMap({MakeOrderItem("0"), MakeOrderItem("1")});

  auto assert_events = [](const RetailOrderChanges& events,
                          std::unordered_set<std::string>&& expected) {
    ASSERT_FALSE(events.add);
    ASSERT_TRUE(events.remove);
    ASSERT_EQ(events.remove->size(), expected.size());
    std::unordered_set<std::string> actual;
    for (const auto& event : *events.remove) {
      actual.insert(event.id);
    }
    ASSERT_EQ(actual, expected);
    ASSERT_FALSE(events.update_count);
    ASSERT_FALSE(events.update_weight);
  };

  // в новой корзине отсутствуют товары из заказа (paid)
  Cart new_cart;
  auto events =
      ComputeRetailOrderChanges(original_order_items, new_cart, kPaid);
  assert_events(events, {"0", "1"});
}

TEST(TestComputeCartChanges, UpdateCount) {
  auto original_order_items =
      MakeOrderItemsMap({MakeOrderItem("0", 1), MakeOrderItem("1", 10)});

  auto assert_events = [](const RetailOrderChanges& events) {
    ASSERT_FALSE(events.add);
    ASSERT_FALSE(events.remove);
    ASSERT_TRUE(events.update_count);
    ASSERT_EQ(events.update_count->size(), 2);
    std::unordered_map<std::string, std::pair<int, int>> actual;
    for (const auto& event : *events.update_count) {
      actual[event.id] = {event.old_count, event.new_count};
    }
    std::unordered_map<std::string, std::pair<int, int>> expected{
        {"0", {1, 2}}, {"1", {10, 5}}};
    ASSERT_EQ(actual, expected);
    ASSERT_FALSE(events.update_weight);
  };

  // в новой корзине появились измененные товары из оригинального заказа
  // (picking)
  Cart new_cart = MakeCart({MakeCartItem("0", 2), MakeCartItem("1", 5)});
  auto events =
      ComputeRetailOrderChanges(original_order_items, new_cart, kPicking);
  assert_events(events);

  // в новой корзине появились измененные товары из оригинального заказа (paid)
  events = ComputeRetailOrderChanges(original_order_items, new_cart, kPicking);
  assert_events(events);
}

TEST(TestComputeCartChanges, UpdateWeight) {
  auto original_order_items =
      MakeOrderItemsMap({MakeOrderItem("0", {}, Weight{100}),
                         MakeOrderItem("1", {}, Weight{1000})});

  auto assert_events = [](const RetailOrderChanges& events) {
    ASSERT_FALSE(events.add);
    ASSERT_FALSE(events.remove);
    ASSERT_FALSE(events.update_count);
    ASSERT_TRUE(events.update_weight);
    ASSERT_EQ(events.update_weight->size(), 2);
    std::unordered_map<std::string, std::pair<double, double>> actual;
    for (const auto& event : *events.update_weight) {
      actual[event.id] = {event.old_weight.value, event.new_weight.value};
    }
    std::unordered_map<std::string, std::pair<double, double>> expected{
        {"0", {100, 200}}, {"1", {1000, 500}}};
    ASSERT_EQ(actual, expected);
  };

  // в новой корзине появились измененные товары из оригинального заказа
  // (picking)
  Cart new_cart = MakeCart({MakeCartItem("0", {}, handlers::Weight{200}),
                            MakeCartItem("1", {}, handlers::Weight{500})});
  auto events =
      ComputeRetailOrderChanges(original_order_items, new_cart, kPicking);
  assert_events(events);

  // в новой корзине появились измененные товары из оригинального заказа (paid)
  events = ComputeRetailOrderChanges(original_order_items, new_cart, kPicking);
  assert_events(events);
}
