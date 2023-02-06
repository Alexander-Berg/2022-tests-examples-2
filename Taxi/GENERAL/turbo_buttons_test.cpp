#include <gtest/gtest.h>

#include "turbo_buttons.hpp"

#include <sources/catalog/catalog_data_source.hpp>

#include <widgets/turbo_buttons/factory.hpp>

namespace eats_layout_constructor::widgets {

namespace {

using Response = eats_layout_constructor::sources::DataSourceResponses;

constexpr size_t kDrawAsMiniCarouselTreshold = 2;
const std::string kBlockId = "btn_collection_shops_open";

std::shared_ptr<LayoutWidget> GetWidget() {
  turbo_buttons::WidgetMeta meta;
  auto& collection_group = meta.collection_groups.emplace().emplace_back();
  collection_group.slug = "shops";
  collection_group.buttons_count = 10;
  auto& layout = meta.layout.emplace_back();
  layout.slug = "shops";
  layout.type = turbo_buttons::GroupType::kCollection;
  meta.draw_as_mini_carousel_treshold = kDrawAsMiniCarouselTreshold;

  formats::json::ValueBuilder builder{std::move(meta)};
  return turbo_buttons::TurboButtonsFactory(
      eats_layout_constructor::models::constructor::WidgetTemplateName{},
      models::constructor::Meta{builder.ExtractValue()},
      models::constructor::Payload{}, {}, "id");
}

Response GetSource(int places_count) {
  using Catalog = sources::CatalogDataSource;
  Response response;
  std::vector<sources::catalog::Place> places;
  places.reserve(places_count);
  for (auto i = 0; i < places_count; ++i) {
    formats::json::ValueBuilder place;
    place["slug"] = fmt::format("slug{}", i + 1);
    place["name"] = fmt::format("name{}", i + 1);
    place["brand"]["slug"] = fmt::format("brand_slug{}", i + 1);
    place["brand"]["name"] = fmt::format("brand_name{}", i + 1);
    place["brand"]["business"] = "shop";
    place["availability"]["is_available"] = true;
    place["data"]["features"] = formats::common::Type::kObject;
    place["context"] = formats::common::Type::kObject;
    place["analytics"] = "random_string";
    places.push_back(sources::catalog::Place{
        {sources::PlaceId(i + 1), sources::BrandId(i + 1), std::nullopt},
        place.ExtractValue()});
  }
  auto catalog_response =
      std::make_shared<Catalog::Response>(Catalog::Response{});
  catalog_response->blocks[kBlockId].places = places;
  response[Catalog::kName] = catalog_response;

  return response;
}

}  // namespace

TEST(TurboButtons, RenderAsButtons) {
  const int kPlacesCount = 5;
  auto widget = GetWidget();
  sources::DataSourceParams source_params;
  widget->FillSourceRequestParams(source_params);
  auto source = GetSource(kPlacesCount);

  EXPECT_FALSE(widget->HasData());
  EXPECT_FALSE(widget->HasPlaces());
  widget->FilterSourceResponse(source);
  EXPECT_TRUE(widget->HasData());
  EXPECT_TRUE(widget->HasPlaces());

  formats::json::ValueBuilder response{formats::common::Type::kObject};
  widget->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  {
    auto layout = json_response["layout"];
    ASSERT_EQ(layout.GetSize(), 1);
    ASSERT_EQ(layout[0]["type"].As<std::string>(), "turbo_buttons");
  }
  {
    auto turbo_buttons = json_response["data"]["turbo_buttons"];
    ASSERT_EQ(turbo_buttons.GetSize(), 1);
    ASSERT_EQ(turbo_buttons[0]["payload"]["buttons"].GetSize(), kPlacesCount);
  }
}

TEST(TurboButtons, RenderAsMiniPlacesCarousel) {
  const int kPlacesCount = 2;
  auto widget = GetWidget();
  sources::DataSourceParams source_params;
  widget->FillSourceRequestParams(source_params);
  auto source = GetSource(kPlacesCount);

  EXPECT_FALSE(widget->HasData());
  EXPECT_FALSE(widget->HasPlaces());
  widget->FilterSourceResponse(source);
  EXPECT_TRUE(widget->HasData());
  EXPECT_TRUE(widget->HasPlaces());

  formats::json::ValueBuilder response{formats::common::Type::kObject};
  widget->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  {
    auto layout = json_response["layout"];
    ASSERT_EQ(layout.GetSize(), 1);
    ASSERT_EQ(layout[0]["type"].As<std::string>(), "mini_places_carousel");
  }
  {
    auto turbo_buttons = json_response["data"]["mini_places_carousels"];
    ASSERT_EQ(turbo_buttons.GetSize(), 1);
    auto places = turbo_buttons[0]["payload"]["places"];
    ASSERT_EQ(places.GetSize(), kPlacesCount);
    for (const auto& place : places) {
      auto place_context = place["context"];
      ASSERT_TRUE(place_context.IsString());
      ASSERT_FALSE(place_context.As<std::string>().empty());
    }
  }
}

}  // namespace eats_layout_constructor::widgets
