#include <gtest/gtest.h>

#include <widgets/turbo_buttons/places_button_group.hpp>

#include "utils_test.hpp"

namespace eats_layout_constructor::widgets::turbo_buttons::tests {

TEST(PlacesButtonGroup, Generic) {
  // Проверяет общий случай
  // перекладывания ответа каталога в кнопки
  PlacesButtonGroupParams params{};
  params.business.push_back("store");
  params.limit = 1;
  params.filter_type = sources::catalog::PlaceType::kOpen;
  params.color_config = GetColorConfig();
  params.compilation_type = "some-compilation";
  params.sort_type = sources::catalog::SortType::kFastDelivery;
  auto eta_colors = params.color_config.eta_colors;

  PlacesButtonGroup group{params};

  eats_layout_constructor::sources::DataSourceParams source_params;
  group.FillSourceRequestParams(source_params);
  auto catalog_params =
      std::any_cast<eats_layout_constructor::sources::catalog::Params>(
          source_params["catalog"]);
  ASSERT_EQ(catalog_params.blocks.size(), 1);

  const static std::string kBlockId = "btn_open_limit_1_store";

  ASSERT_EQ(catalog_params.blocks.count(kBlockId), 1);
  auto block = catalog_params.blocks[kBlockId];
  ASSERT_EQ(block.type, sources::catalog::PlaceType::kOpen);
  ASSERT_TRUE(block.compilation_type.has_value());
  ASSERT_EQ(block.compilation_type.value(), params.compilation_type);
  ASSERT_TRUE(block.sort_type.has_value());
  ASSERT_EQ(block.sort_type.value(), params.sort_type);
  ASSERT_TRUE(block.condition.has_value());

  Place place{};
  auto source_respose = GetDataSourceResponse(kBlockId, {place});
  group.ProcessSourceResponse(source_respose);

  auto builder = Render(group);
  auto result = builder.As<std::vector<::handlers::TurboButton>>();

  ASSERT_EQ(result.size(), 1);
  const auto& button = result.front();
  ASSERT_EQ(button.name, place.name);
  ASSERT_EQ(button.description.value().text, place.eta);
  AssertColor(button.description.value().color, eta_colors.open.light,
              eta_colors.open.dark);
}

}  // namespace eats_layout_constructor::widgets::turbo_buttons::tests
