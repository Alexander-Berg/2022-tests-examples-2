#include "places_multiline.hpp"

#include <fmt/format.h>
#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/logging/log.hpp>

#include <models/constructor/db_model.hpp>
#include <sources/catalog/catalog_data_source.hpp>
#include <widgets/places_multiline/utils.hpp>

#include <widgets/places_multiline/factory.hpp>

namespace {
using Response = eats_layout_constructor::sources::DataSourceResponses;
using FilterType =
    eats_layout_constructor::widgets::mini_places_carousel::Placefiltertype;

namespace sources = eats_layout_constructor::sources;
namespace catalog = sources::catalog;

const std::string kBlockId = "any_no_filters_shop_sort_default";

formats::json::Value GetWidgetData(
    const std::string& id, const std::vector<int>& brands_order,
    const std::vector<int>& supported_brands,
    std::optional<std::string> title_size, std::optional<int> min_count,
    std::optional<int> limit, std::optional<FilterType> filter_type,
    const std::optional<std::string>& image_source,
    const std::optional<std::string>& delivery_feature_mode) {
  formats::json::ValueBuilder widget;
  widget["meta"] = formats::json::Type::kObject;
  widget["id"] = id;
  widget["payload"]["title"] = "title";
  widget["type"] = "places_multiline";
  widget["meta"]["brands_order"] = brands_order;
  widget["meta"]["brand_ids"] = supported_brands;
  if (min_count.has_value()) {
    widget["meta"]["min_count"] = *min_count;
  }
  if (limit.has_value()) {
    widget["meta"]["limit"] = *limit;
  }
  if (filter_type.has_value()) {
    widget["meta"]["place_filter_type"] = *filter_type;
  }
  if (image_source.has_value()) {
    widget["meta"]["image_source"] = image_source.value();
  }
  if (delivery_feature_mode.has_value()) {
    widget["meta"]["delivery_feature_mode"] = delivery_feature_mode.value();
  }
  if (title_size.has_value()) {
    widget["meta"]["title_size"] = title_size.value();
  }
  return widget.ExtractValue();
}

std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> GetWidget(
    const std::string& id, const std::vector<int>& brands_order,
    const std::vector<int>& supported_brands,
    std::optional<std::string> title_size = std::nullopt,
    std::optional<int> min_count = std::nullopt,
    std::optional<int> limit = std::nullopt,
    std::optional<FilterType> filter_type = FilterType::kAny,
    const std::optional<std::string>& image_source = std::nullopt,
    const std::optional<std::string>& delivery_feature_mode = std::nullopt) {
  const auto widget_data =
      GetWidgetData(id, brands_order, supported_brands, title_size, min_count,
                    limit, filter_type, image_source, delivery_feature_mode);
  return eats_layout_constructor::widgets::places_multiline::
      PlacesMultilineFactory(
          eats_layout_constructor::models::constructor::WidgetTemplateName{},
          eats_layout_constructor::models::constructor::Meta{
              widget_data["meta"]},
          eats_layout_constructor::models::constructor::Payload{
              widget_data["payload"]},
          {}, widget_data["id"].As<std::string>());
}

formats::json::Value GetTags(size_t count) {
  if (count == 0) {
    return {};
  }

  formats::json::ValueBuilder tags;
  tags = formats::json::Type::kArray;
  tags.Resize(count);

  for (size_t i = 0; i < count; ++i) {
    tags[i]["text"]["text"] = std::to_string(i);
    tags[i]["text"]["color"] = formats::json::Type::kArray;
    tags[i]["text"]["color"].Resize(2);
    tags[i]["text"]["color"][0]["theme"] = "light";
    tags[i]["text"]["color"][0]["value"] = "#ffffff";
    tags[i]["text"]["color"][1]["theme"] = "dark";
    tags[i]["text"]["color"][1]["value"] = "#ffffff";
    tags[i]["background"].Resize(2);
    tags[i]["background"][0]["theme"] = "light";
    tags[i]["background"][0]["value"] = "#ffffff";
    tags[i]["background"][1]["theme"] = "dark";
    tags[i]["background"][1]["value"] = "#ffffff";
  }

  return tags.ExtractValue();
}

Response GetSource(int places_count) {
  using Catalog = eats_layout_constructor::sources::CatalogDataSource;
  Response response;
  std::vector<catalog::Place> places;
  places.reserve(places_count);
  for (auto i = 0; i < places_count; ++i) {
    formats::json::ValueBuilder place;
    place["slug"] = fmt::format("slug{}", i + 1);
    place["name"] = fmt::format("name{}", i + 1);
    place["brand"]["slug"] = fmt::format("brand_slug{}", i + 1);
    place["brand"]["name"] = fmt::format("brand_name{}", i + 1);
    auto const tags = GetTags(i);
    if (tags.IsArray()) {
      place["data"]["features"]["tags"] = tags;
    }
    places.push_back(catalog::Place{
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

TEST(PlacesMultiline, MainFlow) {
  {
    auto places_multiline = GetWidget("morda", {2, 3}, {});
    formats::json::ValueBuilder response;
    auto source = GetSource(4);

    EXPECT_FALSE(places_multiline->HasData());
    places_multiline->FilterSourceResponse(source);
    EXPECT_FALSE(places_multiline->HasData());
  }

  auto places_multiline = GetWidget("morda", {2, 3}, {2, 3}, "medium");
  formats::json::ValueBuilder response;
  auto source = GetSource(4);

  EXPECT_FALSE(places_multiline->HasData());
  places_multiline->FilterSourceResponse(source);
  EXPECT_TRUE(places_multiline->HasData());

  places_multiline->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  {
    auto layout = json_response["layout"];
    EXPECT_EQ(layout.GetSize(), 1);
    EXPECT_EQ(layout[0]["type"].As<std::string>(), "places_multiline");
  }
  uint8_t total_row_weight = 0;
  {
    auto places_multiline = json_response["data"]["places_multiline"];
    EXPECT_EQ(places_multiline.GetSize(), 1);
    EXPECT_EQ(places_multiline[0]["payload"]["places"].GetSize(), 2);
    EXPECT_EQ(places_multiline[0]["id"].As<std::string>(), "morda");

    EXPECT_TRUE(places_multiline[0]["payload"].HasMember("total_columns_hint"));
    total_row_weight =
        places_multiline[0]["payload"]["total_columns_hint"].As<uint8_t>();
    EXPECT_TRUE(places_multiline[0]["payload"].HasMember("title_size"));
    EXPECT_EQ(places_multiline[0]["payload"]["title_size"].As<std::string>(),
              "medium");
  }
  EXPECT_NE(total_row_weight, 0);

  uint8_t sum_of_items = 0;
  {
    std::vector<std::string> order{"slug2", "slug3", "slug1", "slug4"};

    auto places =
        json_response["data"]["places_multiline"][0]["payload"]["places"];

    for (size_t i = 0; i < places.GetSize(); i++) {
      EXPECT_TRUE(places[i].HasMember("layout_hints"));
      const auto& layout_hints = places[i]["layout_hints"];
      EXPECT_TRUE(layout_hints.HasMember("column_width_hint"));
      sum_of_items += layout_hints["column_width_hint"].As<uint8_t>();

      const auto& place = places[i]["item"];
      EXPECT_TRUE(place.HasMember("slug"));
      EXPECT_TRUE(place.HasMember("name"));
      EXPECT_TRUE(place.HasMember("brand"));

      EXPECT_EQ(place["slug"].As<std::string>(), order[i]);
    }
  }

  EXPECT_EQ(total_row_weight, sum_of_items);
}

TEST(PlacesMultiline, GetItemWeight) {
  using eats_layout_constructor::widgets::places_multiline::GetItemWeight;

  EXPECT_EQ(GetItemWeight(0, 1), 6);

  EXPECT_EQ(GetItemWeight(0, 2), 3);
  EXPECT_EQ(GetItemWeight(1, 2), 3);

  EXPECT_EQ(GetItemWeight(0, 3), 2);
  EXPECT_EQ(GetItemWeight(1, 3), 2);
  EXPECT_EQ(GetItemWeight(2, 3), 2);

  EXPECT_EQ(GetItemWeight(0, 4), 3);
  EXPECT_EQ(GetItemWeight(1, 4), 3);
  EXPECT_EQ(GetItemWeight(2, 4), 3);
  EXPECT_EQ(GetItemWeight(3, 4), 3);

  EXPECT_EQ(GetItemWeight(0, 5), 3);
  EXPECT_EQ(GetItemWeight(1, 5), 3);
  EXPECT_EQ(GetItemWeight(2, 5), 2);
  EXPECT_EQ(GetItemWeight(3, 5), 2);
  EXPECT_EQ(GetItemWeight(4, 5), 2);

  EXPECT_EQ(GetItemWeight(0, 6), 2);
  EXPECT_EQ(GetItemWeight(1, 6), 2);
  EXPECT_EQ(GetItemWeight(2, 6), 2);
  EXPECT_EQ(GetItemWeight(3, 6), 2);
  EXPECT_EQ(GetItemWeight(4, 6), 2);
  EXPECT_EQ(GetItemWeight(5, 6), 2);

  EXPECT_EQ(GetItemWeight(0, 7), 3);
  EXPECT_EQ(GetItemWeight(1, 7), 3);
  EXPECT_EQ(GetItemWeight(2, 7), 3);
  EXPECT_EQ(GetItemWeight(3, 7), 3);
  EXPECT_EQ(GetItemWeight(4, 7), 2);
  EXPECT_EQ(GetItemWeight(5, 7), 2);
  EXPECT_EQ(GetItemWeight(6, 7), 2);

  EXPECT_EQ(GetItemWeight(0, 8), 3);
  EXPECT_EQ(GetItemWeight(1, 8), 3);
  EXPECT_EQ(GetItemWeight(2, 8), 2);
  EXPECT_EQ(GetItemWeight(3, 8), 2);
  EXPECT_EQ(GetItemWeight(4, 8), 2);
  EXPECT_EQ(GetItemWeight(5, 8), 2);
  EXPECT_EQ(GetItemWeight(6, 8), 2);
  EXPECT_EQ(GetItemWeight(7, 8), 2);

  EXPECT_EQ(GetItemWeight(0, 9), 2);
  EXPECT_EQ(GetItemWeight(1, 9), 2);
  EXPECT_EQ(GetItemWeight(2, 9), 2);
  EXPECT_EQ(GetItemWeight(3, 9), 2);
  EXPECT_EQ(GetItemWeight(4, 9), 2);
  EXPECT_EQ(GetItemWeight(5, 9), 2);
  EXPECT_EQ(GetItemWeight(6, 9), 2);
  EXPECT_EQ(GetItemWeight(7, 9), 2);
  EXPECT_EQ(GetItemWeight(8, 9), 2);

  EXPECT_EQ(GetItemWeight(0, 10), 3);
  EXPECT_EQ(GetItemWeight(1, 10), 3);
  EXPECT_EQ(GetItemWeight(2, 10), 3);
  EXPECT_EQ(GetItemWeight(3, 10), 3);
  EXPECT_EQ(GetItemWeight(4, 10), 2);
  EXPECT_EQ(GetItemWeight(5, 10), 2);
  EXPECT_EQ(GetItemWeight(6, 10), 2);
  EXPECT_EQ(GetItemWeight(7, 10), 2);
  EXPECT_EQ(GetItemWeight(8, 10), 2);
  EXPECT_EQ(GetItemWeight(9, 10), 2);

  EXPECT_EQ(GetItemWeight(0, 11), 3);
  EXPECT_EQ(GetItemWeight(1, 11), 3);
  EXPECT_EQ(GetItemWeight(2, 11), 2);
  EXPECT_EQ(GetItemWeight(3, 11), 2);
  EXPECT_EQ(GetItemWeight(4, 11), 2);
  EXPECT_EQ(GetItemWeight(5, 11), 2);
  EXPECT_EQ(GetItemWeight(6, 11), 2);
  EXPECT_EQ(GetItemWeight(7, 11), 2);
  EXPECT_EQ(GetItemWeight(8, 11), 2);
  EXPECT_EQ(GetItemWeight(9, 11), 2);
  EXPECT_EQ(GetItemWeight(10, 11), 2);

  EXPECT_EQ(GetItemWeight(0, 12), 2);
  EXPECT_EQ(GetItemWeight(1, 12), 2);
  EXPECT_EQ(GetItemWeight(2, 12), 2);
  EXPECT_EQ(GetItemWeight(3, 12), 2);
  EXPECT_EQ(GetItemWeight(4, 12), 2);
  EXPECT_EQ(GetItemWeight(5, 12), 2);
  EXPECT_EQ(GetItemWeight(6, 12), 2);
  EXPECT_EQ(GetItemWeight(7, 12), 2);
  EXPECT_EQ(GetItemWeight(8, 12), 2);
  EXPECT_EQ(GetItemWeight(9, 12), 2);
  EXPECT_EQ(GetItemWeight(10, 12), 2);
  EXPECT_EQ(GetItemWeight(11, 12), 2);

  EXPECT_EQ(GetItemWeight(0, 13), 3);
  EXPECT_EQ(GetItemWeight(1, 13), 3);
  EXPECT_EQ(GetItemWeight(2, 13), 3);
  EXPECT_EQ(GetItemWeight(3, 13), 3);
  EXPECT_EQ(GetItemWeight(4, 13), 2);
  EXPECT_EQ(GetItemWeight(5, 13), 2);
  EXPECT_EQ(GetItemWeight(6, 13), 2);
  EXPECT_EQ(GetItemWeight(7, 13), 2);
  EXPECT_EQ(GetItemWeight(8, 13), 2);
  EXPECT_EQ(GetItemWeight(9, 13), 2);
  EXPECT_EQ(GetItemWeight(10, 13), 2);
  EXPECT_EQ(GetItemWeight(11, 13), 2);
  EXPECT_EQ(GetItemWeight(12, 13), 2);
}

TEST(PlacesMultiline, Tags) {
  auto places_multiline = GetWidget("tags_test", {1, 2, 3}, {1, 2, 3});
  formats::json::ValueBuilder response;
  auto source = GetSource(4);

  EXPECT_FALSE(places_multiline->HasData());
  places_multiline->FilterSourceResponse(source);
  EXPECT_TRUE(places_multiline->HasData());

  places_multiline->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  auto places =
      json_response["data"]["places_multiline"][0]["payload"]["places"];

  EXPECT_EQ(places.GetSize(), 3);
  EXPECT_TRUE(places[0]["item"]["data"]["features"]["tags"].IsMissing());

  for (size_t i = 1; i < places.GetSize(); ++i) {
    EXPECT_TRUE(places[i]["item"]["data"]["features"]["tags"].IsArray());

    auto tags = places[i]["item"]["data"]["features"]["tags"];
    EXPECT_EQ(tags.GetSize(), i);

    for (size_t j = 0; j < i; ++j) {
      EXPECT_EQ(tags[j]["text"]["text"].As<std::string>(), std::to_string(j));
    }
  }
}
