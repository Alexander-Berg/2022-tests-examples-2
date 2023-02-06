#include "filters.hpp"

#include <gtest/gtest.h>

#include <models/constructor/db_model.hpp>
#include <sources/catalog/catalog_data_source.hpp>
#include <userver/formats/json.hpp>
#include <widgets/filters/factory.hpp>
#include <widgets/layout_widget/params.hpp>

namespace {
using Response = eats_layout_constructor::sources::DataSourceResponses;

formats::json::Value GetWidgetData(const std::string& id,
                                   const std::string& title) {
  formats::json::ValueBuilder widget;
  widget["meta"] =
      formats::json::ValueBuilder{formats::json::Type::kObject}.ExtractValue();
  widget["id"] = id;
  widget["payload"]["title"] = title;
  widget["type"] = "filters";
  return widget.ExtractValue();
}

std::shared_ptr<eats_layout_constructor::widgets::LayoutWidget> GetWidget(
    const std::string& id, const std::string& title) {
  const auto widget_data = GetWidgetData(id, title);
  return eats_layout_constructor::widgets::filters::FiltersFactory(
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
    formats::json::ValueBuilder filters{formats::common::Type::kObject};
    formats::json::ValueBuilder list{formats::common::Type::kArray};
    formats::json::ValueBuilder shaverma;
    shaverma["slug"] = "shaverma";
    shaverma["name"] = "Шаверма";
    shaverma["genitive"] = "шавермы";
    shaverma["photo_uri"] =
        "/images/1368744/aafb68cebeb3e0edf6eb5aa73d80faf6-{w}x{h}.jpg";
    shaverma["picture_uri"] =
        "/images/1368744/7eb79169054839e801225ebcdcc22c13.png";
    shaverma["promo_photo_uri"] =
        "/images/1387779/ebc4de93763e64d978f2012706fd9b2f-{w}x{h}.png";
    list.PushBack(shaverma.ExtractValue());

    formats::json::ValueBuilder shashlyk;
    shashlyk["slug"] = "shashlyk";
    shashlyk["name"] = "Шашлык";
    shashlyk["genitive"] = "шашлыка";
    shashlyk["photo_uri"] =
        "/images/1380157/f82530e5ed9ede1aa310e830eca7cbc8-{w}x{h}.jpg";
    shashlyk["picture_uri"] =
        "/images/1368744/318909aa345cabca778fded1d309c8de.png";
    shashlyk["promo_photo_uri"] =
        "/images/1387779/3578a3519e07f6e4f85a1b66d48cce71-{w}x{h}.png";
    list.PushBack(shashlyk.ExtractValue());

    formats::json::ValueBuilder gruzinskaya;
    gruzinskaya["slug"] = "gruzinskaya";
    gruzinskaya["name"] = "Грузинская";
    gruzinskaya["genitive"] = "блюд грузинской кухни";
    gruzinskaya["photo_uri"] =
        "/images/1380157/7261a46c7ee50edb6208bb58d07a47a9-{w}x{h}.jpg";
    gruzinskaya["picture_uri"] =
        "/images/1387779/d592dc20250aa916ce89d1162941d2c3.png";
    gruzinskaya["promo_photo_uri"] =
        "/images/1387779/9c1ca1a6878c6aedf6a01bb5b7c90c5a-{w}x{h}.png";
    list.PushBack(gruzinskaya.ExtractValue());

    filters["list"] = list;
    auto catalog_response =
        std::make_shared<Catalog::Response>(Catalog::Response{});
    catalog_response->filters = filters.ExtractValue();
    kResponse[Catalog::kName] = catalog_response;
  }
  return kResponse;
}

}  // namespace

TEST(Filters, Simple) {
  namespace widgets = eats_layout_constructor::widgets;
  auto filters = GetWidget("id", "Быстрые фильтры");
  formats::json::ValueBuilder response;
  auto source = GetSource();

  EXPECT_FALSE(filters->HasData());
  filters->FilterSourceResponse(source);
  EXPECT_TRUE(filters->HasData());

  filters->UpdateLayout(response);

  auto json_response = response.ExtractValue();
  EXPECT_EQ(json_response["layout"].GetSize(), 1);
  EXPECT_EQ(json_response["layout"][0]["id"].As<std::string>(), "id");
  EXPECT_EQ(json_response["data"]["filters"].GetSize(), 1);
}

TEST(Filters, NoData) {
  namespace widgets = eats_layout_constructor::widgets;
  auto filters = GetWidget("id", "Быстрые фильтры");
  formats::json::ValueBuilder response;

  EXPECT_FALSE(filters->HasData());
  EXPECT_NO_THROW(filters->FilterSourceResponse({}));
  EXPECT_FALSE(filters->HasData());

  EXPECT_NO_THROW(filters->UpdateLayout(response));

  auto json_response = response.ExtractValue();
  EXPECT_FALSE(json_response.HasMember("layout"));
  EXPECT_FALSE(json_response.HasMember("data"));
}
