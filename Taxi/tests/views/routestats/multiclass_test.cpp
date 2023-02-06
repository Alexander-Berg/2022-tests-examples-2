#include <gtest/gtest.h>
#include <logging/log_extra.hpp>
#include <models/classes.hpp>
#include <views/routestats/multiclass.hpp>

TEST(RoutestatsMulticlass, IsMultuclassEnabledTest) {
  LogExtra log_extra;
  // only fixed price classes
  {
    models::Classes fixed_price_classes;
    fixed_price_classes.Add("econom");
    fixed_price_classes.Add("business");
    fixed_price_classes.Add("comfortplus");
    fixed_price_classes.Add("vip");

    models::Classes multiclass_choices;
    multiclass_choices.Add("business");
    multiclass_choices.Add("comfortplus");

    models::TariffSettings tariff_settings;

    models::TariffSettings::Category ts_category1;
    ts_category1.class_type = models::Classes::Econom;
    ts_category1.client_requirements = {"non_specific1", "non_specific2"};
    tariff_settings.categories.emplace_back(ts_category1);

    models::TariffSettings::Category ts_category2;
    ts_category2.class_type = models::Classes::Business;
    ts_category2.client_requirements = {"non_specific1", "non_specific2"};
    tariff_settings.categories.emplace_back(ts_category2);

    models::TariffSettings::Category ts_category3;
    ts_category3.class_type = models::Classes::ComfortPlus;
    ts_category3.client_requirements = {"non_specific1", "non_specific2"};
    tariff_settings.categories.emplace_back(ts_category3);

    models::TariffSettings::Category ts_category4;
    ts_category4.class_type = models::Classes::Vip;
    ts_category4.client_requirements = {"non_specific1", "non_specific2"};
    tariff_settings.categories.emplace_back(ts_category4);

    EXPECT_TRUE(views::multiclass::IsMulticlassEnabledByFixedPrice(
        fixed_price_classes, multiclass_choices, tariff_settings, log_extra));
  }
  // only non fixed price classes
  {
    models::Classes fixed_price_classes;

    models::Classes multiclass_choices;
    multiclass_choices.Add("business");
    multiclass_choices.Add("comfortplus");

    models::TariffSettings tariff_settings;

    models::TariffSettings::Category ts_category1;
    ts_category1.class_type = models::Classes::Econom;
    ts_category1.client_requirements = {"non_specific1", "non_specific2"};
    tariff_settings.categories.emplace_back(ts_category1);

    models::TariffSettings::Category ts_category2;
    ts_category2.class_type = models::Classes::Business;
    ts_category2.client_requirements = {"non_specific1", "non_specific2"};
    tariff_settings.categories.emplace_back(ts_category2);

    models::TariffSettings::Category ts_category3;
    ts_category3.class_type = models::Classes::ComfortPlus;
    ts_category3.client_requirements = {"non_specific1", "non_specific2"};
    tariff_settings.categories.emplace_back(ts_category3);

    models::TariffSettings::Category ts_category4;
    ts_category4.class_type = models::Classes::Vip;
    ts_category4.client_requirements = {"non_specific1", "non_specific2"};
    tariff_settings.categories.emplace_back(ts_category4);

    EXPECT_TRUE(views::multiclass::IsMulticlassEnabledByFixedPrice(
        fixed_price_classes, multiclass_choices, tariff_settings, log_extra));
  }
  // mixed price classes
  {
    models::Classes fixed_price_classes;
    fixed_price_classes.Add("econom");
    fixed_price_classes.Add("business");

    models::Classes multiclass_choices;
    multiclass_choices.Add("econom");
    multiclass_choices.Add("business");
    multiclass_choices.Add("comfortplus");
    multiclass_choices.Add("vip");

    models::TariffSettings tariff_settings;

    models::TariffSettings::Category ts_category1;
    ts_category1.class_type = models::Classes::Econom;
    ts_category1.client_requirements = {"non_specific1", "non_specific2"};
    tariff_settings.categories.emplace_back(ts_category1);

    models::TariffSettings::Category ts_category2;
    ts_category2.class_type = models::Classes::Business;
    ts_category2.client_requirements = {"non_specific1", "non_specific2"};
    tariff_settings.categories.emplace_back(ts_category2);

    models::TariffSettings::Category ts_category3;
    ts_category3.class_type = models::Classes::ComfortPlus;
    ts_category3.client_requirements = {"non_specific1", "non_specific2"};
    tariff_settings.categories.emplace_back(ts_category3);

    EXPECT_FALSE(views::multiclass::IsMulticlassEnabledByFixedPrice(
        fixed_price_classes, multiclass_choices, tariff_settings, log_extra));
  }
}
