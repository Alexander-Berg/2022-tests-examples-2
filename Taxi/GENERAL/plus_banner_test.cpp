#include "plus_banner.hpp"

#include <gtest/gtest.h>
#include <userver/formats/json/value_builder.hpp>

#include <sources/eats-plus/eats_plus_source.hpp>
#include <widgets/plus_banner/factory.hpp>

namespace {

using Response = eats_layout_constructor::sources::DataSourceResponses;
Response CreateDataSourceResposne(bool empty = false) {
  using EatsPlus = eats_layout_constructor::sources::eats_plus::DataSource;

  auto response = Response{};
  auto plus_response = std::make_shared<EatsPlus::Response>();
  if (!empty) {
    formats::json::ValueBuilder payload;
    payload["deeplink"] = "eda.yandex://plus/home";
    payload["icon_url"] = "asset://yandex_plus";
    payload["text_parts"] = formats::json::Type::kArray;

    {
      formats::json::ValueBuilder text_part;
      text_part["text"] = "Баланс в плюсе: ";
      payload["text_parts"].PushBack(text_part.ExtractValue());
    }

    {
      formats::json::ValueBuilder text_part;
      text_part["text"] = "-20234122 баллов";
      text_part["styles"]["rainbow"] = true;
      payload["text_parts"].PushBack(text_part.ExtractValue());
    }

    plus_response->banner = payload.ExtractValue();
  }

  response[EatsPlus::kName] = plus_response;

  return response;
}

std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> CreateWidget(
    std::string id, std::optional<std::string> title = std::nullopt) {
  formats::json::Value config;
  {
    formats::json::ValueBuilder builder;
    builder["payload"] = formats::json::Type::kObject;
    builder["meta"] = formats::json::Type::kObject;
    if (title.has_value()) {
      builder["payload"]["title"] = *title;
    }

    config = builder.ExtractValue();
  }

  return eats_layout_constructor::widgets::plus_banner::PlusBannerFactory(
      eats_layout_constructor::models::constructor::WidgetTemplateName{},
      eats_layout_constructor::models::constructor::Meta{config["meta"]},
      eats_layout_constructor::models::constructor::Payload{config["payload"]},
      {}, id);
}

TEST(PlusBanner, Response) {
  const std::string widget_id = "fake_widget_id";
  const std::string widget_title = "Заголовок виджета";

  auto widget = CreateWidget(widget_id, widget_title);
  auto source = CreateDataSourceResposne(false);

  formats::json::ValueBuilder response;

  EXPECT_FALSE(widget->HasData());
  widget->FilterSourceResponse(source);
  EXPECT_TRUE(widget->HasData());

  widget->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  ASSERT_FALSE(json_response["layout"].IsMissing());

  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["layout"][0]["type"].As<std::string>(),
            "yandex_plus_banner");
  EXPECT_EQ(json_response["layout"][0]["id"].As<std::string>(), widget_id);
  EXPECT_EQ(json_response["layout"][0]["payload"]["title"].As<std::string>(),
            widget_title);

  {
    ASSERT_FALSE(json_response["data"]["yandex_plus_banners"].IsMissing());
    ASSERT_EQ(json_response["data"]["yandex_plus_banners"].GetSize(), 1);
    auto data = json_response["data"]["yandex_plus_banners"][0];

    EXPECT_EQ(data["id"].As<std::string>(), widget_id);
    ASSERT_FALSE(data["payload"]["text_parts"].IsMissing());
  }
}

TEST(PlusBanner, EmptyResponse) {
  const std::string widget_id = "fake_widget_id";
  const std::string widget_title = "Заголовок виджета";

  auto widget = CreateWidget(widget_id, widget_title);
  auto source = CreateDataSourceResposne(true);

  formats::json::ValueBuilder response;

  EXPECT_FALSE(widget->HasData());
  widget->FilterSourceResponse(source);
  EXPECT_FALSE(widget->HasData());

  widget->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  ASSERT_TRUE(json_response["layout"].IsMissing());
  ASSERT_TRUE(json_response["data"].IsMissing());
}

}  // namespace
