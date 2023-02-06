#include "view.hpp"

namespace handlers::test_mapping_remove_mappings_for_items::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  std::vector<eats_menu_categories::models::MenuItemId> menu_item_ids;
  menu_item_ids.reserve(request.body.menu_items.size());

  for (auto& menu_item_id : request.body.menu_items) {
    menu_item_ids.emplace_back(std::move(menu_item_id));
  }

  dependencies.extra.mappings.RemoveMappingsForItems(menu_item_ids);

  Response204 response;
  return response;
}

}  // namespace handlers::test_mapping_remove_mappings_for_items::post
