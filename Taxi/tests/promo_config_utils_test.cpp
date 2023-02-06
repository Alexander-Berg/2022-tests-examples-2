#include <userver/utest/utest.hpp>

#include <experiments3/eats_restapp_promo_settings.hpp>
#include <src/defs/definitions.hpp>
#include <utils/promo_config_utils.hpp>
#include <utils/translation/tests/mock_translator_test.hpp>

namespace eats_restapp_promo::utils {

::handlers::PromoConfiguration ConvertConfigPromoInfoConfigurationToOurOne(
    const experiments3::eats_restapp_promo_settings::PromoConfiguration&
        config_promo_info_configuration);

}

TEST(PromoSettingsCodegenAdapters, ConfigToResponse) {
  {
    experiments3::eats_restapp_promo_settings::PromoConfiguration
        config_promo_info_configuration;
    experiments3::eats_restapp_promo_settings::ItemIdsConfiguration item_ids;
    item_ids.min_items = 123;
    item_ids.disabled_categories = {"foo", "bar"};
    config_promo_info_configuration.item_ids = item_ids;

    auto response_promo_info_configuration =
        eats_restapp_promo::utils::ConvertConfigPromoInfoConfigurationToOurOne(
            config_promo_info_configuration);

    EXPECT_EQ(response_promo_info_configuration.item_ids->min_items, 123);
    ASSERT_EQ(response_promo_info_configuration.item_ids->disabled_categories,
              (std::vector<std::string>{"foo", "bar"}));
  }

  {
    experiments3::eats_restapp_promo_settings::PromoConfiguration
        config_promo_info_configuration;
    experiments3::eats_restapp_promo_settings::ItemIdsConfiguration item_ids;
    item_ids.min_items = 789;
    item_ids.disabled_categories = {"bar", "baz"};
    config_promo_info_configuration.item_ids = item_ids;
    experiments3::eats_restapp_promo_settings::DiscountConfiguration discount;
    discount.minimum = 123;
    discount.maximum = 456;
    config_promo_info_configuration.discount = discount;

    auto response_promo_info_configuration =
        eats_restapp_promo::utils::ConvertConfigPromoInfoConfigurationToOurOne(
            config_promo_info_configuration);

    EXPECT_EQ(response_promo_info_configuration.discount,
              (handlers::DiscountConfiguration{123, 456}));
    EXPECT_EQ(response_promo_info_configuration.item_ids->min_items, 789);
    ASSERT_EQ(response_promo_info_configuration.item_ids->disabled_categories,
              (std::vector<std::string>{"bar", "baz"}));
  }

  {
    experiments3::eats_restapp_promo_settings::PromoConfiguration
        config_promo_info_configuration;
    experiments3::eats_restapp_promo_settings::ItemIdConfiguration item_id;
    item_id.disabled_categories = {"baz", "bar"};
    config_promo_info_configuration.item_id = item_id;

    auto response_promo_info_configuration =
        eats_restapp_promo::utils::ConvertConfigPromoInfoConfigurationToOurOne(
            config_promo_info_configuration);

    ASSERT_EQ(response_promo_info_configuration.item_id->disabled_categories,
              (std::vector<std::string>{"baz", "bar"}));
  }

  {
    experiments3::eats_restapp_promo_settings::PromoConfiguration
        config_promo_info_configuration;
    experiments3::eats_restapp_promo_settings::CashbackConfiguration cashback;
    cashback.minimum = 100;
    cashback.maximum = 200;
    config_promo_info_configuration.cashback = cashback;

    auto response_promo_info_configuration =
        eats_restapp_promo::utils::ConvertConfigPromoInfoConfigurationToOurOne(
            config_promo_info_configuration);

    ASSERT_EQ(response_promo_info_configuration.cashback,
              (handlers::CashbackConfiguration{100, 200}));
  }

  {
    experiments3::eats_restapp_promo_settings::PromoConfiguration
        config_promo_info_configuration;
    experiments3::eats_restapp_promo_settings::CashbackConfiguration cashback;
    cashback.minimum = 101;
    cashback.maximum = 201;
    config_promo_info_configuration.cashback = cashback;

    auto response_promo_info_configuration =
        eats_restapp_promo::utils::ConvertConfigPromoInfoConfigurationToOurOne(
            config_promo_info_configuration);

    ASSERT_EQ(response_promo_info_configuration.cashback,
              (handlers::CashbackConfiguration{101, 201}));
  }
}
