#include <userver/utest/utest.hpp>

#include "presenters/sdk-state/sdk-state-v1/menu.hpp"

#include "internal/action_button/models.hpp"

#include "tests/mocks/price_formatter_service.hpp"
#include "tests/mocks/translator_service.hpp"
#include "tests/presenters/models_test.hpp"
#include "tests/use_cases/client_application_menu/output_models_test.hpp"

namespace sweet_home::tests::handlers {

::handlers::BalanceBadge MakeBalanceBadge(
    const std::optional<::std::string>& subtitle,
    const std::optional<::std::string>& placeholder, bool show_glyph) {
  ::handlers::BalanceBadge badge;
  badge.subtitle = subtitle;
  badge.placeholder = placeholder;
  badge.show_glyph = show_glyph;
  return badge;
}

bool operator==(const ::handlers::BalanceBadge& left,
                const ::handlers::BalanceBadge& right) {
  return left.placeholder == right.placeholder &&
         left.subtitle == right.subtitle && left.show_glyph == right.show_glyph;
}

}  // namespace sweet_home::tests::handlers

namespace sweet_home::presenters::sdk_state_v1 {

namespace {

namespace output_models = client_application_menu::output_models;

output_models::MenuData PrepareModel(
    const std::optional<output_models::ActionButton>& action_button =
        std::nullopt,
    const std::optional<output_models::BalanceBadge>& balance_badge =
        std::nullopt,
    const std::string& currency = "RUB") {
  namespace tests = tests::output_models;

  output_models::MenuData model;

  if (balance_badge) {
    model.balance_badge = *balance_badge;
  } else {
    model.balance_badge =
        tests::MakeBalanceBadge(true, "Ваши баллы на Плюсе", std::nullopt);
  }

  model.currency = currency;
  model.action_button = action_button;

  auto simple_item = tests::MakeListMenuItem(tests::MakeLead("lead_title_key"));

  auto item_with_subtitle = tests::MakeListMenuItem(
      tests::MakeLead("another_lead_title_key", "lead_subtitle_key"));

  auto url_item = tests::MakeListMenuItem(
      tests::MakeLead("url_title_key"),
      tests::MakeTrail(client_application::ElementStyle::kNav));

  auto setting_item = tests::MakeListMenuItem(
      tests::MakeLead("setting_title_key"),
      tests::MakeTrail(client_application::ElementStyle::kSwitch));

  model.sections = {
      tests::MakeSection({simple_item, item_with_subtitle, url_item}),
      tests::MakeSection({setting_item},
                         client_application::SectionStyle::kBordered,
                         "section_title_key")};

  return model;
}

MenuContext PrepareContext(const mocks::TranslatorServiceMock& translator =
                               mocks::TranslatorServiceMock(),
                           const mocks::PriceFormatterMock& price_formatter =
                               mocks::PriceFormatterMock(),
                           const std::string& locale = "RU") {
  MenuContext result;

  result.translator =
      std::make_shared<mocks::TranslatorServiceMock>(translator);
  result.price_formatter =
      std::make_shared<mocks::PriceFormatterMock>(price_formatter);
  result.locale = locale;

  return result;
}

output_models::ActionButton MakeActionButton(
    const action_button::Action& action = action_button::Action::kPlusBuy) {
  output_models::ActionButton result;
  result.action = action;
  result.title = core::MakeTranslation(
      {l10n::keysets::kClientMessages, "Первые 90 дней бесплатно"});
  result.subtitle = core::MakeTranslation(
      {l10n::keysets::kClientMessages, "Потом за 199 руб./мес"});

  auto state_title = core::MakeTranslation(
      {l10n::keysets::kClientMessages, "Попробовать бесплатно"});
  result.states = {{state_title, std::nullopt, action_button::State::kIdle}};

  return result;
}

void AssertSection(
    const handlers::SectionV1& section, size_t expected_items_count,
    const std::optional<std::string>& expected_title = std::nullopt,
    handlers::SectionV1Style expected_style =
        handlers::SectionV1Style::kDefault) {
  ASSERT_EQ(section.items.size(), expected_items_count);
  ASSERT_EQ(section.style, expected_style);
  if (expected_title) {
    ASSERT_TRUE(section.title);
    ASSERT_EQ(*section.title, *expected_title);
  } else {
    ASSERT_FALSE(section.title);
  }
}

}  // namespace

TEST(TestBuildMenu, HappyPath) {
  // prepare
  auto action_button = MakeActionButton();
  auto model = PrepareModel(action_button);

  auto context = PrepareContext();
  // call
  auto result = BuildMenu(context, model);

  // check balance_badge
  auto expected_balance_badge = tests::handlers::MakeBalanceBadge(
      "Ваши баллы на Плюсе", std::nullopt, true);
  ASSERT_EQ(result.balance_badge, expected_balance_badge);

  // check currency_rules
  ASSERT_EQ(result.currency_rules->code, "RUB");
  ASSERT_EQ(result.currency_rules->template_, "$VALUE$ $SIGN$$CURRENCY$");
  ASSERT_EQ(result.currency_rules->text, "руб.");
  ASSERT_EQ(result.currency_rules->sign, "₽");

  // check action_button
  auto expected_action_button = tests::handlers::MakeActionButton(
      "Первые 90 дней бесплатно", "Потом за 199 руб./мес");
  action_button::AssertActionButton(result.action_button,
                                    expected_action_button);

  // check sections
  ASSERT_EQ(result.sections.size(), 2);

  auto& section_1 = result.sections[0];
  AssertSection(section_1, 3);

  auto& section_2 = result.sections[1];
  AssertSection(section_2, 1, "section_title_key",
                handlers::SectionV1Style::kBordered);
}

TEST(TestBuildMenu, ErrorInTranslatorBalanceBadge) {
  // prepare
  auto model = PrepareModel();

  mocks::HandlerTranslate handler_translate = [](const core::TranslationData&,
                                                 const std::string&) {
    return std::nullopt;
  };

  auto context = PrepareContext({handler_translate, nullptr});

  // call
  auto result = BuildMenu(context, model);
  auto expected_balance_badge =
      tests::handlers::MakeBalanceBadge(std::nullopt, std::nullopt, true);

  ASSERT_EQ(result.balance_badge, expected_balance_badge);
}

TEST(TestBuildMenu, ErrorInTranslatorActionButton) {
  // prepare
  auto action_button = MakeActionButton();
  auto model = PrepareModel(action_button);

  auto handler_translate_throw = [](const core::TranslationData& translation,
                                    const std::string&) {
    throw core::TranslatorServiceError("translate error");
    return translation.main_key->key;
  };

  auto context = PrepareContext({nullptr, handler_translate_throw});

  // call
  auto result = BuildMenu(context, model);

  action_button::AssertActionButton(result.action_button, std::nullopt);
}

TEST(TestBuildMenu, SectionTranslationErrors) {
  // prepare
  auto handler_translate = [](const core::TranslationData& translation,
                              const std::string&) {
    std::optional<std::string> result;
    if (translation.main_key->key == "section_title_key")
      result = std::nullopt;
    else
      result = translation.main_key->key;
    return result;
  };

  auto context = PrepareContext({handler_translate, nullptr});

  auto model = PrepareModel();

  // call
  auto result = BuildMenu(context, model);

  ASSERT_EQ(result.sections.size(), 2);
  AssertSection(result.sections[1], 1, std::nullopt,
                handlers::SectionV1Style::kBordered);
}

TEST(TestBuildMenu, HideElementIfTitleHasTranslationErrors) {
  auto handler_translate_throw = [](const core::TranslationData& translation,
                                    const std::string&) {
    if (translation.main_key->key == "another_lead_title_key") {
      // title translation throws -> hide whole element
      throw core::TranslatorServiceError("translate error");
    }

    return translation.main_key->key;
  };

  auto context = PrepareContext({nullptr, handler_translate_throw});
  auto model = PrepareModel();
  auto result = BuildMenu(context, model);

  ASSERT_EQ(result.sections.size(), 2);
  AssertSection(result.sections[0], 2);
}

TEST(TestBuildMenu, HideSubtitleOnTranslationErrors) {
  // hide subtitles on translation problems
  auto handler_translate =
      [](const core::TranslationData& translation,
         const std::string&) -> std::optional<std::string> {
    // this needed for lambda return type deduction
    if (translation.main_key->key == "lead_subtitle_key")
      // subtitle translation returns null -> hide subtitle, not element
      return std::nullopt;

    return translation.main_key->key;
  };

  auto context = PrepareContext({handler_translate, nullptr});
  auto model = PrepareModel();
  auto result = BuildMenu(context, model);

  ASSERT_EQ(result.sections.size(), 2);
  AssertSection(result.sections[0], 3);

  auto& item_with_subtitle = result.sections[0].items[1];
  ASSERT_TRUE(item_with_subtitle.lead.title);
  ASSERT_TRUE(
      std::holds_alternative<std::string>(*item_with_subtitle.lead.title));
  ASSERT_EQ(std::get<std::string>(*item_with_subtitle.lead.title),
            "another_lead_title_key");
  ASSERT_FALSE(item_with_subtitle.lead.subtitle);
  ASSERT_FALSE(item_with_subtitle.trail);
}

}  // namespace sweet_home::presenters::sdk_state_v1
