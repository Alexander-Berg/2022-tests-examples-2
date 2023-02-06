#include <userver/utest/utest.hpp>

#include <clients/eats-restapp-tg-bot/client_gmock.hpp>
#include <components/telegram.hpp>

namespace testing {

using ::eats_restapp_communications::components::telegram::ComponentImpl;
using ::eats_restapp_communications::components::telegram::detail::
    ConfigTelegramSettings;
using ::eats_restapp_communications::components::telegram::detail::
    TelegramSettings;
using ::eats_restapp_communications::types::telegram::Recipients;

struct TelegramFixture {
  TelegramSettings settings;
  formats::json::Value args;
  Recipients recipients;
  TelegramFixture()
      : settings(
            ConfigTelegramSettings{{{"daily-digest", {"single_row"}},
                                    {"penalty",
                                     {"<b>{place_name}, {place_address}</b>",
                                      "penalty: {penalty} ({place_name})",
                                      "rows to be removed {unknown}"}}}}) {
    formats::json::ValueBuilder args_builder;
    args_builder["penalty"] = 420;
    args = args_builder.ExtractValue();

    recipients.place_id = 123;
    recipients.place_name = "Сыто-Пьяно";
    recipients.place_address = "Симферополь, Карла Маркса, 7";
  }
};

using TemplateMapTestParams = std::tuple<std::string, std::vector<std::string>>;

struct TemplateMapTest : public TelegramFixture,
                         public TestWithParam<TemplateMapTestParams> {};

INSTANTIATE_TEST_SUITE_P(
    TemplateMapTest, TemplateMapTest,
    Values(TemplateMapTestParams{"penalty",
                                 {"<b>{place_name}, {place_address}</b>",
                                  "penalty: {penalty} ({place_name})",
                                  "rows to be removed {unknown}"}},
           TemplateMapTestParams{"daily-digest", {"single_row"}},
           TemplateMapTestParams{"other-event", {}}));

TEST_P(TemplateMapTest, should_return_template_by_type) {
  const auto [event, expected] = GetParam();
  ASSERT_EQ(settings.GetTemplate(event), expected);
}

using ResolveTemplateTestParams = std::tuple<std::string, std::string>;

struct ResolveTemplateTest : public TelegramFixture,
                             public TestWithParam<ResolveTemplateTestParams> {};

INSTANTIATE_TEST_SUITE_P(
    ResolveTemplateTest, ResolveTemplateTest,
    Values(ResolveTemplateTestParams{"daily-digest", "single_row"},
           ResolveTemplateTestParams{
               "penalty",
               "<b>Сыто-Пьяно, Симферополь, Карла Маркса, 7</b>\npenalty: 420 "
               "(Сыто-Пьяно)"}));

TEST_P(ResolveTemplateTest, should_make_message_from_template) {
  const auto [event, expected] = GetParam();
  const auto message = ComponentImpl().MakeMessage(
      recipients, event, args, settings,
      eats_restapp_communications::models::ConfigTelegramTypes(), {});
  ASSERT_EQ(message, expected);
}

TEST(BuildMessage, should_build_message) {
  eats_restapp_communications::types::telegram::Recipients recipients;
  recipients.place_name = "Place Name";
  std::string event_type = "stop_menu_items";
  auto args = formats::json::FromString(R"(
{
  "place_address": "Place Address",
  "new_stoped_items": [
    {
      "name": "Name1",
      "reactivated_at": "2021-02-12T14:11:16+00:00"
    },
    {
      "name": "Name2"
    }
  ],
  "old_stoped_items": [
    {
      "name": "Name3",
      "reactivated_at": "2021-02-12T14:11:16+00:00"
    }
  ],
  "other_items": [
    {
      "name": "Name4"
    }
  ],
  "empty_items": []
}
  )");
  ConfigTelegramSettings telegram_settings{
      {{"other_event", {"Ny1", "Ny2, {old_stoped_items}"}},
       {"stop_menu_items",
        {"Ресторан {place_name}", "Адрес {place_address}",
         "Доставка {delivery_type}",
         "Блюда поставили в стоп:", "{new_stoped_items:stoped_item}",
         "Блюда были в стопе:", "{old_stoped_items:stoped_item}", "Еще что то",
         "{empty_items:stoped_item}", "Конец"}}}};
  eats_restapp_communications::models::ConfigTelegramTypes telegram_types{{
      {"other_type", {"Ny1", "Ny2, {old_stoped_items}"}},
      {"stoped_item", {"{name}", "Недосткпно до {reactivated_at}"}},
  }};
  eats_restapp_communications::models::TemplateContext context;
  context.timezone = "UTC";
  context.formats = {"%d.%m.%Y", "%H:%M %d.%m.%Y"};
  context.delivery_types = {{"native", "Курьер"}, {"marketplace", "Ресторан"}};
  eats_restapp_communications::components::telegram::ComponentImpl component;
  auto result = component.MakeMessage(
      recipients, event_type, args, telegram_settings, telegram_types, context);
  std::string expected_result = R"(Ресторан Place Name
Адрес Place Address
Блюда поставили в стоп:
Name1
Недосткпно до 2021-02-12T14:11:16+00:00
Name2

Блюда были в стопе:
Name3
Недосткпно до 2021-02-12T14:11:16+00:00

Еще что то

Конец)";
  ASSERT_EQ(result, expected_result);
}

}  // namespace testing
