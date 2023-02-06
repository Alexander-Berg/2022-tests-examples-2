#include "mini_places_carousel.hpp"

#include <fmt/format.h>
#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/logging/log.hpp>

#include <models/constructor/db_model.hpp>
#include <sources/catalog/catalog_data_source.hpp>
#include <widgets/mini_places_carousel/factory.hpp>

namespace {
using Response = eats_layout_constructor::sources::DataSourceResponses;
using FilterType =
    eats_layout_constructor::widgets::mini_places_carousel::Placefiltertype;

namespace sources = eats_layout_constructor::sources;
namespace catalog = sources::catalog;

const std::string kBlockId = "open_no_filters_shop_sort_default";

formats::json::Value GetWidgetData(
    const std::string& id, const std::string& title,
    const std::vector<int>& brands, std::optional<int> min_count,
    std::optional<int> limit, std::optional<FilterType> filter_type,
    const std::optional<std::string>& image_source,
    const std::optional<std::string>& delivery_feature_mode) {
  formats::json::ValueBuilder widget;
  widget["meta"] = formats::json::Type::kObject;
  widget["id"] = id;
  widget["payload"]["title"] = title;
  widget["type"] = "mini_places_carousel";
  widget["meta"]["brands_order"] = brands;
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
  return widget.ExtractValue();
}

std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> GetWidget(
    const std::string& id, const std::string& title,
    const std::vector<int>& brands, std::optional<int> min_count = std::nullopt,
    std::optional<int> limit = std::nullopt,
    std::optional<FilterType> filter_type = std::nullopt,
    const std::optional<std::string>& image_source = std::nullopt,
    const std::optional<std::string>& delivery_feature_mode = std::nullopt) {
  const auto widget_data =
      GetWidgetData(id, title, brands, min_count, limit, filter_type,
                    image_source, delivery_feature_mode);
  return eats_layout_constructor::widgets::mini_places_carousel::
      MiniPlacesCarouselFactory(
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
    place["slug"] = fmt::format("slug{}", i + 1);
    place["name"] = fmt::format("name{}", i + 1);
    place["brand"]["slug"] = fmt::format("brand_slug{}", i + 1);
    place["brand"]["name"] = fmt::format("brand_name{}", i + 1);
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

TEST(MiniPlacesCarousel, MainFlow) {
  namespace widgets = eats_layout_constructor::widgets;
  auto mini_places_carousel = GetWidget("morda", "Рекламная пауза", {2, 3});
  formats::json::ValueBuilder response;
  auto source = GetSource(4);

  EXPECT_FALSE(mini_places_carousel->HasData());
  mini_places_carousel->FilterSourceResponse(source);
  EXPECT_TRUE(mini_places_carousel->HasData());

  mini_places_carousel->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  {
    auto layout = json_response["layout"];
    EXPECT_EQ(layout.GetSize(), 1);
    EXPECT_EQ(layout[0]["type"].As<std::string>(), "mini_places_carousel");
  }
  {
    auto mini_places_carousels = json_response["data"]["mini_places_carousels"];
    EXPECT_EQ(mini_places_carousels.GetSize(), 1);
    EXPECT_EQ(mini_places_carousels[0]["payload"]["places"].GetSize(), 4);
    EXPECT_EQ(mini_places_carousels[0]["id"].As<std::string>(), "morda");
  }

  {
    std::vector<std::string> order{"slug2", "slug3", "slug1", "slug4"};

    auto places =
        json_response["data"]["mini_places_carousels"][0]["payload"]["places"];

    for (size_t i = 0; i < places.GetSize(); i++) {
      EXPECT_TRUE(places[i].HasMember("slug"));
      EXPECT_TRUE(places[i].HasMember("name"));
      EXPECT_TRUE(places[i].HasMember("brand"));

      EXPECT_EQ(places[i]["slug"].As<std::string>(), order[i]);
    }
  }
}

TEST(MiniPlacesCarousel, ContainLessThanMin) {
  namespace widgets = eats_layout_constructor::widgets;
  auto mini_places_carousel = GetWidget("morda", "Рекламная пауза", {1, 2}, 3);

  formats::json::ValueBuilder response;
  auto source = GetSource(2);

  EXPECT_FALSE(mini_places_carousel->HasData());
  mini_places_carousel->FilterSourceResponse(source);
  EXPECT_FALSE(mini_places_carousel->HasData());

  mini_places_carousel->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_FALSE(json_response.HasMember("layout"));
  EXPECT_FALSE(json_response.HasMember("data"));
}

TEST(MiniPlacesCarousel, ContainMoreThanMax) {
  namespace widgets = eats_layout_constructor::widgets;
  auto mini_places_carousel =
      GetWidget("morda", "Рекламная пауза", {2, 3, 4, 5, 6, 7, 1}, 3, 5);

  formats::json::ValueBuilder response;
  auto source = GetSource(7);

  EXPECT_FALSE(mini_places_carousel->HasData());
  mini_places_carousel->FilterSourceResponse(source);
  EXPECT_TRUE(mini_places_carousel->HasData());

  mini_places_carousel->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(
      json_response["data"]["mini_places_carousels"][0]["payload"]["places"]
          .GetSize(),
      5);
}

TEST(MiniPlacesCarousel, Sort) {
  namespace widgets = eats_layout_constructor::widgets;
  auto mini_places_carousel = GetWidget("morda", "hello", {6, 4, 8, 7, 1});

  formats::json::ValueBuilder response;
  auto source = GetSource(10);

  EXPECT_FALSE(mini_places_carousel->HasData());
  mini_places_carousel->FilterSourceResponse(source);
  EXPECT_TRUE(mini_places_carousel->HasData());

  mini_places_carousel->UpdateLayout(response);

  const std::vector<int> order{6, 4, 8, 7, 1, 2, 3, 5, 9, 10};

  auto json_response = response.ExtractValue();

  const auto places =
      json_response["data"]["mini_places_carousels"][0]["payload"]["places"];

  ASSERT_EQ(places.GetSize(), order.size());

  for (size_t i = 0; i < order.size(); ++i) {
    EXPECT_EQ(places[i]["slug"].As<std::string>(),
              fmt::format("slug{}", order[i]))
        << "unexpected place on position " << i;
  }
}

TEST(MiniPlacesCarousel, RequestParams) {
  const std::string kAnyBlockId = "any_no_filters_shop_sort_default";

  namespace widgets = eats_layout_constructor::widgets;
  auto mini_places_carousel = GetWidget("morda",            // id
                                        "Рекламная пауза",  // title
                                        {},                 // brands
                                        std::nullopt,       // min_count
                                        std::nullopt,       // limit
                                        FilterType::kAny    // filter_type
  );

  eats_layout_constructor::sources::DataSourceParams params;
  mini_places_carousel->FillSourceRequestParams(params);

  EXPECT_NE(params.find("catalog"), params.end());
  auto catalog_params = std::any_cast<catalog::Params>(params["catalog"]);
  EXPECT_EQ(catalog_params.blocks.size(), 1);
  ASSERT_EQ(catalog_params.blocks.count(kAnyBlockId), 1);

  auto block = catalog_params.blocks[kAnyBlockId];
  EXPECT_EQ(block.sort_type, sources::catalog::SortType::kDefault);
  EXPECT_EQ(block.type, sources::catalog::PlaceType::kAny);
  EXPECT_TRUE(block.disable_filters);
}

TEST(MiniPlacesCarousel, ImageSource) {
  static const std::string kPhoto = "photo";
  auto mini_places_carousel = GetWidget("morda",            // id
                                        "Рекламная пауза",  // title
                                        {},                 // brands
                                        std::nullopt,       // min_count
                                        std::nullopt,       // limit
                                        std::nullopt,       // filter_type
                                        kPhoto              // image_source
  );

  formats::json::ValueBuilder response;

  auto source = GetSource(1);
  mini_places_carousel->FilterSourceResponse(source);

  ASSERT_TRUE(mini_places_carousel->HasData());
  mini_places_carousel->UpdateLayout(response);
  auto json_response = response.ExtractValue();
  auto meta = json_response["data"]["mini_places_carousels"][0]["payload"]
                           ["places"][0]["meta"];

  ASSERT_TRUE(meta.IsObject());

  auto image_source = meta["image_source"];
  ASSERT_TRUE(image_source.IsString());
  ASSERT_EQ(image_source.As<std::string>(), kPhoto);
}

TEST(MiniPlacesCarousel, DeliveryFeatureMode) {
  auto mini_places_carousel = GetWidget("morda",            // id
                                        "Рекламная пауза",  // title
                                        {},                 // brands
                                        std::nullopt,       // min_count
                                        std::nullopt,       // limit
                                        std::nullopt,       // filter_type
                                        std::nullopt,       // image_source
                                        "max"               // image_source
  );

  eats_layout_constructor::sources::DataSourceParams params;
  mini_places_carousel->FillSourceRequestParams(params);

  EXPECT_NE(params.find("catalog"), params.end());
  auto catalog_params = std::any_cast<catalog::Params>(params["catalog"]);
  EXPECT_EQ(catalog_params.blocks.size(), 1);
  LOG_ERROR() << catalog_params.blocks.begin()->first;
  EXPECT_EQ(
      catalog_params.blocks.count("open_no_filters_shop_sort_default_eta_max"),
      1);

  auto block =
      catalog_params.blocks["open_no_filters_shop_sort_default_eta_max"];
  EXPECT_EQ(block.delivery_feature_mode.value(),
            clients::catalog::BlockSpecDeliveryfeaturemode::kMax);
}
