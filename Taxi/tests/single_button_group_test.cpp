#include <gtest/gtest.h>

#include <widgets/turbo_buttons/single_button_group.hpp>

#include "utils_test.hpp"

namespace eats_layout_constructor::widgets::turbo_buttons::tests {

TEST(SingleButtonGroup, Generic) {
  // Проверяет общий случай перекладвания конфига в кнопку
  SingleButtonParams params{};
  params.name = "my button";
  params.app_link = "my/link";
  params.icon = "my/icon";

  SingleButtonGroup group(params);

  auto builder = Render(group);
  auto result = builder.As<std::vector<::handlers::TurboButton>>();

  ASSERT_EQ(result.size(), 1);
  const auto& button = result.front();
  ASSERT_EQ(button.name, params.name);
  ASSERT_EQ(button.icon, params.icon);
  ASSERT_EQ(button.app_link, params.app_link);
}

TEST(SingleButtonGroup, WithDescription) {
  // Проверяет, что описание корректно заполняется
  SingleButtonParams params{};
  params.name = "my button";
  params.app_link = "my/link";
  params.icon = "my/icon";
  auto& description = params.description.emplace();
  description.text = "my_description";
  description.colors.light = "light";
  description.colors.dark = "dark";

  SingleButtonGroup group(params);

  auto builder = Render(group);
  auto result = builder.As<std::vector<::handlers::TurboButton>>();

  ASSERT_EQ(result.size(), 1);
  const auto& button = result.front();
  ASSERT_EQ(button.name, params.name);
  ASSERT_EQ(button.icon, params.icon);
  ASSERT_EQ(button.app_link, params.app_link);

  ASSERT_EQ(button.description.value().text, params.description.value().text);
  AssertColor(button.description.value().color,
              params.description.value().colors.light,
              params.description.value().colors.dark);
}

}  // namespace eats_layout_constructor::widgets::turbo_buttons::tests
