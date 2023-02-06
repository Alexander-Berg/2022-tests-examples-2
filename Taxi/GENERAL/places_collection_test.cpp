#include "places_collection.hpp"

#include <fmt/format.h>
#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>

#include <models/constructor/db_model.hpp>
#include <sources/catalog/catalog_data_source.hpp>
#include <widgets/places_collection/factory.hpp>

namespace {

using Response = eats_layout_constructor::sources::DataSourceResponses;
namespace sources = eats_layout_constructor::sources;
namespace catalog = sources::catalog;
namespace predicate = ::clients::catalog::libraries::eats_catalog_predicate;

struct WidgetConfig {
  std::string id = "test_id";
  std::string title = "Untitled";
  std::string place_filter_type = "open";
  std::string output_type = "list";
  std::optional<std::string> selection = std::nullopt;
  std::optional<size_t> low = std::nullopt;
  std::optional<size_t> min_count = std::nullopt;
  std::optional<size_t> limit = std::nullopt;
  std::optional<std::unordered_set<int>> exclude_brands = std::nullopt;
  std::optional<std::string> delivery_feature_mode = std::nullopt;
  std::optional<int> max_distance_m = std::nullopt;
  std::optional<std::unordered_set<int>> only_places = std::nullopt;
  std::optional<std::unordered_set<int>> only_brands = std::nullopt;
  std::optional<std::vector<int>> promo_type_ids = std::nullopt;
  std::optional<std::vector<std::string>> courier_types = std::nullopt;
  std::optional<std::string> surge_radius = std::nullopt;
  std::optional<bool> open_delivery_or_surge_radius = std::nullopt;
  std::optional<std::vector<std::string>> include_businesses = std::nullopt;
  std::optional<std::vector<std::string>> include_places_with_tag =
      std::nullopt;
  std::optional<std::vector<std::string>> exclude_places_with_tag =
      std::nullopt;
};

template <typename T>
void SetIfHasValue(formats::json::ValueBuilder& builder,
                   const std::string& field, const std::optional<T>& value) {
  if (value.has_value()) {
    builder[field] = value.value();
  }
}

formats::json::Value GetWidgetData(const WidgetConfig& conf) {
  formats::json::ValueBuilder widget;
  widget["id"] = conf.id;
  widget["payload"]["title"] = conf.title;
  widget["type"] = "places_selection";

  auto meta = formats::json::ValueBuilder{formats::json::Type::kObject};

  meta["place_filter_type"] = conf.place_filter_type;
  meta["output_type"] = conf.output_type;

  SetIfHasValue(meta, "selection", conf.selection);
  SetIfHasValue(meta, "low", conf.low);
  SetIfHasValue(meta, "limit", conf.limit);
  SetIfHasValue(meta, "min_count", conf.min_count);
  SetIfHasValue(meta, "exclude_brands", conf.exclude_brands);
  SetIfHasValue(meta, "delivery_feature_mode", conf.delivery_feature_mode);
  SetIfHasValue(meta, "max_distance_m", conf.max_distance_m);
  SetIfHasValue(meta, "only_places", conf.only_places);
  SetIfHasValue(meta, "only_brands", conf.only_brands);
  SetIfHasValue(meta, "courier_types", conf.courier_types);
  SetIfHasValue(meta, "promo_type_ids", conf.promo_type_ids);
  SetIfHasValue(meta, "surge_radius", conf.surge_radius);
  SetIfHasValue(meta, "open_delivery_or_surge_radius",
                conf.open_delivery_or_surge_radius);
  SetIfHasValue(meta, "open_delivery_or_surge_radius",
                conf.open_delivery_or_surge_radius);
  SetIfHasValue(meta, "include_businesses", conf.include_businesses);
  SetIfHasValue(meta, "include_places_with_tag", conf.include_places_with_tag);
  SetIfHasValue(meta, "exclude_places_with_tag", conf.exclude_places_with_tag);

  widget["meta"] = std::move(meta);
  return widget.ExtractValue();
}

std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> GetWidget(
    const WidgetConfig& conf) {
  using eats_layout_constructor::models::constructor::Meta;
  using eats_layout_constructor::models::constructor::Payload;
  const auto widget_data = GetWidgetData(conf);

  return eats_layout_constructor::widgets::places_collection::
      PlacesCollectionFactory(
          eats_layout_constructor::models::constructor::WidgetTemplateName{},
          Meta{widget_data["meta"]}, Payload{widget_data["payload"]}, {},
          widget_data["id"].As<std::string>());
}

Response GetSource(const std::vector<std::pair<std::string, int>>& blocks) {
  using Catalog = eats_layout_constructor::sources::CatalogDataSource;
  auto catalog_response =
      std::make_shared<Catalog::Response>(Catalog::Response{});

  int unique_id = 1;
  for (const auto& block : blocks) {
    const int places_count = block.second;
    std::vector<catalog::Place> places;
    places.reserve(places_count);
    for (auto i = 0; i < places_count; ++i) {
      formats::json::ValueBuilder place;
      place["id"] = fmt::format("id{}", unique_id);
      place["name"] = fmt::format("name{}", unique_id);
      places.push_back(
          catalog::Place{{sources::PlaceId(unique_id),
                          sources::BrandId(unique_id), std::nullopt},
                         place.ExtractValue()});
      unique_id++;
    }

    const auto& block_id = block.first;
    catalog_response->blocks[block_id].places = places;
  }

  Response response;
  response[Catalog::kName] = catalog_response;
  return response;
}

using Places = std::vector<int>;                // places by ids
using Widget = std::pair<std::string, Places>;  // id, places

void CheckLayoutPlaces(const formats::json::Value& json_value,
                       const std::vector<Widget>& expected_widgets) {
  EXPECT_TRUE(json_value.HasMember("layout"))
      << "Empty response layout: " << ToString(json_value);
  EXPECT_EQ(json_value["layout"].GetSize(), expected_widgets.size());
  const auto& places_lists = json_value["data"]["places_lists"];
  EXPECT_EQ(places_lists.GetSize(), expected_widgets.size());

  for (size_t i = 0; i < expected_widgets.size(); ++i) {
    const auto& expected_widget_id = expected_widgets.at(i).first;
    EXPECT_EQ(places_lists[i]["id"].As<std::string>(), expected_widget_id);

    const auto& places = places_lists[i]["payload"]["places"];
    const auto& expected_places = expected_widgets.at(i).second;
    for (size_t j = 0; j < expected_places.size(); ++j) {
      const auto& place_id = expected_places.at(j);
      const auto id_str = fmt::format("id{}", place_id);
      const auto name_str = fmt::format("name{}", place_id);
      EXPECT_EQ(places[j]["id"].As<std::string>(), id_str);
      EXPECT_EQ(places[j]["name"].As<std::string>(), name_str);
    }
  }
}

}  // namespace

TEST(PlacesCollection, AllPlaces) {
  const auto widget_id = "all_places";
  auto places_list = GetWidget({widget_id, "Все рестораны", "open"});

  const auto source = GetSource({{"open", 3}});

  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  formats::json::ValueBuilder response;
  places_list->UpdateLayout(response);

  const auto json_response = response.ExtractValue();
  const std::vector<Widget> expected_widgets = {{widget_id, {1, 2, 3}}};
  CheckLayoutPlaces(json_response, expected_widgets);
}

TEST(PlacesCollection, FirstNPlaces) {
  const auto limit = 4;
  const auto widget_id = "first_n";
  auto places_list =
      GetWidget({widget_id, "4 первых ресторана", "open", "list", std::nullopt,
                 std::nullopt, std::nullopt, limit});

  const auto source = GetSource({{"open", 5}});
  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  formats::json::ValueBuilder response;
  places_list->UpdateLayout(response);

  const auto json_response = response.ExtractValue();
  const std::vector<Widget> expected_widgets = {{widget_id, {1, 2, 3, 4}}};
  CheckLayoutPlaces(json_response, expected_widgets);
}

TEST(PlacesCollection, FirstPlacesNotMoreThanN) {
  const auto limit = 3;
  const auto widget_id = "first_n";
  auto places_list =
      GetWidget({widget_id, "Три первых ресторана", "open", "list",
                 std::nullopt, std::nullopt, std::nullopt, limit});

  const auto source = GetSource({{"open", 2}});
  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  formats::json::ValueBuilder response;
  places_list->UpdateLayout(response);

  const auto json_response = response.ExtractValue();
  const std::vector<Widget> expected_widgets = {{widget_id, {1, 2}}};
  CheckLayoutPlaces(json_response, expected_widgets);
}

TEST(PlacesCollection, LastPlaces) {
  const auto low = 2;
  const auto widget_id = "last";
  auto places_list = GetWidget({widget_id, "Все остальные после первых двух",
                                "open", "list", std::nullopt, low});

  auto source = GetSource({{"open", 4}});
  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  formats::json::ValueBuilder response;
  places_list->UpdateLayout(response);

  const auto json_response = response.ExtractValue();
  const std::vector<Widget> expected_widgets = {{widget_id, {3, 4}}};
  CheckLayoutPlaces(json_response, expected_widgets);
}

TEST(PlacesCollection, PlacesSlice) {
  const auto low = 2;
  const auto limit = 2;
  const auto widget_id = "slice";
  auto places_list =
      GetWidget({widget_id, "Два ресторана в середине", "open", "list",
                 std::nullopt, low, std::nullopt, limit});

  const auto source = GetSource({{"open", 5}});
  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  formats::json::ValueBuilder response;
  places_list->UpdateLayout(response);

  const auto json_response = response.ExtractValue();
  const std::vector<Widget> expected_widgets = {{widget_id, {3, 4}}};
  CheckLayoutPlaces(json_response, expected_widgets);
}

TEST(PlacesCollection, PlacesSliceContainLess) {
  const auto low = 1;
  const auto limit = 3;
  const auto widget_id = "slice";
  auto places_list =
      GetWidget({widget_id, "Три ресторана в середине", "open", "list",
                 std::nullopt, low, std::nullopt, limit});

  const auto source = GetSource({{"open", 3}});
  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  formats::json::ValueBuilder response;
  places_list->UpdateLayout(response);

  const auto json_response = response.ExtractValue();
  const std::vector<Widget> expected_widgets = {{widget_id, {2, 3}}};
  CheckLayoutPlaces(json_response, expected_widgets);
}

TEST(PlacesCollection, PlacesSliceEmpty) {
  const auto low = 3;
  const auto limit = 2;
  const auto widget_id = "slice";
  auto places_list =
      GetWidget({widget_id, "Два ресторана в середине", "open", "list",
                 std::nullopt, low, std::nullopt, limit});

  const auto source = GetSource({{"open", 2}});
  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_FALSE(places_list->HasData());

  formats::json::ValueBuilder response;
  places_list->UpdateLayout(response);

  const auto json_response = response.ExtractValue();
  EXPECT_FALSE(json_response["data"].HasMember("places_lists"));
  EXPECT_FALSE(json_response.HasMember("layout"))
      << "There is no data, skip layout.";
}

TEST(PlacesCollection, EnoughPlaces) {
  const auto min = 3;
  const auto widget_id = "min3";
  auto places_list = GetWidget({widget_id, "Как минимум 3 ресторана", "open",
                                "list", std::nullopt, std::nullopt, min});

  const auto source = GetSource({{"open", 4}});
  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  formats::json::ValueBuilder response;
  places_list->UpdateLayout(response);

  const auto json_response = response.ExtractValue();
  const std::vector<Widget> expected_widgets = {{widget_id, {1, 2, 3, 4}}};
  CheckLayoutPlaces(json_response, expected_widgets);
}

TEST(PlacesCollection, NotEnoughPlaces) {
  const auto min = 5;
  const auto widget_id = "min5";
  auto places_list = GetWidget({widget_id, "Как минимум 5 ресторанов", "open",
                                "list", std::nullopt, std::nullopt, min});

  const auto source = GetSource({{"open", 4}});
  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_FALSE(places_list->HasData());

  formats::json::ValueBuilder response;
  places_list->UpdateLayout(response);

  const auto json_response = response.ExtractValue();
  EXPECT_FALSE(json_response["data"].HasMember("places_lists"));
  EXPECT_FALSE(json_response.HasMember("layout"));
}

TEST(PlacesCollection, PlacesExcludeBrands) {
  const auto widget_id = "exclude_brands";
  const auto excluded_brands = std::unordered_set<int>{2};
  auto places_list =
      GetWidget({widget_id, "Все кроме brand2", "open", "list", std::nullopt,
                 std::nullopt, std::nullopt, std::nullopt, excluded_brands});

  const auto source = GetSource({{"open", 3}});
  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  formats::json::ValueBuilder response;
  places_list->UpdateLayout(response);

  const auto json_response = response.ExtractValue();
  const std::vector<Widget> expected_widgets = {{widget_id, {1, 3}}};
  CheckLayoutPlaces(json_response, expected_widgets);
}

TEST(PlacesCollection, OnlyPlaces) {
  WidgetConfig cfg{};
  cfg.id = "only_places";
  cfg.only_places = std::unordered_set<int>{2, 4};

  auto places_list = GetWidget(cfg);

  const auto source = GetSource({{"open", 6}});
  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  formats::json::ValueBuilder response;
  places_list->UpdateLayout(response);

  const auto json_response = response.ExtractValue();
  const std::vector<Widget> expected_widgets = {{cfg.id, {2, 4}}};
  CheckLayoutPlaces(json_response, expected_widgets);
}

TEST(PlacesCollection, OnlyBrands) {
  WidgetConfig cfg{};
  cfg.id = "only_brands";
  cfg.only_brands = std::unordered_set<int>{1, 4};

  auto places_list = GetWidget(cfg);

  const auto source = GetSource({{"open", 6}});
  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  formats::json::ValueBuilder response;
  places_list->UpdateLayout(response);

  const auto json_response = response.ExtractValue();
  const std::vector<Widget> expected_widgets = {{cfg.id, {1, 4}}};
  CheckLayoutPlaces(json_response, expected_widgets);
}

TEST(PlacesCollection, FiltersCombine) {
  WidgetConfig cfg{};
  cfg.id = "filter";
  cfg.only_brands = std::unordered_set<int>{1, 4, 6};
  cfg.only_places = std::unordered_set<int>{4, 6, 10};
  cfg.exclude_brands = std::unordered_set<int>{6, 11};

  auto places_list = GetWidget(cfg);

  const auto source = GetSource({{"open", 15}});
  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  formats::json::ValueBuilder response;
  places_list->UpdateLayout(response);

  const auto json_response = response.ExtractValue();
  const std::vector<Widget> expected_widgets = {{cfg.id, {4}}};
  CheckLayoutPlaces(json_response, expected_widgets);
}

TEST(PlacesCollection, OpenPlaces) {
  const auto widget_id = "open_places";
  auto places_list = GetWidget({widget_id, "Открытые", "open"});

  auto source = GetSource({{"closed", 3}, {"open", 2}});
  EXPECT_FALSE(places_list->HasData());
  places_list->FilterSourceResponse(source);
  EXPECT_TRUE(places_list->HasData());

  formats::json::ValueBuilder response;
  places_list->UpdateLayout(response);

  const auto json_response = response.ExtractValue();
  const std::vector<Widget> expected_widgets = {{widget_id, {4, 5}}};
  CheckLayoutPlaces(json_response, expected_widgets);
}

TEST(PlacesCollection, PlacesCarousel) {
  const auto widget_id = "carousel_widget";
  auto places_carousel = GetWidget({widget_id, "Карусель", "open", "carousel"});

  auto source = GetSource({{"open", 3}});
  EXPECT_FALSE(places_carousel->HasData());
  places_carousel->FilterSourceResponse(source);
  EXPECT_TRUE(places_carousel->HasData());

  formats::json::ValueBuilder response;
  places_carousel->UpdateLayout(response);

  const auto json_response = response.ExtractValue();
  const std::vector<Widget> expected_widgets = {{widget_id, {1, 2, 3}}};
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["layout"][0]["type"].As<std::string>(),
            "places_carousel");
  const auto& places_carousels = json_response["data"]["places_carousels"];
  EXPECT_EQ(places_carousels.GetSize(), 1);
  EXPECT_EQ(places_carousels[0]["payload"]["places"].GetSize(), 3);
}

TEST(PlacesCollection, PlacesCarouselAsList) {
  /* Widget with 'output_type=carousel' will be rendered as a list
   * if it contains only one place */
  const auto widget_id = "carousel_widget";
  auto places_carousel =
      GetWidget({widget_id, "Один рест", "open", "carousel"});

  auto source = GetSource({{"open", 1}});
  EXPECT_FALSE(places_carousel->HasData());
  places_carousel->FilterSourceResponse(source);
  EXPECT_TRUE(places_carousel->HasData());

  formats::json::ValueBuilder response;
  places_carousel->UpdateLayout(response);

  const auto json_response = response.ExtractValue();
  const std::vector<Widget> expected_widgets = {{widget_id, {1, 2, 3}}};
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["layout"][0]["type"].As<std::string>(),
            "places_list");
  const auto& places_carousels = json_response["data"]["places_lists"];
  EXPECT_EQ(places_carousels.GetSize(), 1);
  EXPECT_EQ(places_carousels[0]["payload"]["places"].GetSize(), 1);
}

TEST(PlacesCollection, RequestParams) {
  auto places_list =
      GetWidget({"history", "Акции", "open", "list", "history_order"});

  eats_layout_constructor::sources::DataSourceParams params;
  places_list->FillSourceRequestParams(params);

  EXPECT_NE(params.find("catalog"), params.end());
  auto catalog_params = std::any_cast<catalog::Params>(params["catalog"]);
  EXPECT_EQ(catalog_params.blocks.size(), 1);
  EXPECT_EQ(catalog_params.blocks.count("open_history_order"), 1);
  EXPECT_EQ(catalog_params.blocks["open_history_order"].compilation_type,
            "history_order");
}

TEST(PlacesCollection, HistoryOrderSelection) {
  auto places_selection =
      GetWidget({"history", "Вы заказывали", "open", "list", "history_order"});
  formats::json::ValueBuilder response;
  const auto source = GetSource({{"open_history_order", 3}});

  EXPECT_FALSE(places_selection->HasData());
  places_selection->FilterSourceResponse(source);
  EXPECT_TRUE(places_selection->HasData());

  places_selection->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["places_lists"].GetSize(), 1);
  EXPECT_EQ(
      json_response["data"]["places_lists"][0]["payload"]["places"].GetSize(),
      3);
  EXPECT_EQ(json_response["data"]["places_lists"][0]["id"].As<std::string>(),
            "history");
}

TEST(PlacesCollection, DeliveryFeatureMode) {
  WidgetConfig cfg{};
  cfg.place_filter_type = "open";
  cfg.delivery_feature_mode = "max";
  auto places_list = GetWidget(cfg);

  eats_layout_constructor::sources::DataSourceParams params;
  places_list->FillSourceRequestParams(params);

  EXPECT_NE(params.find("catalog"), params.end());
  auto catalog_params = std::any_cast<catalog::Params>(params["catalog"]);
  EXPECT_EQ(catalog_params.blocks.size(), 1);
  EXPECT_EQ(catalog_params.blocks.count("open_eta_max"), 1);
  EXPECT_EQ(catalog_params.blocks["open_eta_max"].delivery_feature_mode.value(),
            clients::catalog::BlockSpecDeliveryfeaturemode::kMax);
}

TEST(PlacesCollection, Distance) {
  constexpr int kMaxDistance = 1000;
  WidgetConfig cfg{};
  cfg.place_filter_type = "open";
  cfg.max_distance_m = kMaxDistance;
  auto places_list = GetWidget(cfg);

  eats_layout_constructor::sources::DataSourceParams params;
  places_list->FillSourceRequestParams(params);

  EXPECT_NE(params.find("catalog"), params.end());

  auto catalog_params = std::any_cast<catalog::Params>(params["catalog"]);
  EXPECT_EQ(catalog_params.blocks.size(), 1);
  EXPECT_EQ(catalog_params.blocks.count("open_distance_m_1000"), 1);

  const auto& block = catalog_params.blocks["open_distance_m_1000"];
  ASSERT_TRUE(block.condition.has_value());

  const auto& condition = block.condition.value();
  EXPECT_EQ(condition.type, predicate::PredicateType::kLte);
  ASSERT_TRUE(condition.init.has_value());
  const auto& init = condition.init.value();

  EXPECT_EQ(init.arg_name, predicate::Argument::kDistanceM);
  EXPECT_EQ(init.arg_type.value(), predicate::ValueType::kInt);
  EXPECT_EQ(std::get<int>(init.value.value()), kMaxDistance);
}

TEST(PlacesCollection, CourierTypes) {
  const std::string kExpectedBlockId =
      "open_courier_types_bicycle_yandex_rover";

  WidgetConfig cfg{};
  cfg.courier_types = std::vector<std::string>{"bicycle", "yandex_rover"};

  auto places_list = GetWidget(cfg);

  eats_layout_constructor::sources::DataSourceParams params;
  places_list->FillSourceRequestParams(params);

  ASSERT_NE(params.find("catalog"), params.end());

  auto catalog_params = std::any_cast<catalog::Params>(params["catalog"]);
  ASSERT_EQ(catalog_params.blocks.size(), 1);
  ASSERT_EQ(catalog_params.blocks.count(kExpectedBlockId), 1);

  const auto& block = catalog_params.blocks[kExpectedBlockId];
  ASSERT_TRUE(block.condition.has_value());

  const auto& condition = block.condition.value();
  EXPECT_EQ(condition.type, predicate::PredicateType::kInSet);
  ASSERT_TRUE(condition.init.has_value());
  const auto& init = condition.init.value();

  EXPECT_EQ(init.arg_name, predicate::Argument::kCourierType);
  EXPECT_EQ(init.set_elem_type, predicate::ValueType::kString);

  ASSERT_TRUE(init.set.has_value());
  std::unordered_set<std::string> values;
  for (const auto& item : init.set.value()) {
    values.insert(std::get<std::string>(item));
  }

  EXPECT_EQ(values, std::unordered_set<std::string>(cfg.courier_types->begin(),
                                                    cfg.courier_types->end()));
}

TEST(PlacesCollection, PromoTypeIds) {
  const std::string kExpectedBlockId = "open_promo_type_1_200_1021";

  WidgetConfig cfg{};
  cfg.promo_type_ids = std::vector<int>{1, 200, 1021};

  auto places_list = GetWidget(cfg);

  eats_layout_constructor::sources::DataSourceParams params;
  places_list->FillSourceRequestParams(params);

  ASSERT_NE(params.find("catalog"), params.end());

  auto catalog_params = std::any_cast<catalog::Params>(params["catalog"]);
  ASSERT_EQ(catalog_params.blocks.size(), 1);
  ASSERT_EQ(catalog_params.blocks.count(kExpectedBlockId), 1);

  const auto& block = catalog_params.blocks[kExpectedBlockId];
  ASSERT_TRUE(block.condition.has_value());

  const auto& condition = block.condition.value();
  EXPECT_EQ(condition.type, predicate::PredicateType::kInSet);

  ASSERT_TRUE(condition.init.has_value());
  const auto& init = condition.init.value();

  EXPECT_EQ(init.arg_name, predicate::Argument::kPromoType);
  EXPECT_EQ(init.set_elem_type, predicate::ValueType::kInt);

  ASSERT_TRUE(init.set.has_value());
  std::unordered_set<int> values;
  for (const auto& item : init.set.value()) {
    values.insert(std::get<int>(item));
  }

  EXPECT_EQ(values, std::unordered_set<int>(cfg.promo_type_ids->begin(),
                                            cfg.promo_type_ids->end()));
}

TEST(PlacesCollection, NoSurgeRadius) {
  WidgetConfig cfg{};
  cfg.place_filter_type = "open";
  cfg.surge_radius = "none";
  auto places_list = GetWidget(cfg);

  eats_layout_constructor::sources::DataSourceParams params;
  places_list->FillSourceRequestParams(params);

  EXPECT_NE(params.find("catalog"), params.end());

  auto catalog_params = std::any_cast<catalog::Params>(params["catalog"]);
  EXPECT_EQ(catalog_params.blocks.count("open_surge_radius_none"), 1);

  const auto& block = catalog_params.blocks["open_surge_radius_none"];

  ASSERT_TRUE(block.condition.has_value());
  const auto& condition = block.condition.value();

  ASSERT_TRUE(condition.init.has_value());
  const auto& init = condition.init.value();

  EXPECT_EQ(condition.type, predicate::PredicateType::kLte);
  EXPECT_EQ(init.arg_name, predicate::Argument::kSurgeShowRadius);
  EXPECT_EQ(init.arg_type.value(), predicate::ValueType::kInt);
  EXPECT_EQ(std::get<int>(init.value.value()), 0);
}

TEST(PlacesCollection, DeliveryDisabledBySurgeRadius) {
  WidgetConfig cfg{};
  cfg.place_filter_type = "open";
  cfg.surge_radius = "delivery_disabled";
  auto places_list = GetWidget(cfg);

  eats_layout_constructor::sources::DataSourceParams params;
  places_list->FillSourceRequestParams(params);

  EXPECT_NE(params.find("catalog"), params.end());

  auto catalog_params = std::any_cast<catalog::Params>(params["catalog"]);
  EXPECT_EQ(catalog_params.blocks.count("open_surge_radius_delivery_disabled"),
            1);

  const auto& block =
      catalog_params.blocks["open_surge_radius_delivery_disabled"];

  const auto& condition = block.condition.value();

  ASSERT_TRUE(condition.init.has_value());
  const auto& init = condition.init.value();

  EXPECT_EQ(condition.type, predicate::PredicateType::kGt);
  EXPECT_EQ(init.arg_name, predicate::Argument::kSurgeShowRadius);
  EXPECT_EQ(init.arg_type.value(), predicate::ValueType::kInt);
  EXPECT_EQ(std::get<int>(init.value.value()), 0);
}

TEST(PlacesCollection, OpenDeliveryOrSurgeRadius) {
  namespace catalog_predicate =
      ::clients::catalog::libraries::eats_catalog_predicate;
  using Pred = catalog_predicate::Predicate;
  using Preds = std::vector<catalog_predicate::Predicate>;

  WidgetConfig cfg{};
  cfg.place_filter_type = "any";
  cfg.open_delivery_or_surge_radius = true;
  auto places_list = GetWidget(cfg);

  eats_layout_constructor::sources::DataSourceParams params;
  places_list->FillSourceRequestParams(params);

  EXPECT_NE(params.find("catalog"), params.end());

  auto catalog_params = std::any_cast<catalog::Params>(params["catalog"]);
  const auto& block =
      catalog_params.blocks.at("any_open_delivery_or_surge_radius");

  ASSERT_TRUE(block.allow_surge_radius_shipping_type_flowing);
  ASSERT_TRUE(block.condition.has_value());

  const auto& condition = block.condition.value();
  EXPECT_EQ(condition.type, predicate::PredicateType::kAllOf);

  const auto kExpectedIsValid = catalog_predicate::Predicate{
      catalog_predicate::PredicateType::kIntersects,
      catalog_predicate::PredicateInit{
          catalog_predicate::Argument::kShippingTypes,
          std::nullopt,
          std::nullopt,
          catalog_predicate::ValueType::kString,
          std::unordered_set<std::variant<std::string, int>>{"delivery",
                                                             "pickup"},
      },
  };

  const auto kExpectedOpenDelivery = catalog_predicate::Predicate{
      catalog_predicate::PredicateType::kEq,
      catalog_predicate::PredicateInit{
          catalog_predicate::Argument::kDeliveryAvailable,
          catalog_predicate::ValueType::kInt,
          1,
      },
  };

  const auto kExpectedUnderSurgeRadius = catalog_predicate::Predicate{
      catalog_predicate::PredicateType::kGt,
      catalog_predicate::PredicateInit{
          catalog_predicate::Argument::kSurgeShowRadius,
          catalog_predicate::ValueType::kInt,
          0,
      },
  };

  const auto kExpectedPredicate = Pred{
      catalog_predicate::PredicateType::kAllOf,
      std::nullopt,
      Preds{
          kExpectedIsValid,
          Pred{
              catalog_predicate::PredicateType::kAnyOf,
              std::nullopt,
              Preds{
                  kExpectedOpenDelivery,
                  kExpectedUnderSurgeRadius,
              },
          },
      },
  };

  ASSERT_EQ(condition, kExpectedPredicate)
      << ToString(formats::json::ValueBuilder{condition}.ExtractValue());
}

TEST(PlacesCollection, RestaurantsOrTag) {
  namespace catalog_predicate =
      ::clients::catalog::libraries::eats_catalog_predicate;
  using Pred = catalog_predicate::Predicate;
  using Preds = std::vector<catalog_predicate::Predicate>;

  WidgetConfig cfg{};
  cfg.place_filter_type = "open";
  cfg.include_businesses = std::vector<std::string>{"restaurant"};
  cfg.include_places_with_tag = std::vector<std::string>{"foodmall"};
  auto places_list = GetWidget(cfg);

  eats_layout_constructor::sources::DataSourceParams params;
  places_list->FillSourceRequestParams(params);

  EXPECT_NE(params.find("catalog"), params.end());

  auto catalog_params = std::any_cast<catalog::Params>(params["catalog"]);
  EXPECT_EQ(
      catalog_params.blocks.count("open_business_restaurant_tag_foodmall"), 1);

  const auto& block =
      catalog_params.blocks["open_business_restaurant_tag_foodmall"];

  const auto& condition = block.condition.value();

  const auto kRestaurantsPredicate = Pred{
      catalog_predicate::PredicateType::kInSet,
      catalog_predicate::PredicateInit{
          catalog_predicate::Argument::kBusiness,
          std::nullopt,
          std::nullopt,
          catalog_predicate::ValueType::kString,
          std::unordered_set<std::variant<std::string, int>>{"restaurant"},
      },
  };

  const auto kFoodmallPredicate = Pred{
      catalog_predicate::PredicateType::kIntersects,
      catalog_predicate::PredicateInit{
          catalog_predicate::Argument::kTags,
          std::nullopt,
          std::nullopt,
          catalog_predicate::ValueType::kString,
          std::unordered_set<std::variant<std::string, int>>{"foodmall"},
      },
  };

  const auto kExpectedPredicate = Pred{
      catalog_predicate::PredicateType::kAnyOf,
      std::nullopt,
      Preds{
          kRestaurantsPredicate,
          kFoodmallPredicate,
      },
  };

  ASSERT_EQ(condition, kExpectedPredicate)
      << ToString(formats::json::ValueBuilder{condition}.ExtractValue());
}

TEST(PlacesCollection, ShopNotFoodmall) {
  namespace catalog_predicate =
      ::clients::catalog::libraries::eats_catalog_predicate;
  using Pred = catalog_predicate::Predicate;
  using Preds = std::vector<catalog_predicate::Predicate>;

  WidgetConfig cfg{};
  cfg.place_filter_type = "open";
  cfg.include_businesses = std::vector<std::string>{"shop"};
  cfg.exclude_places_with_tag = std::vector<std::string>{"foodmall"};
  auto places_list = GetWidget(cfg);

  eats_layout_constructor::sources::DataSourceParams params;
  places_list->FillSourceRequestParams(params);

  EXPECT_NE(params.find("catalog"), params.end());

  auto catalog_params = std::any_cast<catalog::Params>(params["catalog"]);
  EXPECT_EQ(catalog_params.blocks.count("open_business_shop_no_tag_foodmall"),
            1);

  const auto& block =
      catalog_params.blocks["open_business_shop_no_tag_foodmall"];

  const auto& condition = block.condition.value();

  const auto kShopsPredicate = Pred{
      catalog_predicate::PredicateType::kInSet,
      catalog_predicate::PredicateInit{
          catalog_predicate::Argument::kBusiness,
          std::nullopt,
          std::nullopt,
          catalog_predicate::ValueType::kString,
          std::unordered_set<std::variant<std::string, int>>{"shop"},
      },
  };

  const auto kFoodmallPredicate = Pred{
      catalog_predicate::PredicateType::kIntersects,
      catalog_predicate::PredicateInit{
          catalog_predicate::Argument::kTags,
          std::nullopt,
          std::nullopt,
          catalog_predicate::ValueType::kString,
          std::unordered_set<std::variant<std::string, int>>{"foodmall"},
      },
  };

  const auto kExpectedPredicate = Pred{
      catalog_predicate::PredicateType::kAllOf,
      std::nullopt,
      Preds{
          Pred{
              catalog_predicate::PredicateType::kNot,
              std::nullopt,
              Preds{
                  kFoodmallPredicate,
              },
          },
          kShopsPredicate,
      },
  };

  ASSERT_EQ(condition, kExpectedPredicate)
      << ToString(formats::json::ValueBuilder{condition}.ExtractValue());
}
