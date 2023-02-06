#include <gtest/gtest.h>

#include <widgets/turbo_buttons/button.hpp>

namespace eats_layout_constructor::widgets::turbo_buttons {

TEST(Button, IsValid) {
  // Проверяет валидацию кнопки

  Button button;

  // По умолчанию кнопка невалидная
  ASSERT_FALSE(button.IsValid());

  button.SetName("name");
  button.SetAppLink("link");
  // Имени и ссылки достаточно, чтобы считать кнопку валидной
  ASSERT_TRUE(button.IsValid());
}

}  // namespace eats_layout_constructor::widgets::turbo_buttons
