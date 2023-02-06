#include "places_carousel.hpp"

#include <fmt/format.h>
#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>

#include <models/constructor/db_model.hpp>
#include <sources/catalog/catalog_data_source.hpp>
#include <widgets/places_carousel/factory.hpp>

namespace {
using Response = eats_layout_constructor::sources::DataSourceResponses;
namespace sources = eats_layout_constructor::sources;
namespace catalog = sources::catalog;

formats::json::Value GetWidgetData(
    const std::string& id, const std::string& title,
    const std::string& carousel, std::optional<int> min_count,
    std::optional<int> limit,
    const std::optional<std::unordered_set<int>>& exclude_brands) {
  formats::json::ValueBuilder widget;
  widget["meta"] =
      formats::json::ValueBuilder{formats::json::Type::kObject}.ExtractValue();
  widget["id"] = id;
  widget["payload"]["title"] = title;
  widget["type"] = "places_carousel";
  widget["meta"]["carousel"] = carousel;
  if (min_count.has_value()) {
    widget["meta"]["min_count"] = *min_count;
  }
  if (limit.has_value()) {
    widget["meta"]["limit"] = *limit;
  }

  if (exclude_brands.has_value()) {
    widget["meta"]["exclude_brands"] = *exclude_brands;
  }
  return widget.ExtractValue();
}

std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> GetWidget(
    const std::string& id, const std::string& title,
    const std::string& carousel, std::optional<int> min_count = std::nullopt,
    std::optional<int> limit = std::nullopt,
    const std::optional<std::unordered_set<int>>& exclude_brands =
        std::nullopt) {
  const auto widget_data =
      GetWidgetData(id, title, carousel, min_count, limit, exclude_brands);
  return eats_layout_constructor::widgets::places_carousel::
      PlacesCarouselFactory(
          eats_layout_constructor::models::constructor::WidgetTemplateName{},
          eats_layout_constructor::models::constructor::Meta{
              widget_data["meta"]},
          eats_layout_constructor::models::constructor::Payload{
              widget_data["payload"]},
          {}, widget_data["id"].As<std::string>());
}

Response GetSource(catalog::PlaceType carousel, int places_count) {
  using Catalog = eats_layout_constructor::sources::CatalogDataSource;
  Response response;
  std::vector<catalog::Place> places;
  places.reserve(places_count);
  for (auto i = 0; i < places_count; ++i) {
    formats::json::ValueBuilder place;
    place["id"] = fmt::format("id{}", i + 1);
    place["name"] = fmt::format("name{}", i + 1);
    places.push_back(catalog::Place{
        {sources::PlaceId(i), sources::BrandId(i + 1), std::nullopt},
        place.ExtractValue()});
  }
  auto catalog_response =
      std::make_shared<Catalog::Response>(Catalog::Response{});
  catalog_response->blocks[ToString(carousel)].places = places;
  response[Catalog::kName] = catalog_response;

  return response;
}

}  // namespace

TEST(PlacesCarousel, Carousel) {
  namespace widgets = eats_layout_constructor::widgets;
  auto places_carousel = GetWidget("carousel_promo", "Акции", "promo");
  formats::json::ValueBuilder response;
  auto source = GetSource(catalog::PlaceType::kPromo, 4);

  EXPECT_FALSE(places_carousel->HasData());
  places_carousel->FilterSourceResponse(source);
  EXPECT_TRUE(places_carousel->HasData());

  places_carousel->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["places_carousels"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["places_carousels"][0]["payload"]["places"]
                .GetSize(),
            4);
  EXPECT_EQ(
      json_response["data"]["places_carousels"][0]["id"].As<std::string>(),
      "carousel_promo");
}

TEST(PlacesCarousel, ContainLessThanMin) {
  namespace widgets = eats_layout_constructor::widgets;
  auto places_carousel = GetWidget("carousel_promo", "Акции", "promo", 10);

  formats::json::ValueBuilder response;
  auto source = GetSource(catalog::PlaceType::kPromo, 4);

  EXPECT_FALSE(places_carousel->HasData());
  places_carousel->FilterSourceResponse(source);
  EXPECT_FALSE(places_carousel->HasData());

  places_carousel->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_FALSE(json_response.HasMember("layout"));
  EXPECT_FALSE(json_response.HasMember("data"));
}

TEST(PlacesCarousel, ContainMoreThanMax) {
  namespace widgets = eats_layout_constructor::widgets;
  auto places_carousel = GetWidget("carousel_promo", "Акции", "promo", 3, 5);

  formats::json::ValueBuilder response;
  auto source = GetSource(catalog::PlaceType::kPromo, 7);

  EXPECT_FALSE(places_carousel->HasData());
  places_carousel->FilterSourceResponse(source);
  EXPECT_TRUE(places_carousel->HasData());

  places_carousel->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["data"]["places_carousels"][0]["payload"]["places"]
                .GetSize(),
            5);
}

TEST(PlacesCarousel, FilterByBrandId) {
  namespace widgets = eats_layout_constructor::widgets;
  std::unordered_set<int> brands{3, 4};
  auto places_carousel =
      GetWidget("carousel_promo", "Акции", "promo", {}, {}, brands);

  formats::json::ValueBuilder response;
  auto source = GetSource(catalog::PlaceType::kPromo, 4);

  EXPECT_FALSE(places_carousel->HasData());
  places_carousel->FilterSourceResponse(source);
  EXPECT_TRUE(places_carousel->HasData());

  places_carousel->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["data"]["places_carousels"][0]["payload"]["places"]
                .GetSize(),
            2);
  EXPECT_EQ(
      json_response["data"]["places_carousels"][0]["payload"]["places"][0]["id"]
          .As<std::string>(),
      "id1");
  EXPECT_EQ(
      json_response["data"]["places_carousels"][0]["payload"]["places"][1]["id"]
          .As<std::string>(),
      "id2");
}

TEST(PlacesCarousel, RequestParams) {
  namespace widgets = eats_layout_constructor::widgets;
  auto places_carousel = GetWidget("carousel_promo", "Акции", "promo");

  eats_layout_constructor::sources::DataSourceParams params;
  places_carousel->FillSourceRequestParams(params);

  EXPECT_NE(params.find("catalog"), params.end());
  auto catalog_params = std::any_cast<catalog::Params>(params["catalog"]);
  EXPECT_EQ(catalog_params.blocks.size(), 1);
  EXPECT_EQ(catalog_params.blocks.count("promo"), 1);
}
