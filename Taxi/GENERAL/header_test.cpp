#include "header.hpp"

#include <gtest/gtest.h>
#include <widgets/header/factory.hpp>

namespace {

namespace header = eats_layout_constructor::widgets::header;
using Response = eats_layout_constructor::sources::DataSourceResponses;

formats::json::Value GetWidgetData(
    const std::string& id, const std::string& title, const std::string& text,
    // std::optional<header::Styles> styles = std::nullopt,
    std::optional<std::string> styles = std::nullopt,
    // std::optional<header::Button> button = std::nullopt,
    std::optional<std::string> button = std::nullopt,
    std::optional<std::unordered_set<std::string>> depends_on_any =
        std::nullopt) {
  formats::json::ValueBuilder widget;
  widget["id"] = id;
  widget["payload"]["title"] = title;
  widget["type"] = "header";
  widget["meta"] = formats::json::Type::kObject;

  widget["meta"]["text"] = text;
  if (styles.has_value()) {
    widget["meta"]["styles_json"] = styles.value();
  }
  if (button.has_value()) {
    widget["meta"]["button_json"] = button.value();
  }
  if (depends_on_any.has_value()) {
    widget["meta"]["depends_on_any"] = depends_on_any.value();
  }

  return widget.ExtractValue();
}

std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> GetWidget(
    const std::string& id, const std::string& title, const std::string& text,
    // std::optional<header::Styles> styles = std::nullopt,
    std::optional<std::string> styles = std::nullopt,
    // std::optional<header::Button> button = std::nullopt,
    std::optional<std::string> button = std::nullopt,
    std::optional<std::unordered_set<std::string>> depends_on_any =
        std::nullopt) {
  const auto widget_data =
      GetWidgetData(id, title, text, styles, button, depends_on_any);

  return eats_layout_constructor::widgets::header::HeaderFactory(
      eats_layout_constructor::models::constructor::WidgetTemplateName{},
      eats_layout_constructor::models::constructor::Meta{widget_data["meta"]},
      eats_layout_constructor::models::constructor::Payload{
          widget_data["payload"]},
      {}, widget_data["id"].As<std::string>());
}

}  // namespace

TEST(Header, Simple) {
  auto header = GetWidget("id", "Продукты", "продукты");

  formats::json::ValueBuilder response;

  EXPECT_TRUE(header->HasData());
  header->FilterSourceResponse({});
  header->FilterWidgetsWithData({});
  EXPECT_TRUE(header->HasData());

  header->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["headers"].GetSize(), 1);

  auto response_header = json_response["data"]["headers"][0]["payload"];
  EXPECT_EQ(response_header["text"].As<std::string>(), "продукты");

  // We expect an empty object in a "styles".
  EXPECT_TRUE(response_header.HasMember("styles"));
  EXPECT_TRUE(response_header["styles"].IsEmpty());

  EXPECT_FALSE(response_header.HasMember("button"));
}

TEST(Header, BoldStyle) {
  auto styles = "{\"bold\": true}";
  auto header = GetWidget("id", "Продукты", "продукты", styles);

  formats::json::ValueBuilder response;

  EXPECT_TRUE(header->HasData());
  header->FilterSourceResponse({});
  header->FilterWidgetsWithData({});
  EXPECT_TRUE(header->HasData());

  header->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["headers"].GetSize(), 1);

  auto response_header = json_response["data"]["headers"][0]["payload"];
  EXPECT_EQ(response_header["text"].As<std::string>(), "продукты");

  EXPECT_TRUE(response_header["styles"]["bold"].As<bool>());

  EXPECT_FALSE(response_header.HasMember("button"));
}

TEST(Header, WithButton) {
  auto button =
      "{\"text\": \"все\", \"deeplink\": \"eda.yandex://collections/shops\"}";
  auto header = GetWidget("id", "Продукты", "продукты", std::nullopt, button);

  formats::json::ValueBuilder response;

  EXPECT_TRUE(header->HasData());
  header->FilterSourceResponse({});
  header->FilterWidgetsWithData({});
  EXPECT_TRUE(header->HasData());

  header->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["headers"].GetSize(), 1);

  auto response_header = json_response["data"]["headers"][0]["payload"];
  EXPECT_EQ(response_header["text"].As<std::string>(), "продукты");

  EXPECT_TRUE(response_header.HasMember("styles"));
  EXPECT_TRUE(response_header["styles"].IsEmpty());

  EXPECT_EQ(response_header["button"]["text"].As<std::string>(), "все");
  EXPECT_EQ(response_header["button"]["deeplink"].As<std::string>(),
            "eda.yandex://collections/shops");
}

TEST(Header, BrokenStyles) {
  auto styles = "{\"bold\": true";
  auto header = GetWidget("id", "Продукты", "продукты", styles);

  formats::json::ValueBuilder response;

  EXPECT_TRUE(header->HasData());
  header->FilterSourceResponse({});
  header->FilterWidgetsWithData({});
  EXPECT_TRUE(header->HasData());

  EXPECT_NO_THROW(header->UpdateLayout(response));

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["headers"].GetSize(), 1);

  auto response_header = json_response["data"]["headers"][0]["payload"];
  EXPECT_EQ(response_header["text"].As<std::string>(), "продукты");

  EXPECT_TRUE(response_header.HasMember("styles"));
  EXPECT_TRUE(response_header["styles"].IsEmpty());

  EXPECT_FALSE(response_header.HasMember("button"));
}

TEST(Header, BrokenButton) {
  auto button = "{\"text\": \"все\", \"deeplink\": ";
  auto header = GetWidget("id", "Продукты", "продукты", std::nullopt, button);

  formats::json::ValueBuilder response;

  EXPECT_TRUE(header->HasData());
  header->FilterSourceResponse({});
  header->FilterWidgetsWithData({});
  EXPECT_TRUE(header->HasData());

  EXPECT_NO_THROW(header->UpdateLayout(response));

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["headers"].GetSize(), 1);

  auto response_header = json_response["data"]["headers"][0]["payload"];
  EXPECT_EQ(response_header["text"].As<std::string>(), "продукты");

  EXPECT_TRUE(response_header.HasMember("styles"));
  EXPECT_TRUE(response_header["styles"].IsEmpty());

  EXPECT_FALSE(response_header.HasMember("button"));
}

TEST(Header, DependsOnExisted) {
  std::unordered_set<std::string> depends_on_any{"first"};
  auto header = GetWidget("id", "Продукты", "продукты", std::nullopt,
                          std::nullopt, depends_on_any);

  std::unordered_set<std::string> widgets_with_data{"first"};

  formats::json::ValueBuilder response;

  EXPECT_FALSE(header->HasData());
  header->FilterSourceResponse({});
  header->FilterWidgetsWithData(widgets_with_data);
  EXPECT_TRUE(header->HasData());

  header->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["headers"].GetSize(), 1);
}

TEST(Header, DependsOnOnlyOne) {
  std::unordered_set<std::string> depends_on_any{"second", "third"};
  auto header = GetWidget("id", "Продукты", "продукты", std::nullopt,
                          std::nullopt, depends_on_any);

  std::unordered_set<std::string> widgets_with_data{"first", "second"};

  formats::json::ValueBuilder response;

  EXPECT_FALSE(header->HasData());
  header->FilterSourceResponse({});
  header->FilterWidgetsWithData(widgets_with_data);
  EXPECT_TRUE(header->HasData());

  header->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["headers"].GetSize(), 1);
}

TEST(Header, DependsOnNonExisted) {
  std::unordered_set<std::string> depends_on_any{"my_non_existed_test_id"};
  auto header = GetWidget("id", "Продукты", "продукты", std::nullopt,
                          std::nullopt, depends_on_any);

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

TEST(Header, DependsWithEmptySet) {
  std::unordered_set<std::string> depends_on_any{"my_non_existed_test_id"};
  auto header = GetWidget("id", "Продукты", "продукты", std::nullopt,
                          std::nullopt, depends_on_any);

  std::unordered_set<std::string> widgets_with_data{};

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

TEST(Header, NoData) {
  auto header = GetWidget("id", "Продукты", "продукты");

  formats::json::ValueBuilder response;

  EXPECT_TRUE(header->HasData());
  EXPECT_NO_THROW(header->FilterSourceResponse({}));
  EXPECT_NO_THROW(header->FilterWidgetsWithData({}));
  EXPECT_TRUE(header->HasData());

  EXPECT_NO_THROW(header->UpdateLayout(response));

  auto json_response = response.ExtractValue();
  EXPECT_TRUE(json_response.HasMember("layout"));
  EXPECT_TRUE(json_response.HasMember("data"));
}
