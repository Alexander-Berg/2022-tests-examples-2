#include <gtest/gtest.h>

#include <widgets/turbo_buttons/collection_button_group.hpp>

#include "utils_test.hpp"

#include <fmt/format.h>

namespace eats_layout_constructor::widgets::turbo_buttons::tests {

const std::string kCollectionSlug = "my_collection";

CollectionButtonGroup MakeCollectionButtonGroup(
    const size_t buttons_count = 1,
    const std::optional<ShowMore>& show_more = std::nullopt) {
  CollectionButtonGroupParams params{};
  params.collection_slug = kCollectionSlug;
  params.color_config = GetColorConfig();
  params.buttons_count = buttons_count;
  params.show_more = show_more;
  CollectionButtonGroup group{params};
  return group;
};

TEST(CollectionButtonGroup, Generic) {
  // Проверяет общее перекладывание полей из
  // ответа каталога в кнопки коллекции
  const size_t kShowButtons = 1;
  auto group = MakeCollectionButtonGroup(kShowButtons);

  eats_layout_constructor::sources::DataSourceParams source_params;
  group.FillSourceRequestParams(source_params);
  auto catalog_params =
      std::any_cast<eats_layout_constructor::sources::catalog::Params>(
          source_params["catalog"]);
  ASSERT_EQ(catalog_params.blocks.size(), 2);

  const auto open_block_id =
      fmt::format("btn_collection_{}_open", kCollectionSlug);
  const auto closed_block_id =
      fmt::format("btn_collection_{}_closed", kCollectionSlug);

  ASSERT_EQ(catalog_params.blocks.count(open_block_id), 1);
  ASSERT_EQ(catalog_params.blocks.count(closed_block_id), 1);

  auto open_block = catalog_params.blocks[open_block_id];
  ASSERT_EQ(open_block.type, sources::catalog::PlaceType::kOpen);
  ASSERT_TRUE(open_block.collection_slug.has_value());
  ASSERT_EQ(open_block.collection_slug.value(), kCollectionSlug);
  ASSERT_FALSE(open_block.sort_type.has_value());

  auto closed_block = catalog_params.blocks[closed_block_id];
  ASSERT_EQ(closed_block.type, sources::catalog::PlaceType::kClosed);
  ASSERT_TRUE(closed_block.collection_slug.has_value());
  ASSERT_EQ(closed_block.collection_slug.value(), kCollectionSlug);
  ASSERT_FALSE(closed_block.sort_type.has_value());

  Place place{};
  auto source_respose = GetDataSourceResponse(open_block_id, {place});
  group.ProcessSourceResponse(source_respose);

  auto builder = Render(group);
  auto result = builder.As<std::vector<::handlers::TurboButton>>();

  ASSERT_EQ(result.size(), 1);
  const auto& button = result.front();
  ASSERT_EQ(button.name, place.name);
}

TEST(CollectionButtonGroup, NoShowMore) {
  // Проверяет кейс, когда кнопку "еще" показывать не надо
  const size_t kShowButtons = 1;
  auto group = MakeCollectionButtonGroup(kShowButtons);

  sources::DataSourceParams source_params;
  group.FillSourceRequestParams(source_params);
  const auto open_block_id =
      fmt::format("btn_collection_{}_open", kCollectionSlug);

  std::vector<Place> places;
  const size_t kPlacesCount = 3;
  for (size_t i = 0; i < kPlacesCount; i++) {
    auto& place = places.emplace_back();
    place.name = fmt::format("place_{}", i);
  }
  auto source_respose = GetDataSourceResponse(open_block_id, places);
  group.ProcessSourceResponse(source_respose);

  auto builder = Render(group);
  auto result = builder.As<std::vector<::handlers::TurboButton>>();

  ASSERT_EQ(result.size(), 1);
  const auto& button = result.front();
  ASSERT_EQ(button.name, places.front().name);
}

TEST(CollectionButtonGroup, ShowMore) {
  // Проверяет кейс, когда кнопку "еще" показывать надо
  ShowMore show_more{};
  show_more.icon_url = "show_more/icon";
  show_more.name_key = sources::localization::TankerKey{"more"};
  const size_t kShowButtons = 1;
  auto group = MakeCollectionButtonGroup(kShowButtons, show_more);

  sources::DataSourceParams source_params;
  group.FillSourceRequestParams(source_params);
  const auto open_block_id =
      fmt::format("btn_collection_{}_open", kCollectionSlug);

  std::vector<Place> places;
  const size_t kPlacesCount = 3;
  for (size_t i = 0; i < kPlacesCount; i++) {
    auto& place = places.emplace_back();
    place.name = fmt::format("place_{}", i);
  }
  auto source_respose = GetDataSourceResponse(open_block_id, places);
  group.ProcessSourceResponse(source_respose);

  auto builder = Render(group);
  auto result = builder.As<std::vector<::handlers::TurboButton>>();

  ASSERT_EQ(result.size(), 2);
  const auto& button = result.front();
  ASSERT_EQ(button.name, places.front().name);

  const auto& show_more_button = result.back();
  ASSERT_EQ(show_more_button.name, "more");
  ASSERT_EQ(show_more_button.app_link,
            fmt::format("eda.yandex://collections/{}", kCollectionSlug));
  ASSERT_EQ(show_more_button.icon, show_more.icon_url);
  ASSERT_FALSE(show_more_button.description.has_value());
}

TEST(CollectionButtonGroup, NothingToShowMore) {
  // Проверяет кейс, когда кнопку еще показывать надо, но там показывать нечего,
  // поэтому она не показывается
  ShowMore show_more{};
  show_more.icon_url = "show_more/icon";
  const size_t kShowButtons = 2;
  auto group = MakeCollectionButtonGroup(kShowButtons, show_more);

  sources::DataSourceParams source_params;
  group.FillSourceRequestParams(source_params);
  const auto open_block_id =
      fmt::format("btn_collection_{}_open", kCollectionSlug);

  std::vector<Place> places;
  const size_t kPlacesCount = 2;
  for (size_t i = 0; i < kPlacesCount; i++) {
    auto& place = places.emplace_back();
    place.name = fmt::format("place_{}", i);
  }
  auto source_respose = GetDataSourceResponse(open_block_id, places);
  group.ProcessSourceResponse(source_respose);

  auto builder = Render(group);
  auto result = builder.As<std::vector<::handlers::TurboButton>>();

  ASSERT_EQ(result.size(), 2);
  const auto& button = result.front();
  ASSERT_EQ(button.name, places.front().name);

  const auto& another_button = result.back();
  ASSERT_EQ(another_button.name, places.back().name);
}

TEST(CollectionButtonGroup, CollapseShowMore) {
  // Проверяет что если в коллекции остался один рест
  // он будет показан вместо кнопки "еще"
  ShowMore show_more{};
  show_more.icon_url = "show_more/icon";
  const size_t kShowButtons = 1;
  auto group = MakeCollectionButtonGroup(kShowButtons, show_more);

  sources::DataSourceParams source_params;
  group.FillSourceRequestParams(source_params);
  const auto open_block_id =
      fmt::format("btn_collection_{}_open", kCollectionSlug);

  std::vector<Place> places;
  const size_t kPlacesCount = 2;
  for (size_t i = 0; i < kPlacesCount; i++) {
    auto& place = places.emplace_back();
    place.name = fmt::format("place_{}", i);
  }
  auto source_respose = GetDataSourceResponse(open_block_id, places);
  group.ProcessSourceResponse(source_respose);

  auto builder = Render(group);
  auto result = builder.As<std::vector<::handlers::TurboButton>>();

  ASSERT_EQ(result.size(), 2);
  const auto& button = result.front();
  ASSERT_EQ(button.name, places.front().name);

  const auto& another_button = result.back();
  ASSERT_EQ(another_button.name, places.back().name);
}

TEST(CollectionButtonGroup, CollapseShowMoreFromClosed) {
  // Проверяет что если в коллекции остался один рест
  // он будет показан вместо кнопки "еще"
  // но последний рест в блоке closed

  ShowMore show_more{};
  show_more.icon_url = "show_more/icon";
  const size_t kShowButtons = 3;
  auto group = MakeCollectionButtonGroup(kShowButtons, show_more);

  sources::DataSourceParams source_params;
  group.FillSourceRequestParams(source_params);
  const auto open_block_id =
      fmt::format("btn_collection_{}_open", kCollectionSlug);
  const auto closed_block_id =
      fmt::format("btn_collection_{}_closed", kCollectionSlug);

  using Catalog = eats_layout_constructor::sources::CatalogDataSource;
  auto catalog_response =
      std::make_shared<Catalog::Response>(Catalog::Response{});
  for (const auto& block_id : {open_block_id, closed_block_id}) {
    std::vector<sources::catalog::Place> catalog_places;
    const size_t kPlacesCount = 2;
    for (size_t i = 0; i < kPlacesCount; i++) {
      auto& catalog_place = catalog_places.emplace_back();
      Place place{};
      place.name = fmt::format("{}_{}", block_id, i);
      catalog_place = GetCatalogPlace(place);
    }
    catalog_response->blocks[block_id].places = std::move(catalog_places);
  }
  eats_layout_constructor::sources::DataSourceResponses response;
  response[Catalog::kName] = catalog_response;

  group.ProcessSourceResponse(response);

  auto builder = Render(group);
  auto result = builder.As<std::vector<::handlers::TurboButton>>();

  ASSERT_EQ(result.size(), 4);
  const auto& button = result.front();
  ASSERT_EQ(button.name, fmt::format("{}_{}", open_block_id, 0));

  const auto& another_button = result.back();
  ASSERT_EQ(another_button.name, fmt::format("{}_{}", closed_block_id, 1));
}

TEST(CollectionButtonGroup, ExtraBrands) {
  // Проверяем, что, если в параметры переданы extra brands, то
  // они будут запрошены у каталога и помещены как кнопки на первую позицию

  ShowMore show_more{};
  show_more.icon_url = "show_more/icon";
  const std::string kCollectionSlug = "my_collection";
  const size_t kShowButtons = 2;
  const std::vector<sources::BrandId> kExtraBrandIds = {sources::BrandId{1}};
  CollectionButtonGroupParams params{};
  params.collection_slug = kCollectionSlug;
  params.color_config = GetColorConfig();
  params.buttons_count = kShowButtons;
  params.extra_brands = kExtraBrandIds;
  params.show_more = show_more;
  CollectionButtonGroup group{params};

  sources::DataSourceParams source_params;
  group.FillSourceRequestParams(source_params);

  const auto extra_block_id =
      fmt::format("btn_collection_{}_extra_brands", kCollectionSlug);
  const auto open_block_id =
      fmt::format("btn_collection_{}_open", kCollectionSlug);

  using Catalog = eats_layout_constructor::sources::CatalogDataSource;
  auto catalog_response =
      std::make_shared<Catalog::Response>(Catalog::Response{});

  std::vector<std::string> expected_names;
  {
    Place place{};
    place.name = extra_block_id;
    expected_names.push_back(place.name);
    catalog_response->blocks[extra_block_id].places.push_back(
        GetCatalogPlace(place));
  }

  {
    std::vector<sources::catalog::Place> catalog_places;
    const size_t kPlacesCount = 2;
    for (size_t i = 0; i < kPlacesCount; i++) {
      Place place{};
      place.name = fmt::format("{}_{}", open_block_id, i);
      expected_names.push_back(place.name);
      catalog_places.push_back(GetCatalogPlace(place));
    }
    catalog_response->blocks[open_block_id].places = std::move(catalog_places);
  }

  eats_layout_constructor::sources::DataSourceResponses response;
  response[Catalog::kName] = catalog_response;
  group.ProcessSourceResponse(response);

  auto builder = Render(group);
  auto result = builder.As<std::vector<::handlers::TurboButton>>();

  // ASSERT_EQ(result.size(), expected_names.size());
  for (size_t i = 0; i < expected_names.size(); i++) {
    const auto& button = result[i];
    const auto& name = expected_names[i];
    ASSERT_EQ(button.name, name);
  }
}

TEST(CollectionButtonGroup, DeliveryFeatureMode) {
  // Проверяем, что, если в параметры переданы extra brands, то
  // они будут запрошены у каталога и помещены как кнопки на первую позицию

  const std::string kCollectionSlug = "my_collection";
  CollectionButtonGroupParams params{};
  params.collection_slug = kCollectionSlug;
  params.color_config = GetColorConfig();
  params.delivery_feature_mode =
      clients::catalog::BlockSpecDeliveryfeaturemode::kMax;
  CollectionButtonGroup group{params};

  sources::DataSourceParams source_params;
  group.FillSourceRequestParams(source_params);

  auto catalog_params =
      std::any_cast<eats_layout_constructor::sources::catalog::Params>(
          source_params["catalog"]);
  ASSERT_FALSE(catalog_params.blocks.empty());

  const auto open_block_id =
      fmt::format("btn_collection_{}_open", kCollectionSlug);
  const auto closed_block_id =
      fmt::format("btn_collection_{}_closed", kCollectionSlug);

  ASSERT_EQ(catalog_params.blocks.count(open_block_id), 1);
  ASSERT_EQ(catalog_params.blocks.count(closed_block_id), 1);

  auto open_block = catalog_params.blocks[open_block_id];
  ASSERT_EQ(open_block.delivery_feature_mode,
            params.delivery_feature_mode.value());

  auto closed_block = catalog_params.blocks[closed_block_id];
  ASSERT_EQ(closed_block.delivery_feature_mode,
            params.delivery_feature_mode.value());
}

class CollectionButtonGroupColors
    : public ::testing::TestWithParam<std::pair<bool, Colors>> {
 protected:
  std::pair<bool, Colors> test_case;
};

TEST_P(CollectionButtonGroupColors, Colors) {
  // Проверяет цвета описания
  // в зависимости от доступности рестов
  const std::string kCollectionSlug = "my_collection";
  CollectionButtonGroupParams params{};
  params.collection_slug = kCollectionSlug;
  params.color_config = GetColorConfig();
  params.buttons_count = 1;

  CollectionButtonGroup group{params};

  sources::DataSourceParams source_params;
  group.FillSourceRequestParams(source_params);
  const auto open_block_id =
      fmt::format("btn_collection_{}_open", kCollectionSlug);

  auto [available, colors] = GetParam();

  Place place{};
  place.is_avaialbe_now = available;
  auto source_respose = GetDataSourceResponse(open_block_id, {place});
  group.ProcessSourceResponse(source_respose);

  auto builder = Render(group);
  auto result = builder.As<std::vector<::handlers::TurboButton>>();

  ASSERT_EQ(result.size(), 1);
  const auto& button = result.front();
  ASSERT_EQ(button.name, place.name);
  AssertColor(button.description.value().color, colors.light, colors.dark);
}

INSTANTIATE_TEST_SUITE_P(
    CollectionButtonGroup, CollectionButtonGroupColors,
    ::testing::Values(std::make_pair(false, GetColorConfig().eta_colors.closed),
                      std::make_pair(true, GetColorConfig().eta_colors.open)));

}  // namespace eats_layout_constructor::widgets::turbo_buttons::tests
