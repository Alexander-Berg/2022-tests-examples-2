#include "places_brand_carousel.hpp"

#include <fmt/format.h>
#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>

#include <models/constructor/db_model.hpp>
#include <sources/catalog/catalog_data_source.hpp>
#include <widgets/places_brand_carousel/factory.hpp>

namespace {
using Response = eats_layout_constructor::sources::DataSourceResponses;
namespace sources = eats_layout_constructor::sources;
namespace catalog = sources::catalog;

formats::json::Value GetWidgetData(const std::string& id,
                                   const std::string& title,
                                   const std::vector<int>& brands,
                                   std::optional<int> min_count,
                                   std::optional<int> limit,
                                   bool ignore_brands_order) {
  formats::json::ValueBuilder widget;
  widget["meta"] =
      formats::json::ValueBuilder{formats::json::Type::kObject}.ExtractValue();
  widget["id"] = id;
  widget["payload"]["title"] = title;
  widget["type"] = "places_carousel";
  widget["meta"]["brands"] = brands;
  widget["meta"]["ignore_brands_order"] = ignore_brands_order;
  if (min_count.has_value()) {
    widget["meta"]["min_count"] = *min_count;
  }
  if (limit.has_value()) {
    widget["meta"]["limit"] = *limit;
  }
  return widget.ExtractValue();
}

std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> GetWidget(
    const std::string& id, const std::string& title,
    const std::vector<int>& brands, std::optional<int> min_count = std::nullopt,
    std::optional<int> limit = std::nullopt, bool ignore_brands_order = false) {
  const auto widget_data =
      GetWidgetData(id, title, brands, min_count, limit, ignore_brands_order);
  return eats_layout_constructor::widgets::places_brand_carousel::
      PlacesBrandCarouselFactory(
          eats_layout_constructor::models::constructor::WidgetTemplateName{},
          eats_layout_constructor::models::constructor::Meta{
              widget_data["meta"]},
          eats_layout_constructor::models::constructor::Payload{
              widget_data["payload"]},
          {}, widget_data["id"].As<std::string>());
}

Response GetSource(int places_count) {
  using Catalog = eats_layout_constructor::sources::CatalogDataSource;
  Response response;
  std::vector<catalog::Place> places;
  places.reserve(places_count);
  for (auto i = 0; i < places_count; ++i) {
    formats::json::ValueBuilder place;
    place["id"] = fmt::format("id{}", i + 1);
    place["name"] = fmt::format("name{}", i + 1);
    places.push_back(
        catalog::Place{{sources::PlaceId(i), sources::BrandId(i), std::nullopt},
                       place.ExtractValue()});
  }
  auto catalog_response =
      std::make_shared<Catalog::Response>(Catalog::Response{});
  catalog_response->blocks["advertising"].places = places;
  response[Catalog::kName] = catalog_response;

  return response;
}

}  // namespace

TEST(PlacesBrandCarousel, MainFlow) {
  namespace widgets = eats_layout_constructor::widgets;
  auto places_carousel = GetWidget("advertising", "Рекламная пауза", {3, 2});
  formats::json::ValueBuilder response;
  auto source = GetSource(4);

  EXPECT_FALSE(places_carousel->HasData());
  places_carousel->FilterSourceResponse(source);
  EXPECT_TRUE(places_carousel->HasData());

  places_carousel->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["layout"][0]["type"].As<std::string>(),
            "places_carousel");
  EXPECT_EQ(json_response["data"]["places_carousels"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["places_carousels"][0]["payload"]["places"]
                .GetSize(),
            2);
  const auto& places =
      json_response["data"]["places_carousels"][0]["payload"]["places"];

  size_t i = 0;
  for (int id : std::vector<int>{4, 3}) {
    EXPECT_EQ(places[i]["id"].As<std::string>(), fmt::format("id{}", id));
    EXPECT_EQ(places[i]["name"].As<std::string>(), fmt::format("name{}", id));
    ++i;
  }
  EXPECT_EQ(
      json_response["data"]["places_carousels"][0]["id"].As<std::string>(),
      "advertising");
}

TEST(PlacesBrandCarousel, MainFlowIgnoreOrder) {
  namespace widgets = eats_layout_constructor::widgets;
  auto places_carousel = GetWidget("advertising", "Рекламная пауза", {0, 1, 3},
                                   std::nullopt, std::nullopt, true);
  formats::json::ValueBuilder response;
  auto source = GetSource(3);

  EXPECT_FALSE(places_carousel->HasData());
  places_carousel->FilterSourceResponse(source);
  EXPECT_TRUE(places_carousel->HasData());

  places_carousel->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["layout"][0]["type"].As<std::string>(),
            "places_carousel");
  EXPECT_EQ(json_response["data"]["places_carousels"].GetSize(), 1);

  const auto& places =
      json_response["data"]["places_carousels"][0]["payload"]["places"];
  EXPECT_EQ(places.GetSize(), 3);

  size_t i = 0;
  for (int id : std::vector<int>{1, 2, 3}) {
    EXPECT_EQ(places[i]["id"].As<std::string>(), fmt::format("id{}", id));
    EXPECT_EQ(places[i]["name"].As<std::string>(), fmt::format("name{}", id));
    ++i;
  }
  EXPECT_EQ(
      json_response["data"]["places_carousels"][0]["id"].As<std::string>(),
      "advertising");
}

TEST(PlacesBrandCarousel, ContainLessThanMin) {
  namespace widgets = eats_layout_constructor::widgets;
  auto places_carousel = GetWidget("advertising", "Рекламная пауза", {1, 2}, 3);

  formats::json::ValueBuilder response;
  auto source = GetSource(4);

  EXPECT_FALSE(places_carousel->HasData());
  places_carousel->FilterSourceResponse(source);
  EXPECT_FALSE(places_carousel->HasData());

  places_carousel->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_FALSE(json_response.HasMember("layout"));
  EXPECT_FALSE(json_response.HasMember("data"));
}

TEST(PlacesBrandCarousel, ContainMoreThanMax) {
  namespace widgets = eats_layout_constructor::widgets;
  auto places_carousel =
      GetWidget("advertising", "Рекламная пауза", {2, 3, 4, 5, 6, 7, 1}, 3, 5);

  formats::json::ValueBuilder response;
  auto source = GetSource(7);

  EXPECT_FALSE(places_carousel->HasData());
  places_carousel->FilterSourceResponse(source);
  EXPECT_TRUE(places_carousel->HasData());

  places_carousel->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["data"]["places_carousels"][0]["payload"]["places"]
                .GetSize(),
            5);
}

TEST(PlacesBrandCarousel, RequestParams) {
  namespace widgets = eats_layout_constructor::widgets;
  auto places_carousel = GetWidget("advertising", "Рекламная пауза", {});

  eats_layout_constructor::sources::DataSourceParams params;
  places_carousel->FillSourceRequestParams(params);

  EXPECT_NE(params.find("catalog"), params.end());
  auto catalog_params = std::any_cast<catalog::Params>(params["catalog"]);
  EXPECT_EQ(catalog_params.blocks.size(), 1);
  EXPECT_EQ(catalog_params.blocks.count("advertising"), 1);
}
