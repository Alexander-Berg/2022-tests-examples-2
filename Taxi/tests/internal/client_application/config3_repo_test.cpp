#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include <taxi_config/variables/PLUS_SWEET_HOME_CLIENTS_UI_V2.hpp>

#include <internal/client_application/impl/config3_repository.hpp>

namespace sweet_home::client_application::impl {

const std::string kServiceMenuValue = R"(
{
  "enabled": true,
  "sections": [
    {
      "type": "section",
      "style": "none",
      "title_key": "Как тратить баллы",
      "subtitle_key": "Как",
      "item_ids": [
        "common:stories:wide_promotions"
      ],
      "border_styles": {
        "bottom": "rounded"
      },
      "trail": {
        "type": "default",
        "title_key": "1 балл"
      }
    },
    {
      "type": "separator"
    },
    {
      "type": "section",
      "style": "none",
      "item_ids": [
        "common:card:kinopoisk"
      ],
      "border_styles": {
        "top": "rounded",
        "bottom": "rounded"
      }
    }
  ]
}
)";

const std::string kMenuUI2Json = R"(
{
  "common:card:kinopoisk": {
    "hidden": true,
    "card": {
      "background_image_tag": "bg_image",
      "button": {
        "action": {
          "deeplink": "yandextaxi://<open kinopoisk app>",
          "type": "DEEPLINK"
        },
        "background_color": "#000000",
        "title_key": "Смотреть"
      },
      "icon_tag": "icon_tag",
      "subtitle_key": "some_subtitle",
      "title_key": "some_title"
    },
    "type": "card",
    "visibility_requirements": {
      "device_applications": {
        "kinopoisk": {
          "is_installed": true
        }
      }
    }
  },
  "common:stories:wide_promotions": {
    "stories": {
      "preview": {
        "height": 120,
        "width": 322
      },
      "screen_name": "house_of_plus:some_section"
    },
    "visibility_requirements": {
      "required_experiment": "some_experiment"
    },
    "required_client_features": [
      "qr"
    ],
    "type": "stories"
  }
}
)";

core::Experiments PrepareExperiments() {
  core::ExpMappedData data = {{
      "sweet_home_services_menu",  // exp_name
      {"sweet_home_services_menu",
       formats::json::FromString(kServiceMenuValue),
       {}}  // exp_value
  }};
  return core::Experiments(std::move(data));
}

dynamic_config::StorageMock PrepareTaxiConfig() {
  return dynamic_config::MakeDefaultStorage(
      {{taxi_config::PLUS_SWEET_HOME_CLIENTS_UI_V2,
        formats::json::FromString(kMenuUI2Json)}});
}

TEST(TEST, MenuViaConfigs3) {
  auto config_repo = PrepareTaxiConfig();
  auto config = config_repo.GetSnapshot();
  auto experiments = PrepareExperiments();
  auto repo = MenuViaConfigs3Repository(config, experiments);

  core::SDKClient client;
  auto menu = repo.GetMenuForApplication(client);

  ASSERT_EQ(menu.sections.size(), 3);

  {
    const auto& section = menu.sections[0];
    ASSERT_EQ(section.type, SectionType::kSection);

    ASSERT_EQ(section.style, SectionStyle::kNone);
    ASSERT_EQ(section.border_styles->top, BorderStyle::kDefault);
    ASSERT_EQ(section.border_styles->bottom, BorderStyle::kRounded);

    ASSERT_EQ(section.title_key->key, "Как тратить баллы");
    ASSERT_EQ(section.subtitle_key->key, "Как");

    ASSERT_EQ(section.trailing_item->type, TrailingItemType::kDefault);
    ASSERT_EQ(section.trailing_item->title_key->key, "1 балл");

    ASSERT_EQ(section.items.size(), 1);
    const auto& stories_item = section.items.front();
    ASSERT_EQ(stories_item.type, MenuItemType::kStories);
    ASSERT_EQ(stories_item.item_id, "common:stories:wide_promotions");
    ASSERT_EQ(stories_item.hidden, false);
    ASSERT_EQ(*stories_item.visibility_requirements.required_experiment,
              "some_experiment");

    std::unordered_set<std::string> features{"qr"};
    ASSERT_EQ(stories_item.required_client_features, features);
  }

  {
    // separator
    const auto& section = menu.sections[1];
    ASSERT_EQ(section.type, SectionType::kSeparator);
  }

  {
    // with kinopoisk card
    const auto& section = menu.sections[2];
    ASSERT_EQ(section.type, SectionType::kSection);
    ASSERT_TRUE(section.items.size() == 1);

    const auto& kinopoisk_item = section.items.front();

    ASSERT_EQ(kinopoisk_item.type, MenuItemType::kCard);
    ASSERT_EQ(kinopoisk_item.item_id, "common:card:kinopoisk");
    ASSERT_EQ(kinopoisk_item.hidden, true);

    std::unordered_set<std::string> features{};
    ASSERT_EQ(kinopoisk_item.required_client_features, features);
    ASSERT_TRUE(kinopoisk_item.list_item == std::nullopt);
    ASSERT_TRUE(kinopoisk_item.stories == std::nullopt);
    ASSERT_TRUE(kinopoisk_item.card != std::nullopt);

    const auto& app_reqs =
        kinopoisk_item.visibility_requirements.app_requirements;
    ASSERT_EQ(app_reqs.size(), 1);
    ASSERT_EQ(app_reqs.at("kinopoisk").app_name, "kinopoisk");
    ASSERT_EQ(app_reqs.at("kinopoisk").should_be_installed, true);

    const auto& card = *kinopoisk_item.card;
    ASSERT_EQ(card.title_key->key, "some_title");
    ASSERT_EQ(card.subtitle_key->key, "some_subtitle");
    ASSERT_EQ(card.icon->image_tag, "icon_tag");
    ASSERT_EQ(card.background_image.image_tag, "bg_image");
    ASSERT_TRUE(card.button != std::nullopt);

    const auto& button = *card.button;
    ASSERT_EQ(button.title_key->key, "Смотреть");
    ASSERT_EQ(button.background_color, "#000000");
  }
}

}  // namespace sweet_home::client_application::impl
