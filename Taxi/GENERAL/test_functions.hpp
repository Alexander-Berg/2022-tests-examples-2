#include "models/order_items.hpp"
#include "models/picked_items.hpp"

namespace eats_picker_orders::test {

struct ItemInfo {
  using AuthorType = eats_picker_orders::models::AuthorType;
  ItemInfo() = default;
  ItemInfo(std::int64_t id, std::string eats_item_id, double quantity,
           std::vector<std::int64_t> replaced_items = {},
           std::optional<std::string> author = std::nullopt,
           std::optional<AuthorType> author_type = std::nullopt)
      : id(id),
        eats_item_id(std::move(eats_item_id)),
        quantity(quantity),
        replaced_items(std::move(replaced_items)),
        author(std::move(author)),
        author_type(std::move(author_type)) {}
  std::int64_t id{};
  std::string eats_item_id;
  double quantity;
  std::vector<std::int64_t> replaced_items;
  std::optional<std::string> author;
  std::optional<eats_picker_orders::models::AuthorType> author_type;
};

std::vector<eats_picker_orders::models::OrderItemFull> MakeOrderItemsFull(
    const std::vector<std::vector<ItemInfo>>& items_by_version);

std::vector<eats_picker_orders::models::OrderItemWithMeasure>
MakeOrderItemWithMeasure(
    const std::vector<std::vector<ItemInfo>>& items_by_version);

std::vector<eats_picker_orders::models::PickedItem> MakePickedItems(
    const std::vector<std::tuple<std::int64_t, std::string, std::int32_t>>&
        picked_items);

}  // namespace eats_picker_orders::test
