#include "use_cases/client_application_menu/client_application_menu.hpp"

#include <gtest/gtest.h>

#include <testing/taxi_config.hpp>

#include "tests/core/models_test.hpp"
#include "tests/internal/models_test.hpp"
#include "tests/mocks/action_button_repository.hpp"
#include "tests/mocks/application_repository.hpp"
#include "tests/mocks/countries_service.hpp"
#include "tests/mocks/setting_definition_repository.hpp"

namespace sweet_home::client_application_menu {

namespace {
const core::SDKClient kSdkClient{
    kDefaultClientId, kDefaultServiceId, kDefaultPlatform, {}, {}, {}};
const std::string kCountry = "rus";
const std::string kDefaultCurrency = "RUB";

MenuDeps PrepareDeps(const mocks::GetMenuForApplicationHandler& gm_handler) {
  auto settings_repo =
      std::make_shared<mocks::SettingDefinitionRepositoryMock>();
  settings_repo->SetStub_GetDefinitions([](const std::string&) {
    return tests::MakeSettingDefinitionMap(
        {tests::MakeDefinition("boolean_setting_id",
                               setting::SettingType::kBoolean, true, true),
         tests::MakeDefinition("global_setting_id", "global_default_value")});
  });

  MenuDeps deps;
  deps.application_repository =
      std::make_shared<mocks::ApplicationRepositoryMock>(gm_handler);
  deps.countries_service = std::make_shared<mocks::CountriesServiceMock>(
      [](const std::string&) { return kDefaultCurrency; });
  deps.action_button_repository =
      std::make_shared<mocks::ActionButtonRepositoryMock>();
  deps.setting_repository = settings_repo;
  return deps;
}

MenuContext PrepareContext() {
  auto user_subscription = tests::MakePlusSubscription(
      "ya_plus", subscription::PurchaseStatus::kAvailable, false);
  auto config = dynamic_config::GetDefaultSnapshot();
  auto experiments =
      tests::MakeExperiments({{"exist_experiment", kExpEnabled}});
  core::HideableWallet wallet = {tests::MakeWallet("RUB_wallet", "138")};
  return {user_subscription,
          config,
          experiments,
          wallet,
          std::optional<burning_balance::BurnEvent>{},
          std::nullopt};
}

}  // namespace

TEST(TestMenuV2, HappyPath) {
  auto get_menu_handler = [](const core::SDKClient&) {
    client_application::SDKMenu menu;
    {
      // wide promotions
      client_application::Section section;
      section.type = client_application::SectionType::kSection;
      section.style = client_application::SectionStyle::kBordered;
      auto stories_item =
          tests::MakeStoriesItem("house_of_plus:some_section", {322, 120});
      stories_item.visibility_requirements.required_experiment =
          "exist_experiment";
      section.items.push_back(stories_item);
      menu.sections.push_back(section);
    }

    {
      // wide promotions would be hidden by visibility_requirements
      client_application::Section section;
      section.type = client_application::SectionType::kSection;
      section.style = client_application::SectionStyle::kBordered;
      auto would_be_hidden_stories_item =
          tests::MakeStoriesItem("house_of_plus:some_sectionn", {322, 120});
      would_be_hidden_stories_item.visibility_requirements.required_experiment =
          "some_non_exists_required_exp";
      section.items.push_back(would_be_hidden_stories_item);
      menu.sections.push_back(section);
    }

    {
      // spend points
      client_application::Section section;
      section.type = client_application::SectionType::kSection;
      section.title_key = core::MakeClientKey("how_to_spend");
      section.subtitle_key = core::MakeClientKey("some_subtitle");
      section.trailing_item = client_application::TrailingItem{
          client_application::TrailingItemType::kDefault,
          core::MakeClientKey("points_info")};
      section.border_styles = {client_application::BorderStyle::kDefault,
                               client_application::BorderStyle::kRounded};

      section.items.push_back(tests::MakeListItem(
          tests::MakeOpenUrlAction("some_url"), tests::MakeLead("lead_title")));
      menu.sections.push_back(section);
    }

    {
      // separator
      client_application::Section section;
      section.type = client_application::SectionType::kSeparator;
      section.items.push_back(tests::MakeStoriesItem("separator_story", {}));
      menu.sections.push_back(section);
    }

    {
      // unsupported card
      client_application::Section section;
      section.type = client_application::SectionType::kSection;

      auto item = tests::MakeStoriesItem("malformed item", {});
      item.type = client_application::MenuItemType::kCard;

      section.items.push_back(item);
      menu.sections.push_back(section);
    }

    return menu;
  };

  auto deps = PrepareDeps(get_menu_handler);
  auto context = PrepareContext();

  // call
  auto result = GetMenuForApplication(deps, context, kSdkClient, kCountry);

  ASSERT_EQ(result.type, client_application::MenuType::kNative);
  ASSERT_EQ(result.sections.size(), 3);

  {
    // assert wide promotions
    const auto& section = result.sections[0];
    ASSERT_EQ(section.type, client_application::SectionType::kSection);
    ASSERT_EQ(section.style, client_application::SectionStyle::kBordered);

    ASSERT_EQ(section.title, std::nullopt);
    ASSERT_EQ(section.subtitle, std::nullopt);
    ASSERT_EQ(section.trailing_item, std::nullopt);

    const auto& item = section.items[0];
    ASSERT_EQ(item.type, client_application::MenuItemType::kStories);
    ASSERT_EQ(item.item_id, "test_stories_item");
    ASSERT_EQ(item.stories_item->scree_name, "house_of_plus:some_section");
    ASSERT_EQ(item.stories_item->preview.pixel_width, 322);
    ASSERT_EQ(item.stories_item->preview.pixel_height, 120);
    ASSERT_TRUE(item.list_item == std::nullopt);
  }

  {
    // assert spend points
    const auto& section = result.sections[1];

    ASSERT_EQ(section.type, client_application::SectionType::kSection);
    ASSERT_EQ(section.style, client_application::SectionStyle::kNone);
    ASSERT_EQ(section.title->main_key->key, "how_to_spend");
    ASSERT_EQ(section.subtitle->main_key->key, "some_subtitle");
    ASSERT_EQ(section.trailing_item->main_key->key, "points_info");
    ASSERT_EQ(section.border_styles->top,
              client_application::BorderStyle::kDefault);
    ASSERT_EQ(section.border_styles->bottom,
              client_application::BorderStyle::kRounded);
  }

  {
    // assert separator
    const auto& section = result.sections[2];
    ASSERT_EQ(section.type, client_application::SectionType::kSeparator);

    ASSERT_TRUE(section.items.empty());
    ASSERT_TRUE(section.trailing_item == std::nullopt);
    ASSERT_TRUE(section.title == std::nullopt);
    ASSERT_TRUE(section.subtitle == std::nullopt);
  }
}

}  // namespace sweet_home::client_application_menu
