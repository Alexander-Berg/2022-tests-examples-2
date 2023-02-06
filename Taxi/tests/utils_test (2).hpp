#pragma once

#include <widgets/turbo_buttons/button_group.hpp>
#include <widgets/turbo_buttons/place_button.hpp>

#include <sources/catalog/catalog_data_source.hpp>

#include <defs/internal/turbo_buttons.hpp>

namespace eats_layout_constructor::widgets::turbo_buttons::tests {

struct PlusBadge {
  std::string text;
  std::string icon;
};

struct Place {
  int place_id = 1;
  int brand_id = 1;
  bool is_avaialbe_now = true;
  std::string name = "my place";
  std::string slug = "my_slug";
  std::string logo_url = "logo/url";
  std::string eta = "10 - 20min";
  bool available = true;
  defs::internal::turbo_buttons::Business business =
      defs::internal::turbo_buttons::Business::kRestaurant;
  std::optional<PlusBadge> plus_badge;
};

sources::catalog::Place GetCatalogPlace(const Place& input);

ColorConfig GetColorConfig();

sources::DataSourceResponses GetDataSourceResponse(
    const std::string& block_id, const std::vector<Place>& place);

void AssertColor(const std::vector<::handlers::ThemedColorA>& color,
                 const std::string& light, const std::string& dark);

/*
 * Хелпер, чтобы рендерить группу кнопок
 * сразу в json
 */
formats::json::Value Render(const ButtonGroup& group);

}  // namespace eats_layout_constructor::widgets::turbo_buttons::tests
