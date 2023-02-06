#include "test_functions.hpp"

namespace eats_picker_orders::test {

using eats_picker_orders::models::OrderItemFull;
using eats_picker_orders::models::OrderItemWithMeasure;

std::vector<OrderItemFull> MakeOrderItemsFull(
    const std::vector<std::vector<ItemInfo>>& items_by_version) {
  std::unordered_map<std::int64_t, OrderItemFull> items_map;
  for (size_t version = 0; version < items_by_version.size(); ++version) {
    for (const auto& item_info : items_by_version[version]) {
      OrderItemFull item_full;
      item_full.item.id = item_info.id;
      item_full.item.eats_item_id = item_info.eats_item_id;
      item_full.item.version = version;
      item_full.item.author = item_info.author;
      item_full.item.author_type = item_info.author_type;
      item_full.item.quantity = item_info.quantity;
      for (const auto& replacement_of_id : item_info.replaced_items) {
        const auto& replacement_of =
            items_map.at(replacement_of_id).item.eats_item_id;
        item_full.replacements.push_back(
            {item_info.id, replacement_of, replacement_of_id});
      }
      if (!items_map.try_emplace(item_info.id, std::move(item_full)).second) {
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

std::vector<eats_picker_orders::models::OrderItemWithMeasure>
MakeOrderItemWithMeasure(
    const std::vector<std::vector<ItemInfo>>& items_by_version) {
  std::unordered_map<std::int64_t, OrderItemWithMeasure> items_map;
  for (size_t version = 0; version < items_by_version.size(); ++version) {
    for (const auto& item_info : items_by_version[version]) {
      OrderItemWithMeasure item;
      item.id = item_info.id;
      item.eats_item_id = item_info.eats_item_id;
      item.version = version;
      item.author = item_info.author;
      item.author_type = item_info.author_type;
      item.quantity = item_info.quantity;
      for (const auto& replacement_of_id : item_info.replaced_items) {
        std::string replacement_of;
        if (items_map.count(replacement_of_id)) {
          replacement_of = items_map.at(replacement_of_id).eats_item_id;
        }
        item.replacements.push_back(
            {item_info.id, replacement_of, replacement_of_id});
      }
      if (!items_map.try_emplace(item_info.id, std::move(item)).second) {
        throw std::invalid_argument("Duplicated item id");
      }
    }
  }
  std::vector<OrderItemWithMeasure> items;
  for (const auto& [id, item] : items_map) {
    items.push_back(item);
    if (!item.replacements.empty()) {
      for (const auto& replacement : item.replacements) {
        items.back().replacements.push_back(replacement);
      }
    }
  }
  return items;
}

std::vector<eats_picker_orders::models::PickedItem> MakePickedItems(
    const std::vector<std::tuple<std::int64_t, std::string, int32_t>>&
        picked_items) {
  std::vector<eats_picker_orders::models::PickedItem> result;
  for (const auto& [id, eats_item_id, count] : picked_items) {
    eats_picker_orders::models::PickedItem picked_item;
    picked_item.id = id;
    picked_item.eats_item_id = eats_item_id;
    picked_item.count = count;
    result.push_back(std::move(picked_item));
  }
  return result;
}

}  // namespace eats_picker_orders::test
