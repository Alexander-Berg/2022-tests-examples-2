#include "banners.hpp"

#include <gtest/gtest.h>

#include <models/constructor/db_model.hpp>
#include <sources/banners/banners_data_source.hpp>

#include <set>

#include <userver/formats/json.hpp>
#include <widgets/banners/factory.hpp>
#include <widgets/layout_widget/params.hpp>

namespace {
namespace banners = eats_layout_constructor::widgets::banners;
using Response = eats_layout_constructor::sources::DataSourceResponses;

formats::json::Value GetWidgetData(
    const std::string& id, const std::string& title, banners::Format format,
    std::set<banners::BannertypesA> types = {}, std::set<int> banner_ids = {},
    std::set<int> exclude = {},
    std::optional<std::unordered_set<std::string>> depends_on_any =
        std::nullopt,
    std::optional<std::unordered_set<std::string>> not_show_with =
        std::nullopt) {
  formats::json::ValueBuilder widget;
  widget["meta"] =
      formats::json::ValueBuilder{formats::json::Type::kObject}.ExtractValue();
  widget["id"] = id;
  widget["payload"]["title"] = title;
  widget["type"] = "banners";

  for (auto type : types) {
    widget["meta"]["banner_types"].PushBack(banners::ToString(type));
  }

  for (auto banner_id : banner_ids) {
    widget["meta"]["banners_id"].PushBack(banner_id);
  }

  for (auto exclude_id : exclude) {
    widget["meta"]["exclude"].PushBack(exclude_id);
  }

  widget["meta"]["format"] = banners::ToString(format);

  if (depends_on_any.has_value()) {
    widget["meta"]["depends_on_any"] = depends_on_any.value();
  }
  if (not_show_with.has_value()) {
    widget["meta"]["not_show_with"] = not_show_with.value();
  }

  return widget.ExtractValue();
}

std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> GetWidget(
    const std::string& id, const std::string& title, banners::Format format,
    std::set<banners::BannertypesA> types = {}, std::set<int> banner_ids = {},
    std::set<int> exclude = {},
    std::optional<std::unordered_set<std::string>> depends_on_any =
        std::nullopt,
    std::optional<std::unordered_set<std::string>> not_show_with =
        std::nullopt) {
  const auto widget_data =
      GetWidgetData(id, title, format, types, banner_ids, exclude,
                    depends_on_any, not_show_with);
  return eats_layout_constructor::widgets::banners::BannersFactory(
      eats_layout_constructor::models::constructor::WidgetTemplateName{},
      eats_layout_constructor::models::constructor::Meta{widget_data["meta"]},
      eats_layout_constructor::models::constructor::Payload{
          widget_data["payload"]},
      {}, widget_data["id"].As<std::string>());
}

Response GetSource() {
  namespace sources = eats_layout_constructor::sources;
  using Banners = eats_layout_constructor::sources::BannersDataSource;
  using Banner = sources::banners::Banner;
  using Meta = sources::banners::Meta;
  using Kind = sources::banners::Kind;
  using Format = sources::banners::Format;
  static auto kResponse = Response{};
  if (kResponse.empty()) {
    auto banners_response =
        std::make_shared<Banners::Response>(Banners::Response{});
    banners_response->banners.push_back(
        Banner{Meta{
                   sources::BannerId(1),
                   std::nullopt,
                   std::nullopt,
                   Kind::kInfo,
                   {Format::kClassic},
                   1,
               },
               formats::json::FromString(R"=({"some" : "content_1"})=")});
    banners_response->banners.push_back(
        Banner{Meta{
                   sources::BannerId(2),
                   std::nullopt,
                   std::nullopt,
                   Kind::kPlace,
                   {Format::kShortcut},
                   2,
               },
               formats::json::FromString(R"=({"some" : "content_2"})=")});
    banners_response->banners.push_back(
        Banner{Meta{
                   sources::BannerId(3),
                   std::nullopt,
                   std::nullopt,
                   Kind::kCollection,
                   {Format::kClassic, Format::kShortcut},
                   3,
               },
               formats::json::FromString(R"=({"some" : "content_3"})=")});
    kResponse[Banners::kName] = banners_response;
  }
  return kResponse;
}

}  // namespace

TEST(Banners, Simple) {
  namespace widgets = eats_layout_constructor::widgets;
  auto banners = GetWidget("id", "Баннеры", banners::Format::kClassic);
  formats::json::ValueBuilder response;
  auto source = GetSource();

  EXPECT_FALSE(banners->HasData());
  banners->FilterSourceResponse(source);
  banners->FilterWidgetsWithData({});
  EXPECT_TRUE(banners->HasData());

  banners->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["layout"][0]["id"].As<std::string>(), "id");
  EXPECT_EQ(json_response["data"]["banners"].GetSize(), 1);
}

TEST(Banners, Kinds) {
  namespace widgets = eats_layout_constructor::widgets;
  auto banners = GetWidget(
      "id", "Баннеры", banners::Format::kClassic,
      {banners::BannertypesA::kCollection, banners::BannertypesA::kInfo});
  formats::json::ValueBuilder response;
  auto source = GetSource();

  EXPECT_FALSE(banners->HasData());
  banners->FilterSourceResponse(source);
  banners->FilterWidgetsWithData({});
  EXPECT_TRUE(banners->HasData());

  banners->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["data"]["banners"].GetSize(), 1);

  auto response_banners =
      json_response["data"]["banners"][0]["payload"]["banners"];
  EXPECT_EQ(response_banners.GetSize(), 2);
  EXPECT_EQ(response_banners[0]["some"].As<std::string>(), "content_1");
  EXPECT_EQ(response_banners[1]["some"].As<std::string>(), "content_3");
}

TEST(Banners, BannerIds) {
  namespace widgets = eats_layout_constructor::widgets;
  auto banners =
      GetWidget("id", "Баннеры", banners::Format::kClassic, {}, {1, 3});
  formats::json::ValueBuilder response;
  auto source = GetSource();

  EXPECT_FALSE(banners->HasData());
  banners->FilterSourceResponse(source);
  banners->FilterWidgetsWithData({});
  EXPECT_TRUE(banners->HasData());

  banners->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["data"]["banners"].GetSize(), 1);

  auto response_banners =
      json_response["data"]["banners"][0]["payload"]["banners"];
  EXPECT_EQ(response_banners.GetSize(), 2);
  EXPECT_EQ(response_banners[0]["some"].As<std::string>(), "content_1");
  EXPECT_EQ(response_banners[1]["some"].As<std::string>(), "content_3");
}

TEST(Banners, Excludes) {
  namespace widgets = eats_layout_constructor::widgets;
  auto banners =
      GetWidget("id", "Баннеры", banners::Format::kClassic, {}, {}, {1});
  formats::json::ValueBuilder response;
  auto source = GetSource();

  EXPECT_FALSE(banners->HasData());
  banners->FilterSourceResponse(source);
  banners->FilterWidgetsWithData({});
  EXPECT_TRUE(banners->HasData());

  banners->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["data"]["banners"].GetSize(), 1);

  auto response_banners =
      json_response["data"]["banners"][0]["payload"]["banners"];

  EXPECT_EQ(response_banners.GetSize(), 1);
  EXPECT_EQ(response_banners[0]["some"].As<std::string>(), "content_3");
}

TEST(Banners, FormatClassic) {
  namespace widgets = eats_layout_constructor::widgets;
  auto banners = GetWidget("id", "Баннеры", banners::Format::kClassic);
  formats::json::ValueBuilder response;
  auto source = GetSource();

  EXPECT_FALSE(banners->HasData());
  banners->FilterSourceResponse(source);
  banners->FilterWidgetsWithData({});
  EXPECT_TRUE(banners->HasData());

  banners->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["data"]["banners"].GetSize(), 1);

  auto response_banners =
      json_response["data"]["banners"][0]["payload"]["banners"];
  EXPECT_EQ(response_banners.GetSize(), 2);
  EXPECT_EQ(response_banners[0]["some"].As<std::string>(), "content_1");
  EXPECT_EQ(response_banners[1]["some"].As<std::string>(), "content_3");
}

TEST(Banners, FormatShortcut) {
  namespace widgets = eats_layout_constructor::widgets;
  auto banners = GetWidget("id", "Баннеры", banners::Format::kShortcut);
  formats::json::ValueBuilder response;
  auto source = GetSource();

  EXPECT_FALSE(banners->HasData());
  banners->FilterSourceResponse(source);
  banners->FilterWidgetsWithData({});
  EXPECT_TRUE(banners->HasData());

  banners->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["data"]["banners"].GetSize(), 1);

  auto response_banners =
      json_response["data"]["banners"][0]["payload"]["banners"];
  EXPECT_EQ(response_banners.GetSize(), 2);
  EXPECT_EQ(response_banners[0]["some"].As<std::string>(), "content_2");
  EXPECT_EQ(response_banners[1]["some"].As<std::string>(), "content_3");
}

TEST(Banners, NoData) {
  namespace widgets = eats_layout_constructor::widgets;
  auto banners = GetWidget("id", "Баннеры", banners::Format::kClassic);
  formats::json::ValueBuilder response;

  EXPECT_FALSE(banners->HasData());
  EXPECT_NO_THROW(banners->FilterSourceResponse({}));
  EXPECT_NO_THROW(banners->FilterWidgetsWithData({}));
  EXPECT_FALSE(banners->HasData());

  EXPECT_NO_THROW(banners->UpdateLayout(response));

  auto json_response = response.ExtractValue();
  EXPECT_FALSE(json_response.HasMember("layout"));
  EXPECT_FALSE(json_response.HasMember("data"));
}

TEST(Banners, DependsOnOnlyOne) {
  std::unordered_set<std::string> depends_on_any{"second", "third"};
  const auto banners = GetWidget("id", "Баннеры", banners::Format::kClassic, {},
                                 {}, {}, depends_on_any);
  EXPECT_FALSE(banners->HasData());

  const auto source = GetSource();
  banners->FilterSourceResponse(source);
  const std::unordered_set<std::string> widgets_with_data{"first", "second"};
  banners->FilterWidgetsWithData(widgets_with_data);
  EXPECT_TRUE(banners->HasData());

  formats::json::ValueBuilder response;
  EXPECT_NO_THROW(banners->UpdateLayout(response));

  const auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["banners"].GetSize(), 1);
}

TEST(Banners, DependsOnNonExisted) {
  std::unordered_set<std::string> depends_on_any{"third"};
  const auto banners = GetWidget("id", "Баннеры", banners::Format::kClassic, {},
                                 {}, {}, depends_on_any);
  EXPECT_FALSE(banners->HasData());

  const auto source = GetSource();
  banners->FilterSourceResponse(source);
  const std::unordered_set<std::string> widgets_with_data{"first", "second"};
  banners->FilterWidgetsWithData(widgets_with_data);
  EXPECT_FALSE(banners->HasData());

  formats::json::ValueBuilder response;
  EXPECT_NO_THROW(banners->UpdateLayout(response));

  const auto json_response = response.ExtractValue();
  EXPECT_FALSE(json_response.HasMember("layout"));
  EXPECT_FALSE(json_response.HasMember("data"));
}

TEST(Banners, DependsWithEmptySet) {
  std::unordered_set<std::string> depends_on_any{"third"};
  const auto banners = GetWidget("id", "Баннеры", banners::Format::kClassic, {},
                                 {}, {}, depends_on_any);
  EXPECT_FALSE(banners->HasData());

  const auto source = GetSource();
  banners->FilterSourceResponse(source);
  banners->FilterWidgetsWithData({});
  EXPECT_FALSE(banners->HasData());

  formats::json::ValueBuilder response;
  EXPECT_NO_THROW(banners->UpdateLayout(response));

  const auto json_response = response.ExtractValue();
  EXPECT_FALSE(json_response.HasMember("layout"));
  EXPECT_FALSE(json_response.HasMember("data"));
}

TEST(Banners, NotShowWithOnlyOne) {
  std::unordered_set<std::string> not_show_with{"third"};
  const auto banners = GetWidget("id", "Баннеры", banners::Format::kClassic, {},
                                 {}, {}, std::nullopt, not_show_with);
  EXPECT_FALSE(banners->HasData());

  const auto source = GetSource();
  banners->FilterSourceResponse(source);
  const std::unordered_set<std::string> widgets_with_data{"first", "second"};
  banners->FilterWidgetsWithData(widgets_with_data);
  EXPECT_TRUE(banners->HasData());

  formats::json::ValueBuilder response;
  EXPECT_NO_THROW(banners->UpdateLayout(response));

  const auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["banners"].GetSize(), 1);
}

TEST(Banners, NotShowWithExisted) {
  std::unordered_set<std::string> not_show_with{"second", "third"};
  const auto banners = GetWidget("id", "Баннеры", banners::Format::kClassic, {},
                                 {}, {}, std::nullopt, not_show_with);
  EXPECT_FALSE(banners->HasData());

  const auto source = GetSource();
  banners->FilterSourceResponse(source);
  const std::unordered_set<std::string> widgets_with_data{"first", "second"};
  banners->FilterWidgetsWithData(widgets_with_data);
  EXPECT_FALSE(banners->HasData());

  formats::json::ValueBuilder response;
  EXPECT_NO_THROW(banners->UpdateLayout(response));

  const auto json_response = response.ExtractValue();
  EXPECT_FALSE(json_response.HasMember("layout"));
  EXPECT_FALSE(json_response.HasMember("data"));
}

TEST(Banners, NotShowWithEmptySet) {
  std::unordered_set<std::string> not_show_with{"third"};
  const auto banners = GetWidget("id", "Баннеры", banners::Format::kClassic, {},
                                 {}, {}, std::nullopt, not_show_with);
  EXPECT_FALSE(banners->HasData());

  const auto source = GetSource();
  banners->FilterSourceResponse(source);
  banners->FilterWidgetsWithData({});
  EXPECT_TRUE(banners->HasData());

  formats::json::ValueBuilder response;
  EXPECT_NO_THROW(banners->UpdateLayout(response));

  const auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["banners"].GetSize(), 1);
}

TEST(Banners, DependsAndNotShowWithOnlyOne) {
  std::unordered_set<std::string> depends_on_any{"second", "third"};
  std::unordered_set<std::string> not_show_with{"third"};
  const auto banners = GetWidget("id", "Баннеры", banners::Format::kClassic, {},
                                 {}, {}, depends_on_any, not_show_with);
  EXPECT_FALSE(banners->HasData());

  const auto source = GetSource();
  banners->FilterSourceResponse(source);
  const std::unordered_set<std::string> widgets_with_data{"first", "second"};
  banners->FilterWidgetsWithData(widgets_with_data);
  EXPECT_TRUE(banners->HasData());

  formats::json::ValueBuilder response;
  EXPECT_NO_THROW(banners->UpdateLayout(response));

  const auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["banners"].GetSize(), 1);
}

TEST(Banners, DependsAndNotShowWithNotExisted) {
  std::unordered_set<std::string> depends_on_any{"third"};
  std::unordered_set<std::string> not_show_with{"third"};
  const auto banners = GetWidget("id", "Баннеры", banners::Format::kClassic, {},
                                 {}, {}, depends_on_any, not_show_with);
  EXPECT_FALSE(banners->HasData());

  const auto source = GetSource();
  banners->FilterSourceResponse(source);
  const std::unordered_set<std::string> widgets_with_data{"first", "second"};
  banners->FilterWidgetsWithData(widgets_with_data);
  EXPECT_FALSE(banners->HasData());

  formats::json::ValueBuilder response;
  EXPECT_NO_THROW(banners->UpdateLayout(response));

  const auto json_response = response.ExtractValue();
  EXPECT_FALSE(json_response.HasMember("layout"));
  EXPECT_FALSE(json_response.HasMember("data"));
}

TEST(Banners, DependsAndNotShowWithExisted) {
  std::unordered_set<std::string> depends_on_any{"second", "third"};
  std::unordered_set<std::string> not_show_with{"second", "third"};
  const auto banners = GetWidget("id", "Баннеры", banners::Format::kClassic, {},
                                 {}, {}, depends_on_any, not_show_with);
  EXPECT_FALSE(banners->HasData());

  const auto source = GetSource();
  banners->FilterSourceResponse(source);
  const std::unordered_set<std::string> widgets_with_data{"first", "second"};
  banners->FilterWidgetsWithData(widgets_with_data);
  EXPECT_FALSE(banners->HasData());

  formats::json::ValueBuilder response;
  EXPECT_NO_THROW(banners->UpdateLayout(response));

  const auto json_response = response.ExtractValue();
  EXPECT_FALSE(json_response.HasMember("layout"));
  EXPECT_FALSE(json_response.HasMember("data"));
}

TEST(Banners, DependsWithNotShowWithEmptySet) {
  std::unordered_set<std::string> depends_on_any{"third"};
  std::unordered_set<std::string> not_show_with{"third"};
  const auto banners = GetWidget("id", "Баннеры", banners::Format::kClassic, {},
                                 {}, {}, depends_on_any, not_show_with);
  EXPECT_FALSE(banners->HasData());

  const auto source = GetSource();
  banners->FilterSourceResponse(source);
  banners->FilterWidgetsWithData({});
  EXPECT_FALSE(banners->HasData());

  formats::json::ValueBuilder response;
  EXPECT_NO_THROW(banners->UpdateLayout(response));

  const auto json_response = response.ExtractValue();
  EXPECT_FALSE(json_response.HasMember("layout"));
  EXPECT_FALSE(json_response.HasMember("data"));
}
