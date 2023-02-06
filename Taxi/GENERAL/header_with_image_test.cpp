#include "header_with_image.hpp"

#include <gtest/gtest.h>
#include <widgets/header_with_image/factory.hpp>

namespace {

namespace header_with_image =
    eats_layout_constructor::widgets::header_with_image;
using Response = eats_layout_constructor::sources::DataSourceResponses;

formats::json::Value GetWidgetData(
    const std::string& id, const header_with_image::ThemedImage& image_url,
    std::optional<header_with_image::ThemedImage> right_button_image =
        std::nullopt,
    std::optional<header_with_image::Deeplink> right_button_deeplink =
        std::nullopt,
    std::unordered_set<std::string> depends_on_any = {}) {
  formats::json::ValueBuilder widget;

  widget["id"] = id;
  widget["payload"] = formats::json::Type::kObject;

  widget["type"] = "header_with_image";
  header_with_image::WidgetMeta widget_meta{
      right_button_image, right_button_deeplink, image_url,
      std::vector<std::string>(depends_on_any.begin(), depends_on_any.end())};
  widget["meta"] = formats::json::ValueBuilder{widget_meta};
  return widget.ExtractValue();
}

std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> GetWidget(
    const std::string& id, const header_with_image::ThemedImage& image_url,
    std::optional<header_with_image::ThemedImage> right_button_image =
        std::nullopt,
    std::optional<header_with_image::Deeplink> right_button_deeplink =
        std::nullopt,
    std::unordered_set<std::string> depends_on_any = {}) {
  const auto widget_data = GetWidgetData(id, image_url, right_button_image,
                                         right_button_deeplink, depends_on_any);

  return header_with_image::HeaderWithImageFactory(
      eats_layout_constructor::models::constructor::WidgetTemplateName{},
      eats_layout_constructor::models::constructor::Meta{widget_data["meta"]},
      eats_layout_constructor::models::constructor::Payload{
          widget_data["payload"]},
      {}, widget_data["id"].As<std::string>());
}

}  // namespace

/// Проверка на корректность заполнения полей
TEST(HeaderWithImage, Simple) {
  auto header =
      GetWidget("id", {"image_light", "image_dark"},
                header_with_image::ThemedImage{"right_button_image_light",
                                               "right_button_image_dark"},
                header_with_image::Deeplink{"right_button_deeplink_app",
                                            "right_button_deeplink_web"});

  formats::json::ValueBuilder response;

  EXPECT_TRUE(header->HasData());
  header->FilterSourceResponse({});
  header->FilterWidgetsWithData({});
  EXPECT_TRUE(header->HasData());

  header->UpdateLayout(response);

  auto json_response = response.ExtractValue();

  EXPECT_EQ(json_response["data"]["headers_with_image"].GetSize(), 1);

  auto response_header =
      json_response["data"]["headers_with_image"][0]["payload"];
  EXPECT_EQ(response_header["right_button_image"]["light"].As<std::string>(),
            "right_button_image_light");
  EXPECT_EQ(response_header["right_button_image"]["dark"].As<std::string>(),
            "right_button_image_dark");
  EXPECT_EQ(response_header["right_button_deeplink"]["app"].As<std::string>(),
            "right_button_deeplink_app");
  EXPECT_EQ(response_header["right_button_deeplink"]["web"].As<std::string>(),
            "right_button_deeplink_web");
  EXPECT_EQ(response_header["image_url"]["light"].As<std::string>(),
            "image_light");
  EXPECT_EQ(response_header["image_url"]["dark"].As<std::string>(),
            "image_dark");
}

/// Проверка на отображение виджета, если виджет от которого он зависит есть
TEST(HeaderWithImage, DependsOnExisted) {
  std::unordered_set<std::string> depends_on_any{"first"};
  auto header =
      GetWidget("id", {"image_light", "image_dark"},
                header_with_image::ThemedImage{"right_button_image_light",
                                               "right_button_image_dark"},
                header_with_image::Deeplink{"right_button_deeplink_app",
                                            "right_button_deeplink_web"},
                depends_on_any);

  std::unordered_set<std::string> widgets_with_data{"first"};

  formats::json::ValueBuilder response;

  EXPECT_FALSE(header->HasData());
  header->FilterSourceResponse({});
  header->FilterWidgetsWithData(widgets_with_data);
  EXPECT_TRUE(header->HasData());

  header->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["data"]["headers_with_image"].GetSize(), 1);
}

/// Проверка на отображение виджета, если один из нескольких виджетов
/// от которых он зависит есть
TEST(HeaderWithImage, DependsOnOnlyOne) {
  std::unordered_set<std::string> depends_on_any{"second", "third"};
  auto header =
      GetWidget("id", {"image_light", "image_dark"},
                header_with_image::ThemedImage{"right_button_image_light",
                                               "right_button_image_dark"},
                header_with_image::Deeplink{"right_button_deeplink_app",
                                            "right_button_deeplink_web"},
                depends_on_any);

  std::unordered_set<std::string> widgets_with_data{"first", "second"};

  formats::json::ValueBuilder response;

  EXPECT_FALSE(header->HasData());
  header->FilterSourceResponse({});
  header->FilterWidgetsWithData(widgets_with_data);
  EXPECT_TRUE(header->HasData());

  header->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["data"]["headers_with_image"].GetSize(), 1);
}

/// Проверка что виджет не отображается, если виджета, от которого он зависит
/// нет
TEST(HeaderWithImage, DependsOnNonExisted) {
  std::unordered_set<std::string> depends_on_any{"my_non_existed_test_id"};
  auto header =
      GetWidget("id", {"image_light", "image_dark"},
                header_with_image::ThemedImage{"right_button_image_light",
                                               "right_button_image_dark"},
                header_with_image::Deeplink{"right_button_deeplink_app",
                                            "right_button_deeplink_web"},
                depends_on_any);

  std::unordered_set<std::string> widgets_with_data{"first"};

  formats::json::ValueBuilder response;

  EXPECT_FALSE(header->HasData());
  header->FilterSourceResponse({});
  header->FilterWidgetsWithData(widgets_with_data);
  EXPECT_FALSE(header->HasData());

  header->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_FALSE(json_response.HasMember("layout"));
  EXPECT_FALSE(json_response.HasMember("data"));
}

/// Проверка что виджет не отображает необязательные поля
TEST(HeaderWithImage, OnlyReqiredData) {
  auto header = GetWidget("id", {"image_light", "image_dark"});

  formats::json::ValueBuilder response;

  EXPECT_TRUE(header->HasData());
  EXPECT_NO_THROW(header->FilterSourceResponse({}));
  EXPECT_NO_THROW(header->FilterWidgetsWithData({}));
  EXPECT_TRUE(header->HasData());

  EXPECT_NO_THROW(header->UpdateLayout(response));

  auto json_response = response.ExtractValue();

  EXPECT_TRUE(json_response.HasMember("layout"));
  EXPECT_TRUE(json_response.HasMember("data"));

  auto response_header =
      json_response["data"]["headers_with_image"][0]["payload"];

  EXPECT_TRUE(response_header.HasMember("image_url"));

  EXPECT_FALSE(response_header.HasMember("right_button_image"));
  EXPECT_FALSE(response_header.HasMember("right_button_deeplink"));
}
