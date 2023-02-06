#include "places_list.hpp"

#include <set>

#include <fmt/format.h>
#include <gtest/gtest.h>

#include <models/constructor/db_model.hpp>
#include <sources/catalog/catalog_data_source.hpp>
#include <userver/formats/json/serialize.hpp>
#include <widgets/places_list/factory.hpp>

namespace {
using Response = eats_layout_constructor::sources::DataSourceResponses;
namespace sources = eats_layout_constructor::sources;
namespace catalog = sources::catalog;

formats::json::Value GetWidgetData(
    const std::string& id, const std::string& title, std::optional<int> low,
    std::optional<int> high, const std::string& filter_type,
    const std::optional<std::set<int64_t>> exclude_brands) {
  formats::json::ValueBuilder widget;
  widget["meta"] =
      formats::json::ValueBuilder{formats::json::Type::kObject}.ExtractValue();
  widget["id"] = id;
  widget["payload"]["title"] = title;
  widget["meta"]["place_filter_type"] = filter_type;
  widget["type"] = "places_list";

  if (low.has_value()) {
    widget["meta"]["low"] = *low;
  }
  if (high.has_value()) {
    widget["meta"]["high"] = *high;
  }

  if (exclude_brands.has_value()) {
    widget["meta"]["exclude_brands"] = exclude_brands.value();
  }

  return widget.ExtractValue();
}

std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> GetWidget(
    const std::string& id, const std::string& title,
    std::optional<int> low = std::nullopt,
    std::optional<int> high = std::nullopt,
    const std::string& filter_type = "open",
    const std::optional<std::set<int64_t>> exclude_brands = std::nullopt) {
  const auto widget_data =
      GetWidgetData(id, title, low, high, filter_type, exclude_brands);
  return eats_layout_constructor::widgets::places_list::PlacesListFactory(
      eats_layout_constructor::models::constructor::WidgetTemplateName{},
      eats_layout_constructor::models::constructor::Meta{widget_data["meta"]},
      eats_layout_constructor::models::constructor::Payload{
          widget_data["payload"]},
      {}, widget_data["id"].As<std::string>());
}

Response GetSource(int places_count, bool is_closed = false) {
  using Catalog = eats_layout_constructor::sources::CatalogDataSource;
  Response response;
  std::vector<catalog::Place> places;
  places.reserve(places_count);
  for (auto i = 0; i < places_count; ++i) {
    formats::json::ValueBuilder place;
    place["id"] = fmt::format("id{}", i + 1);
    place["name"] = fmt::format("name{}", i + 1);
    places.push_back(catalog::Place{
        {sources::PlaceId(i + 1), sources::BrandId(i + 1), std::nullopt},
        place.ExtractValue()});
  }
  auto catalog_response =
      std::make_shared<Catalog::Response>(Catalog::Response{});
  catalog_response->blocks[is_closed ? "closed" : "open"].places = places;
  response[Catalog::kName] = catalog_response;

  return response;
}
}  // namespace

TEST(PlacesList, AllPlaces) {
  auto places_list = GetWidget("all_places", "Все рестораны");

  formats::json::ValueBuilder response;
  auto source = GetSource(2);

  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  places_list->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["places_lists"].GetSize(), 1);
  EXPECT_EQ(
      json_response["data"]["places_lists"][0]["payload"]["places"].GetSize(),
      2);
  EXPECT_EQ(json_response["data"]["places_lists"][0]["id"].As<std::string>(),
            "all_places");
}

TEST(PlacesList, FirstNPlaces) {
  auto places_list = GetWidget("first_n", "Три первых ресторана", 0, 3);
  formats::json::ValueBuilder response;
  auto source = GetSource(5);

  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  places_list->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  auto places = json_response["data"]["places_lists"][0]["payload"]["places"];
  EXPECT_EQ(places.GetSize(), 3);
  for (int i = 0; i < 3; ++i) {
    EXPECT_EQ(places[i]["id"].As<std::string>(), fmt::format("id{}", i + 1));
    EXPECT_EQ(places[i]["name"].As<std::string>(),
              fmt::format("name{}", i + 1));
  }
}

TEST(PlacesList, FirstPlacesNotMoreThanN) {
  auto places_list = GetWidget("first_n", "Три первых ресторана", 0, 3);

  formats::json::ValueBuilder response;
  auto source = GetSource(2);

  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  places_list->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  auto places = json_response["data"]["places_lists"][0]["payload"]["places"];
  EXPECT_EQ(places.GetSize(), 2);
  for (int i = 0; i < 2; ++i) {
    EXPECT_EQ(places[i]["id"].As<std::string>(), fmt::format("id{}", i + 1));
    EXPECT_EQ(places[i]["name"].As<std::string>(),
              fmt::format("name{}", i + 1));
  }
}

TEST(PlacesList, PlacesSlice) {
  auto places_list = GetWidget("part_n", "Два ресторана из середины", 2, 4);

  formats::json::ValueBuilder response;
  auto source = GetSource(5);

  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  places_list->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  auto places = json_response["data"]["places_lists"][0]["payload"]["places"];
  EXPECT_EQ(places.GetSize(), 2);
  for (int i = 0; i < 2; ++i) {
    EXPECT_EQ(places[i]["id"].As<std::string>(), fmt::format("id{}", i + 3));
    EXPECT_EQ(places[i]["name"].As<std::string>(),
              fmt::format("name{}", i + 3));
  }
}

TEST(PlacesList, PlacesSliceContainLess) {
  auto places_list = GetWidget("part_n", "Три ресторана из середины", 2, 5);

  formats::json::ValueBuilder response;
  auto source = GetSource(4);

  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  places_list->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  auto places = json_response["data"]["places_lists"][0]["payload"]["places"];
  EXPECT_EQ(places.GetSize(), 2);
  for (int i = 0; i < 2; ++i) {
    EXPECT_EQ(places[i]["id"].As<std::string>(), fmt::format("id{}", i + 3));
    EXPECT_EQ(places[i]["name"].As<std::string>(),
              fmt::format("name{}", i + 3));
  }
}

TEST(PlacesList, PlacesSliceExcludeBrandsInMiddle) {
  auto places_list = GetWidget("part_n", "Три ресторана из середины", 2, 8,
                               "open", std::set<int64_t>{4, 8});

  formats::json::ValueBuilder response;
  auto source = GetSource(10);

  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  places_list->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  auto places = json_response["data"]["places_lists"][0]["payload"]["places"];
  ASSERT_EQ(places.GetSize(),
            8 /* high */ - 2 /* low */ - 2 /* exclude_brands.size() */);

  size_t i = 0;
  for (int id : std::vector<int>{3, 5, 6, 7}) {
    EXPECT_EQ(places[i]["id"].As<std::string>(), fmt::format("id{}", id));
    EXPECT_EQ(places[i]["name"].As<std::string>(), fmt::format("name{}", id));
    ++i;
  }
}

TEST(PlacesList, PlacesExcludeBrands) {
  auto places_list =
      GetWidget("part_n", "Три ресторана из середины", std::nullopt,
                std::nullopt, "open", std::set<int64_t>{1});

  formats::json::ValueBuilder response;
  auto source = GetSource(2);

  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  places_list->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  auto places = json_response["data"]["places_lists"][0]["payload"]["places"];
  ASSERT_EQ(places.GetSize(), 1);

  size_t i = 0;
  for (int id : std::vector<int>{2}) {
    EXPECT_EQ(places[i]["id"].As<std::string>(), fmt::format("id{}", id));
    EXPECT_EQ(places[i]["name"].As<std::string>(), fmt::format("name{}", id));
    ++i;
  }
}

TEST(PlacesList, PlacesSliceEmpty) {
  auto places_list = GetWidget("part_n", "Три ресторана из середины", 3, 5);

  formats::json::ValueBuilder response;
  auto source = GetSource(3);

  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_FALSE(places_list->HasData());

  places_list->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  EXPECT_FALSE(json_response["data"].HasMember("places_lists"));
  EXPECT_FALSE(json_response.HasMember("layout"))
      << "There is no data, skip layout.";
}

TEST(PlacesList, LastPlaces) {
  auto places_list = GetWidget("part_n", "Два последних ресторана", 2);

  formats::json::ValueBuilder response;
  auto source = GetSource(4);

  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  places_list->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  auto places = json_response["data"]["places_lists"][0]["payload"]["places"];
  EXPECT_EQ(places.GetSize(), 2);
  for (int i = 0; i < 2; ++i) {
    EXPECT_EQ(places[i]["id"].As<std::string>(), fmt::format("id{}", i + 3));
    EXPECT_EQ(places[i]["name"].As<std::string>(),
              fmt::format("name{}", i + 3));
  }
}

TEST(PlacesList, LastPlacesEmpty) {
  auto places_list = GetWidget("part_n", "Два последних ресторана", 2);

  formats::json::ValueBuilder response;
  auto source = GetSource(2);

  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_FALSE(places_list->HasData());

  places_list->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  EXPECT_FALSE(json_response["data"].HasMember("places_lists"));
  EXPECT_FALSE(json_response.HasMember("layout"))
      << "There is no data, skip layout.";
}

TEST(PlacesList, ClosedPlaces) {
  auto places_list =
      GetWidget("part_n", "Закрыты", std::nullopt, std::nullopt, "closed");

  formats::json::ValueBuilder response;
  auto source = GetSource(5, true);

  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  places_list->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  auto places = json_response["data"]["places_lists"][0]["payload"]["places"];
  EXPECT_EQ(places.GetSize(), 5);
  for (int i = 0; i < 5; ++i) {
    EXPECT_EQ(places[i]["id"].As<std::string>(), fmt::format("id{}", i + 1));
    EXPECT_EQ(places[i]["name"].As<std::string>(),
              fmt::format("name{}", i + 1));
  }
}
