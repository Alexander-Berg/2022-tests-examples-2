#include "timepickers.hpp"

#include <gtest/gtest.h>

#include <models/constructor/db_model.hpp>
#include <sources/catalog/catalog_data_source.hpp>
#include <userver/formats/json.hpp>
#include <widgets/timepickers/factory.hpp>
namespace {
using Response = eats_layout_constructor::sources::DataSourceResponses;

formats::json::Value GetWidgetData(const std::string& id,
                                   const std::string& title) {
  formats::json::ValueBuilder widget;
  widget["meta"] =
      formats::json::ValueBuilder{formats::json::Type::kObject}.ExtractValue();
  widget["id"] = id;
  widget["payload"]["title"] = title;
  widget["type"] = "timepickers";
  return widget.ExtractValue();
}

std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> GetWidget(
    const std::string& id, const std::string& title) {
  const auto widget_data = GetWidgetData(id, title);
  return eats_layout_constructor::widgets::timepickers::TimepickersFactory(
      eats_layout_constructor::models::constructor::WidgetTemplateName{},
      eats_layout_constructor::models::constructor::Meta{widget_data["meta"]},
      eats_layout_constructor::models::constructor::Payload{
          widget_data["payload"]},
      {}, widget_data["id"].As<std::string>());
}

Response GetSource() {
  using Catalog = eats_layout_constructor::sources::CatalogDataSource;
  static auto kResponse = Response{};
  if (kResponse.empty()) {
    formats::json::ValueBuilder source;
    source["timepicker"] = formats::common::Type::kArray;
    formats::json::ValueBuilder today;
    today.PushBack("2020-05-15T18:30:00+05:00");
    today.PushBack("2020-05-15T19:00:00+05:00");
    today.PushBack("2020-05-15T19:30:00+05:00");
    today.PushBack("2020-05-15T20:00:00+05:00");
    today.PushBack("2020-05-15T20:30:00+05:00");
    source["timepicker"].PushBack(today.ExtractValue());
    formats::json::ValueBuilder tomorrow;
    today.PushBack("2020-05-16T18:30:00+05:00");
    today.PushBack("2020-05-16T19:00:00+05:00");
    today.PushBack("2020-05-16T19:30:00+05:00");
    today.PushBack("2020-05-16T20:00:00+05:00");
    today.PushBack("2020-05-16T20:30:00+05:00");
    source["timepicker"].PushBack(tomorrow.ExtractValue());
    auto catalog_response =
        std::make_shared<Catalog::Response>(Catalog::Response{});
    catalog_response->timepicker = source.ExtractValue();
    kResponse[Catalog::kName] = catalog_response;
  }
  return kResponse;
}
}  // namespace

TEST(Timepickers, Simple) {
  auto timepickers = GetWidget("id", "Выбери время");

  formats::json::ValueBuilder response;
  auto source = GetSource();

  EXPECT_FALSE(timepickers->HasData());
  timepickers->FilterSourceResponse(source);
  EXPECT_TRUE(timepickers->HasData());

  timepickers->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["timepickers"].GetSize(), 1);
}

TEST(Timepickers, NoData) {
  auto timepickers = GetWidget("id", "Выбери время");

  formats::json::ValueBuilder response;

  EXPECT_FALSE(timepickers->HasData());
  EXPECT_NO_THROW(timepickers->FilterSourceResponse({}));
  EXPECT_FALSE(timepickers->HasData());

  EXPECT_NO_THROW(timepickers->UpdateLayout(response));

  auto json_response = response.ExtractValue();
  EXPECT_FALSE(json_response.HasMember("layout"));
  EXPECT_FALSE(json_response.HasMember("data"));
}
