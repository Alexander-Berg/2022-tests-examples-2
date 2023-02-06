#include <gtest/gtest.h>

#include <unordered_set>

#include <userver/formats/json/value_builder.hpp>
#include <userver/utils/algo.hpp>

#include <sources/banners/banners_data_source.hpp>
#include <widgets/high_banners_carousel/factory.hpp>
#include <widgets/layout_widget/layout_widget.hpp>
#include <widgets/layout_widget/params.hpp>

namespace eats_layout_constructor::widgets {

namespace {

std::shared_ptr<LayoutWidget> GetWidget(
    const std::string& id, const std::unordered_set<std::string>& experiments) {
  formats::json::ValueBuilder meta{formats::common::Type::kObject};
  formats::json::ValueBuilder exps{formats::common::Type::kArray};
  for (const auto& exp : experiments) {
    exps.PushBack(exp);
  }
  meta["experiments"] = std::move(exps);

  return high_banners_carousel::HighBannersCarouselFactory(
      eats_layout_constructor::models::constructor::WidgetTemplateName{},
      models::constructor::Meta{meta.ExtractValue()},
      models::constructor::Payload{}, {}, id);
}

}  // namespace

TEST(HighBannersCarousel, Generic) {
  // Проверяет общий случай, что запрос за баннерами корректно заполняется
  // и ответ перекладывается в ответ layout

  static const std::unordered_set<std::string> kExps{"exp1", "exp2"};
  static const std::string kBlockId = "exp1_exp2";

  auto widget = GetWidget("id", kExps);
  ASSERT_NE(widget, nullptr);

  sources::DataSourceParams source_params;
  widget->FillSourceRequestParams(source_params);

  const auto banners_params =
      std::any_cast<sources::banners::Params>(source_params["banners"]);
  ASSERT_FALSE(banners_params.blocks.empty());
  ASSERT_EQ(banners_params.blocks.size(), 1);

  const auto* block = ::utils::FindOrNullptr(banners_params.blocks, kBlockId);
  ASSERT_NE(block, nullptr);
  ASSERT_EQ(block->block_type,
            sources::banners::BlockType::kHighBannersCarousel);
  ASSERT_EQ(block->experiments, kExps);

  sources::DataSourceResponses response{};
  auto banners_response =
      std::make_shared<sources::BannersDataSource::Response>();
  auto& response_block = banners_response->blocks[kBlockId];
  response_block.block_type = sources::banners::BlockType::kHighBannersCarousel;
  formats::json::ValueBuilder payload{formats::common::Type::kObject};
  payload["key"] = "test_value";
  response_block.payload = payload.ExtractValue();
  response[sources::BannersDataSource::kName] = std::move(banners_response);
  widget->FilterSourceResponse(response);

  formats::json::ValueBuilder layout{};
  widget->UpdateLayout(layout);

  auto result = layout.ExtractValue();
  const auto high_banners_carousel = result["data"]["high_banners_carousel"];
  ASSERT_EQ(high_banners_carousel.GetSize(), 1);

  auto widget_payload = high_banners_carousel[0]["payload"];
  ASSERT_TRUE(widget_payload.IsObject());
  ASSERT_EQ(widget_payload["key"].As<std::string>(), "test_value");
};

TEST(HighBannersCarousel, NoBlock) {
  // Проверяем случай, когда в ответе баннеров нет блока,
  // ожидаем HasData() == false и UpdateData() ничего не сгенерирует

  static const std::unordered_set<std::string> kExps{"exp1", "exp2"};

  auto widget = GetWidget("id", kExps);
  ASSERT_NE(widget, nullptr);

  sources::DataSourceParams source_params;
  widget->FillSourceRequestParams(source_params);

  sources::DataSourceResponses response{};
  auto banners_response =
      std::make_shared<sources::BannersDataSource::Response>();
  response[sources::BannersDataSource::kName] = std::move(banners_response);
  widget->FilterSourceResponse(response);

  ASSERT_FALSE(widget->HasData());

  formats::json::ValueBuilder layout{};
  widget->UpdateLayout(layout);
  auto result = layout.ExtractValue();
  ASSERT_TRUE(result.IsEmpty());
};

}  // namespace eats_layout_constructor::widgets
