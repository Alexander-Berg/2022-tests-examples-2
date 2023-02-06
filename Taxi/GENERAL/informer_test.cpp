#include <gtest/gtest.h>

#include <sources/eats-order-stats/eats_order_stats_source.hpp>
#include "informer.hpp"

#include <widgets/informer/factory.hpp>

namespace {

namespace informer = eats_layout_constructor::widgets::informer;

using Response = eats_layout_constructor::sources::DataSourceResponses;
Response CreateDataSourceResposne(
    const eats_surge::free_delivery::PlacesStatsWithError&
        place_stats_with_error) {
  using DataSource =
      eats_layout_constructor::sources::eats_order_stats::DataSource;

  auto response = Response{};
  auto informer_response =
      std::make_shared<eats_layout_constructor::sources::eats_order_stats::
                           DataSource::Response>();
  informer_response->place_stats_with_error = place_stats_with_error;
  response[DataSource::kName] = std::move(informer_response);

  return response;
}

using ThemeColor = std::pair<std::string, std::string>;
using ThemedColor = std::vector<ThemeColor>;
using ThemeIcon = std::pair<std::string, std::string>;
using ThemedIcon = std::vector<ThemeIcon>;

struct Text {
  std::string text;
  ThemedColor color;
};

formats::json::ValueBuilder ThemedColorToJson(const ThemedColor& themed_color) {
  formats::json::ValueBuilder result{formats::json::Type::kArray};

  for (const auto& color : themed_color) {
    formats::json::ValueBuilder color_item;
    color_item["theme"] = color.first;
    color_item["color"] = color.second;
    result.PushBack(std::move(color_item));
  }

  return result;
}

formats::json::ValueBuilder TextToJson(const Text& text) {
  formats::json::ValueBuilder text_json;
  text_json["text"] = text.text;
  text_json["color"] = ThemedColorToJson(text.color);
  return text_json;
}

formats::json::ValueBuilder IconToJson(const ThemedIcon& themed_icon) {
  formats::json::ValueBuilder result{formats::json::Type::kArray};

  for (const auto& icon : themed_icon) {
    formats::json::ValueBuilder icon_item;
    icon_item["theme"] = icon.first;
    icon_item["icon"] = icon.second;
    result.PushBack(std::move(icon_item));
  }

  return result;
}

formats::json::Value GetWidgetData(
    const std::string& id, const Text& text,
    const std::optional<ThemedColor>& background_color = std::nullopt,
    const std::optional<ThemedIcon>& icon = std::nullopt,
    const std::optional<std::string>& link = std::nullopt,
    std::optional<int> max_orders = std::nullopt) {
  formats::json::ValueBuilder widget;
  widget["id"] = id;
  widget["type"] = "informer";
  widget["payload"] = formats::json::Type::kObject;
  widget["meta"] = formats::json::Type::kObject;
  widget["meta"]["text"] = TextToJson(text);

  if (background_color) {
    widget["meta"]["background_color"] =
        ThemedColorToJson(background_color.value());
  }

  if (icon) {
    widget["meta"]["icon"] = IconToJson(icon.value());
  }

  if (link) {
    widget["meta"]["link"] = link.value();
  }

  if (max_orders) {
    widget["meta"]["max_orders"] = max_orders.value();
  }

  return widget.ExtractValue();
}

std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> GetWidget(
    const std::string& id, const Text& text,
    const std::optional<ThemedColor>& background_color = std::nullopt,
    const std::optional<ThemedIcon>& icon = std::nullopt,
    const std::optional<std::string>& link = std::nullopt,
    std::optional<int> max_orders = std::nullopt) {
  const auto widget_data =
      GetWidgetData(id, text, background_color, icon, link, max_orders);

  return eats_layout_constructor::widgets::informer::InformerFactory(
      eats_layout_constructor::models::constructor::WidgetTemplateName{},
      eats_layout_constructor::models::constructor::Meta{widget_data["meta"]},
      eats_layout_constructor::models::constructor::Payload{
          widget_data["payload"]},
      {}, widget_data["id"].As<std::string>());
}

}  // namespace

TEST(Informer, TextOnly) {
  auto informer =
      GetWidget("id", {"Текст", {{"dark", "#ffffff"}, {"light", "#000000"}}});

  formats::json::ValueBuilder response;

  EXPECT_TRUE(informer->HasData());
  informer->FilterSourceResponse({});
  informer->FilterWidgetsWithData({});
  EXPECT_TRUE(informer->HasData());

  informer->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["informers"].GetSize(), 1);

  auto response_informer = json_response["data"]["informers"][0]["payload"];
  EXPECT_EQ(response_informer["text"]["text"].As<std::string>(), "Текст");
  const auto& text_color = response_informer["text"]["color"];
  EXPECT_EQ(text_color.GetSize(), 2);
  EXPECT_EQ(text_color[0]["theme"].As<std::string>(), "dark");
  EXPECT_EQ(text_color[0]["value"].As<std::string>(), "#ffffff");
  EXPECT_EQ(text_color[1]["theme"].As<std::string>(), "light");
  EXPECT_EQ(text_color[1]["value"].As<std::string>(), "#000000");
  EXPECT_TRUE(response_informer["background_color"].IsMissing());
  EXPECT_TRUE(response_informer["icon"].IsMissing());
  EXPECT_TRUE(response_informer["link"].IsMissing());
}

TEST(Informer, BackgrounColor) {
  auto informer =
      GetWidget("id", {"Текст", {{"dark", "#ffffff"}, {"light", "#000000"}}},
                {{{"dark", "#000000"}, {"light", "#ffffff"}}});

  formats::json::ValueBuilder response;

  EXPECT_TRUE(informer->HasData());
  informer->FilterSourceResponse({});
  informer->FilterWidgetsWithData({});
  EXPECT_TRUE(informer->HasData());

  informer->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["informers"].GetSize(), 1);

  auto response_informer = json_response["data"]["informers"][0]["payload"];
  EXPECT_EQ(response_informer["text"]["text"].As<std::string>(), "Текст");
  EXPECT_EQ(response_informer["text"]["color"].GetSize(), 2);

  const auto& background_color = response_informer["background_color"];
  EXPECT_EQ(background_color.GetSize(), 2);
  EXPECT_EQ(background_color[0]["theme"].As<std::string>(), "dark");
  EXPECT_EQ(background_color[0]["value"].As<std::string>(), "#000000");
  EXPECT_EQ(background_color[1]["theme"].As<std::string>(), "light");
  EXPECT_EQ(background_color[1]["value"].As<std::string>(), "#ffffff");
  EXPECT_TRUE(response_informer["icon"].IsMissing());
  EXPECT_TRUE(response_informer["link"].IsMissing());
}

TEST(Informer, Icon) {
  auto informer = GetWidget(
      "id", {"Текст", {{"dark", "#ffffff"}, {"light", "#000000"}}},
      std::nullopt, {{{"dark", "icon_dark"}, {"light", "icon_light"}}});

  formats::json::ValueBuilder response;

  EXPECT_TRUE(informer->HasData());
  informer->FilterSourceResponse({});
  informer->FilterWidgetsWithData({});
  EXPECT_TRUE(informer->HasData());

  informer->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["informers"].GetSize(), 1);

  auto response_informer = json_response["data"]["informers"][0]["payload"];

  EXPECT_TRUE(response_informer["background_color"].IsMissing());

  const auto& icon = response_informer["icon"];
  EXPECT_EQ(icon.GetSize(), 2);
  EXPECT_EQ(icon[0]["theme"].As<std::string>(), "dark");
  EXPECT_EQ(icon[0]["icon"].As<std::string>(), "icon_dark");
  EXPECT_EQ(icon[1]["theme"].As<std::string>(), "light");
  EXPECT_EQ(icon[1]["icon"].As<std::string>(), "icon_light");

  EXPECT_TRUE(response_informer["link"].IsMissing());
}

TEST(Informer, Link) {
  auto informer =
      GetWidget("id", {"Текст", {{"dark", "#ffffff"}, {"light", "#000000"}}},
                std::nullopt, std::nullopt, "link");

  formats::json::ValueBuilder response;

  EXPECT_TRUE(informer->HasData());
  informer->FilterSourceResponse({});
  informer->FilterWidgetsWithData({});
  EXPECT_TRUE(informer->HasData());

  informer->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["informers"].GetSize(), 1);

  auto response_informer = json_response["data"]["informers"][0]["payload"];
  EXPECT_TRUE(response_informer["background_color"].IsMissing());
  EXPECT_TRUE(response_informer["icon"].IsMissing());
  EXPECT_EQ(response_informer["link"].As<std::string>(), "link");
}

TEST(Informer, LessThanMaxOrders) {
  auto informer =
      GetWidget("id", {"Текст", {{"dark", "#ffffff"}, {"light", "#000000"}}},
                std::nullopt, std::nullopt, std::nullopt, {3});

  formats::json::ValueBuilder response;
  eats_layout_constructor::sources::DataSourceParams params;

  eats_surge::free_delivery::PlacesStats places_stats{
      {1,  // place_id
       {
           2,             // counter
           1,             // place_id
           "",            // first_order_at
           "",            // last_order_at
           std::nullopt,  // brand_id
           "retail",      // business_type
           std::nullopt   // delivery_type
       }}};
  eats_surge::free_delivery::PlacesStatsWithError place_stats_with_error{
      places_stats, false};

  EXPECT_FALSE(informer->HasData());
  informer->FillSourceRequestParams(params);
  informer->FilterSourceResponse(
      CreateDataSourceResposne(place_stats_with_error));
  informer->FilterWidgetsWithData({});
  EXPECT_TRUE(informer->HasData());

  informer->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["informers"].GetSize(), 1);

  auto response_informer = json_response["data"]["informers"][0]["payload"];
  EXPECT_TRUE(response_informer["background_color"].IsMissing());
  EXPECT_TRUE(response_informer["icon"].IsMissing());
  EXPECT_TRUE(response_informer["link"].IsMissing());
}

TEST(Informer, MaxOrders) {
  auto informer =
      GetWidget("id", {"Текст", {{"dark", "#ffffff"}, {"light", "#000000"}}},
                std::nullopt, std::nullopt, std::nullopt, {3});

  formats::json::ValueBuilder response;
  eats_layout_constructor::sources::DataSourceParams params;

  eats_surge::free_delivery::PlacesStats places_stats{
      {1,  // place_id
       {
           3,             // counter
           1,             // place_id
           "",            // first_order_at
           "",            // last_order_at
           std::nullopt,  // brand_id
           "retail",      // business_type
           std::nullopt   // delivery_type
       }}};
  eats_surge::free_delivery::PlacesStatsWithError place_stats_with_error{
      places_stats, false};

  EXPECT_FALSE(informer->HasData());
  informer->FillSourceRequestParams(params);
  informer->FilterSourceResponse(
      CreateDataSourceResposne(place_stats_with_error));
  informer->FilterWidgetsWithData({});
  EXPECT_FALSE(informer->HasData());
}
