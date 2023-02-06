#include "sorts.hpp"

#include <gtest/gtest.h>

#include <models/constructor/db_model.hpp>
#include <sources/catalog/catalog_data_source.hpp>
#include <userver/formats/json.hpp>
#include <widgets/sorts/factory.hpp>

namespace {
using Response = eats_layout_constructor::sources::DataSourceResponses;

formats::json::Value GetWidgetData(const std::string& id,
                                   const std::string& title) {
  formats::json::ValueBuilder widget;
  widget["meta"] =
      formats::json::ValueBuilder{formats::json::Type::kObject}.ExtractValue();
  widget["id"] = id;
  widget["payload"]["title"] = title;
  widget["type"] = "sorts";
  return widget.ExtractValue();
}

std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> GetWidget(
    const std::string& id, const std::string& title) {
  const auto widget_data = GetWidgetData(id, title);
  return eats_layout_constructor::widgets::sorts::SortsFactory(
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
    source["sort"]["current"] = "default";
    source["sort"]["default"] = "default";
    source["sort"]["list"] = formats::common::Type::kArray;
    formats::json::ValueBuilder default_sort;
    default_sort["description"] = "Доверюсь вам";
    default_sort["slug"] = "default";
    source["sort"]["list"].PushBack(default_sort.ExtractValue());
    formats::json::ValueBuilder high_rating;
    high_rating["description"] = "high_rating";
    high_rating["slug"] = "high_rating";
    source["sort"]["list"].PushBack(high_rating.ExtractValue());
    auto catalog_response =
        std::make_shared<Catalog::Response>(Catalog::Response{});
    catalog_response->sort = source.ExtractValue();
    kResponse[Catalog::kName] = catalog_response;
  }
  return kResponse;
}

}  // namespace

TEST(Sorts, Simple) {
  auto sorts = GetWidget("id", "Сортировки");
  formats::json::ValueBuilder response;
  auto source = GetSource();

  EXPECT_FALSE(sorts->HasData());
  sorts->FilterSourceResponse(source);
  EXPECT_TRUE(sorts->HasData());

  sorts->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["data"]["sorts"].GetSize(), 1);
}

TEST(Sorts, NoData) {
  auto sorts = GetWidget("id", "Сортировки");

  formats::json::ValueBuilder response;

  EXPECT_FALSE(sorts->HasData());
  EXPECT_NO_THROW(sorts->FilterSourceResponse({}));
  EXPECT_FALSE(sorts->HasData());

  EXPECT_NO_THROW(sorts->UpdateLayout(response));

  auto json_response = response.ExtractValue();
  EXPECT_FALSE(json_response.HasMember("layout"));
  EXPECT_FALSE(json_response.HasMember("data"));
}
