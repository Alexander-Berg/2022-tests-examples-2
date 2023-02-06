#include <gtest/gtest.h>

#include <widgets/search_bar/factory.hpp>

namespace eats_layout_constructor::widgets {

namespace {

std::shared_ptr<LayoutWidget> GetWidget(const std::string& id,
                                        const std::string& placeholder_text) {
  search_bar::WidgetMeta meta{};
  meta.placeholder.text = placeholder_text;
  return search_bar::SearchBarFactory(
      eats_layout_constructor::models::constructor::WidgetTemplateName{},
      models::constructor::Meta{
          formats::json::ValueBuilder{std::move(meta)}.ExtractValue()},
      models::constructor::Payload{}, {}, id);
}

}  // namespace

TEST(SearchBar, Generic) {
  // Проверяет общий случай
  // перекладывания текста из
  // настроек в ответ

  const static std::string kPlaceholderText = "Search for food";

  auto widget = GetWidget("id", kPlaceholderText);
  ASSERT_NE(widget, nullptr);

  ASSERT_TRUE(widget->HasData());

  formats::json::ValueBuilder layout{};
  widget->UpdateLayout(layout);

  const auto result = layout.ExtractValue();
  const auto search_bar = result["data"]["search_bar"];
  ASSERT_EQ(search_bar.GetSize(), 1);

  const auto payload = search_bar[0]["payload"];
  ASSERT_TRUE(payload.IsObject());

  const auto placeholder = payload["placeholder"];
  ASSERT_TRUE(placeholder.IsObject());

  ASSERT_EQ(placeholder["text"].As<std::string>(), kPlaceholderText);
};

}  // namespace eats_layout_constructor::widgets
