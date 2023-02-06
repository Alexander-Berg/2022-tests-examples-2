
#include <fmt/format.h>

#include <userver/utest/utest.hpp>

#include "presenters/sdk-state/sdk-state-v2/menu.hpp"

#include "tests/mocks/price_formatter_service.hpp"
#include "tests/mocks/translator_service.hpp"
#include "tests/use_cases/client_application_menu/output_models_test.hpp"

namespace sweet_home::presenters::sdk_state_v2 {

namespace output_models = client_application_menu::output_models;

output_models::MenuData PrepareModel() {
  output_models::MenuData menu;
  menu.currency = "RUB";
  menu.balance_badge.subtitle =
      core::MakeTranslation(core::MakeClientKey("badge"));

  {
    // wide promotions
    output_models::Section section;
    section.type = client_application::SectionType::kSection;
    section.style = client_application::SectionStyle::kBordered;

    output_models::MenuItem stories;
    stories.type = client_application::MenuItemType::kStories;
    stories.item_id = "stories_id_1";
    stories.stories_item =
        output_models::StoriesItem{"test_screen", {320, 240}};
    section.items.push_back(stories);
    menu.sections.push_back(section);
  }

  {
    // spend points
    output_models::Section section;
    section.type = client_application::SectionType::kSection;
    section.style = client_application::SectionStyle::kBordered;
    section.title = core::MakeTranslation(core::MakeClientKey("how_to_spend"));
    section.subtitle =
        core::MakeTranslation(core::MakeClientKey("some_subtitle"));
    section.trailing_item =
        core::MakeTranslation(core::MakeClientKey("points_info"));
    section.border_styles = {client_application::BorderStyle::kDefault,
                             client_application::BorderStyle::kRounded};

    section.items.push_back(tests::output_models::MakeListMenuItem(
        tests::output_models::MakeLead("lead_key")));
    menu.sections.push_back(section);
  }

  {
    // separator
    output_models::Section section;
    section.type = client_application::SectionType::kSeparator;
    section.items.push_back(output_models::MenuItem{});
    menu.sections.push_back(section);
  }

  return menu;
}

MenuContext PrepareContext() {
  MenuContext result;
  result.locale = "RU";
  result.translator = std::make_shared<mocks::TranslatorServiceMock>(
      [](const core::TranslationData& key, const std::string& locale) {
        return fmt::format("{}/{}", key.main_key->key, locale);
      });
  result.price_formatter = std::make_shared<mocks::PriceFormatterMock>(
      nullptr, nullptr, [](const std::string& currency, const std::string&) {
        return core::CurrencyRules{currency, currency, currency, currency};
      });
  return result;
}

const std::string kExpectedJson = R"(
{
    "balance_badge": {
        "subtitle": "badge/RU",
        "show_glyph": false
    },
    "currency_rules": {
        "code": "RUB",
        "sign": "RUB",
        "template": "RUB",
        "text": "RUB"
    },
    "sections": [
        {
            "type": "section",
            "style": "bordered",
            "items": [
                {
                    "type": "stories",
                    "stories": {
                        "screen_name": "test_screen",
                        "preview": {
                            "width": 320,
                            "height": 240
                        }
                    }
                }
            ]
        },
        {
            "type": "section",
            "title": "how_to_spend/RU",
            "subtitle": "some_subtitle/RU",
            "style": "bordered",
            "border_styles": {
                "top": "default",
                "bottom": "rounded"
            },
            "trail": {
                "type": "default",
                "title": "points_info/RU"
            },
            "items": [
                {
                    "type": "list_item",
                    "list_item": {
                        "lead": {
                            "type": "default",
                            "title": "lead_key"
                        },
                        "action": {
                            "type": "DEEPLINK",
                            "deeplink": "this is deeplink for presenters test"
                        }
                    }
                }
            ]
        },
        {
            "type": "separator"
        }
    ]
}
)";

TEST(TestBuildMenuV2, HappyPath) {
  auto context = PrepareContext();
  auto model = PrepareModel();
  auto result = BuildMenuV2(context, model);

  const auto& response = formats::json::ValueBuilder(result).ExtractValue();
  const auto& expected = formats::json::FromString(kExpectedJson);
  ASSERT_EQ(response, expected);
}

}  // namespace sweet_home::presenters::sdk_state_v2
