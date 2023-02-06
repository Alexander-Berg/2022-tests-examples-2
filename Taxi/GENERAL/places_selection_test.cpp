#include "places_selection.hpp"

#include <fmt/format.h>
#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>

#include <models/constructor/db_model.hpp>
#include <sources/catalog/catalog_data_source.hpp>
#include <widgets/places_selection/factory.hpp>

namespace {

using Response = eats_layout_constructor::sources::DataSourceResponses;
namespace sources = eats_layout_constructor::sources;
namespace catalog = sources::catalog;

struct WidgetConfig {
  std::string id;
  std::string title;
  std::string place_filter_type;
  std::string selection;
  std::string output_type = "carousel";
  std::optional<int> min_count = std::nullopt;
  std::optional<int> limit = std::nullopt;
  std::optional<std::unordered_set<int>> exclude_brands = std::nullopt;
};

formats::json::Value GetWidgetData(const WidgetConfig& conf) {
  formats::json::ValueBuilder widget;
  widget["meta"] =
      formats::json::ValueBuilder{formats::json::Type::kObject}.ExtractValue();
  widget["id"] = conf.id;
  widget["payload"]["title"] = conf.title;
  widget["type"] = "places_selection";
  widget["meta"]["place_filter_type"] = conf.place_filter_type;
  widget["meta"]["selection"] = conf.selection;
  widget["meta"]["output_type"] = conf.output_type;
  if (conf.min_count.has_value()) {
    widget["meta"]["min_count"] = *conf.min_count;
  }
  if (conf.limit.has_value()) {
    widget["meta"]["limit"] = *conf.limit;
  }

  if (conf.exclude_brands.has_value()) {
    widget["meta"]["exclude_brands"] = *conf.exclude_brands;
  }
  return widget.ExtractValue();
}

std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> GetWidget(
    const WidgetConfig& conf) {
  const auto widget_data = GetWidgetData(conf);
  return eats_layout_constructor::widgets::places_selection::
      PlacesSelectionFactory(
          eats_layout_constructor::models::constructor::WidgetTemplateName{},
          eats_layout_constructor::models::constructor::Meta{
              widget_data["meta"]},
          eats_layout_constructor::models::constructor::Payload{
              widget_data["payload"]},
          {}, widget_data["id"].As<std::string>());
}

Response GetSource(const std::string& block_id, const int places_count) {
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
  catalog_response->blocks[block_id].places = places;
  response[Catalog::kName] = catalog_response;

  return response;
}

}  // namespace

TEST(PlacesSlection, Simple) {
  namespace widgets = eats_layout_constructor::widgets;
  auto places_selection = GetWidget({
      "widget-id",      // id
      "Вы заказывали",  // title
      "any",            // place_filter_type
      "history_order",  // selection
      "list"            // output_type
  });
  formats::json::ValueBuilder response;
  auto source = GetSource("any_history_order", 4);

  EXPECT_FALSE(places_selection->HasData());
  places_selection->FilterSourceResponse(source);
  EXPECT_TRUE(places_selection->HasData());

  places_selection->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["places_lists"].GetSize(), 1);
  EXPECT_EQ(
      json_response["data"]["places_lists"][0]["payload"]["places"].GetSize(),
      4);
  EXPECT_EQ(json_response["data"]["places_lists"][0]["id"].As<std::string>(),
            "widget-id");
}

TEST(PlacesSelection, ContainLessThanMin) {
  namespace widgets = eats_layout_constructor::widgets;

  auto places_selection = GetWidget({
      "widget-id",      // id
      "Вы заказывали",  // title
      "open",           // place_filter_type
      "history_order",  // selection
      "carousel",       // output_type
      10,               // min_count
  });

  formats::json::ValueBuilder response;
  auto source = GetSource("open_history_order", 4);

  EXPECT_FALSE(places_selection->HasData());
  places_selection->FilterSourceResponse(source);
  EXPECT_FALSE(places_selection->HasData());

  places_selection->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_FALSE(json_response.HasMember("layout"));
  EXPECT_FALSE(json_response.HasMember("data"));
}

TEST(PlacesSelection, ContainMoreThanMax) {
  namespace widgets = eats_layout_constructor::widgets;
  auto places_selection = GetWidget({
      "widget-id",      // id
      "",               // title
      "any",            // place_filter_type
      "history_order",  // selection
      "carousel",       // output_type
      3,                // min_count
      5,                // limit
  });

  formats::json::ValueBuilder response;
  auto source = GetSource("any_history_order", 7);

  EXPECT_FALSE(places_selection->HasData());
  places_selection->FilterSourceResponse(source);
  EXPECT_TRUE(places_selection->HasData());

  places_selection->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["data"]["places_carousels"][0]["payload"]["places"]
                .GetSize(),
            5);
}

TEST(PlacesSelection, FilterByBrandId) {
  namespace widgets = eats_layout_constructor::widgets;
  std::unordered_set<int> brands{3, 4};
  auto places_selection = GetWidget({
      "widget-id",      // id
      "",               // title
      "open",           // place_filter_type
      "history_order",  // selection
      "list",           // output_type
      {},               // min_count
      {},               // limit
      brands,           // exclude_brands
  });

  formats::json::ValueBuilder response;
  auto source = GetSource("open_history_order", 4);

  EXPECT_FALSE(places_selection->HasData());
  places_selection->FilterSourceResponse(source);
  EXPECT_TRUE(places_selection->HasData());

  places_selection->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(
      json_response["data"]["places_lists"][0]["payload"]["places"].GetSize(),
      2);
  EXPECT_EQ(
      json_response["data"]["places_lists"][0]["payload"]["places"][0]["id"]
          .As<std::string>(),
      "id1");
  EXPECT_EQ(
      json_response["data"]["places_lists"][0]["payload"]["places"][1]["id"]
          .As<std::string>(),
      "id2");
}

TEST(PlacesSelection, RequestParams) {
  namespace widgets = eats_layout_constructor::widgets;
  auto places_selection = GetWidget({
      "widget-id",      // id
      "",               // title
      "open",           // place_filter_type
      "history_order",  // selection
      "list",           // output_type
      {},               // min_count
      {},               // limit
  });

  eats_layout_constructor::sources::DataSourceParams params;
  places_selection->FillSourceRequestParams(params);

  EXPECT_NE(params.find("catalog"), params.end());
  auto catalog_params = std::any_cast<catalog::Params>(params["catalog"]);
  EXPECT_EQ(catalog_params.blocks.size(), 1);
  EXPECT_EQ(catalog_params.blocks.count("open_history_order"), 1);
}
