#include "view.hpp"

namespace handlers::test_mapping_save_mappings::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  namespace models = eats_menu_categories::models;

  std::vector<models::Mapping> mappings;
  mappings.reserve(request.body.mappings.size());

  for (auto& mapping : request.body.mappings) {
    mappings.push_back(models::Mapping{
        models::ScoredCategory{
            models::CategoryId(
                std::move(mapping.scored_category.category_id)),  // category_id
            mapping.scored_category.score,                        // score
        },                                                    // scored_category
        models::MenuItemId(std::move(mapping.menu_item_id)),  // menu_item_id
        mapping.place_id,                                     // place_id
        models::RuleId(std::move(mapping.rule_id)),           // rule_id
        std::nullopt,                                         // created_at
    });
  }

  dependencies.extra.mappings.SaveMappings(mappings);

  Response204 response;
  return response;
}

}  // namespace handlers::test_mapping_save_mappings::post
