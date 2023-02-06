#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/yaplus_brandings_config.hpp>

#include "utils/jsonfixtures.hpp"

TEST(TestYaPlusBrandingsConfig, StandardParsingConfig) {
  const std::string kProfileBadgeFixtureFileName =
      "yaplus_brandings_config_unittest/profile_badge.json";
  const auto& profile_badge_bson =
      JSONFixtures::GetFixtureBSON(kProfileBadgeFixtureFileName);

  const std::string kMenuIconFixtureFileName =
      "yaplus_brandings_config_unittest/menu_icon.json";
  const auto& menu_icon_bson =
      JSONFixtures::GetFixtureBSON(kMenuIconFixtureFileName);

  const std::string kTariffCardBadgeFixtureFileName =
      "yaplus_brandings_config_unittest/tariff_card_badge.json";
  const auto& tariff_card_badge_bson =
      JSONFixtures::GetFixtureBSON(kTariffCardBadgeFixtureFileName);

  const std::string kPaymentDecorationFixtureFileName =
      "yaplus_brandings_config_unittest/payment_decoration.json";
  const auto& payment_decoration_bson =
      JSONFixtures::GetFixtureBSON(kPaymentDecorationFixtureFileName);

  config::DocsMap docs_map;
  docs_map.Insert("YAPLUS_PROFILE_BADGE_BY_PLUS_VERSION", profile_badge_bson);
  docs_map.Insert("YAPLUS_MENU_ICON_BASE_TAG_BY_PLUS_VERSION", menu_icon_bson);
  docs_map.Insert("YAPLUS_TARIFF_CARD_BADGE_BY_PLUS_VERSION",
                  tariff_card_badge_bson);
  docs_map.Insert("YAPLUS_PAYMENT_DECORATION_BY_PLUS_VERSION",
                  payment_decoration_bson);
  config::YaPlusBrandingsConfig brandings_config(docs_map);

  // profile badge
  const auto& profile_badge_discount =
      brandings_config.profile_badge_by_plus_version["discount"];
  ASSERT_EQ(profile_badge_discount.title_key, "branding.profile_badge_title");
  ASSERT_EQ(profile_badge_discount.subtitle_key,
            "branding.profile_badge_subtitle");
  ASSERT_EQ(profile_badge_discount.image_tag, "plus_card");

  const auto& profile_badge_cashback =
      brandings_config.profile_badge_by_plus_version["cashback"];
  ASSERT_EQ(profile_badge_cashback.title_key, "branding.profile_badge_title");
  ASSERT_EQ(profile_badge_cashback.subtitle_key,
            "branding.cashback.profile_badge_subtitle");
  ASSERT_EQ(profile_badge_cashback.image_tag, "plus_card_cashback");

  // menu icon
  const auto& config = brandings_config.menu_icon_base_tag_by_plus_version;
  ASSERT_EQ(config["discount"], "plus_discount_profile_icon");
  ASSERT_EQ(config["cashback"], "plus_cashback_profile_icon");
  ASSERT_EQ(config["some_new_version"], "plus_profile_icon");

  // tariff card badge
  const auto& tariff_card_badge_discount =
      brandings_config.tariff_card_badge_by_plus_version["discount"];
  ASSERT_EQ(tariff_card_badge_discount.title_key,
            "yandex_plus_discount_tariff_card_title_default");
  ASSERT_EQ(tariff_card_badge_discount.subtitle_key,
            "yandex_plus_discount_tariff_card_subtitle_default");
  ASSERT_EQ(tariff_card_badge_discount.image_tag, "plus_card");

  const auto& tariff_card_badge_cashback =
      brandings_config.tariff_card_badge_by_plus_version["cashback"];
  ASSERT_EQ(tariff_card_badge_cashback.title_key,
            "branding.cashback.tariff_card_title");
  ASSERT_EQ(tariff_card_badge_cashback.subtitle_key,
            "branding.cashback.tariff_card_subtitle");
  ASSERT_EQ(tariff_card_badge_cashback.image_tag, "plus_card_cashback");

  // payment decoration
  const auto& payment_decoration =
      brandings_config.payment_decoration_by_plus_version;
  ASSERT_EQ(payment_decoration["discount"].summary_payment_subtitle_key,
            "yandex_plus_discount_summary_card_promo");
  ASSERT_EQ(payment_decoration["cashback"].summary_payment_subtitle_key,
            "yandex_plus_cashback_summary_card_promo");
}
