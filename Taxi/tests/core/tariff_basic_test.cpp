#include <gtest/gtest.h>

#include <modules/zoneinfo-core/core/tariff_basic/tariff_basic.hpp>
#include <testing/taxi_config.hpp>

#include "../test_utils/mock_translator.hpp"

namespace zoneinfo::core {

namespace {

clients::taxi_tariffs::Category MockCategory() {
  // values from prod for city izberbash
  clients::taxi_tariffs::Category econom;
  econom.can_be_default = true;
  econom.comments_disabled = true;
  econom.is_default = true;
  econom.mark_as_new = false;
  econom.max_route_points_count = 40;
  econom.max_waiting_time = 180;
  econom.name = "econom";
  econom.only_for_soon_orders = false;
  econom.toll_roads_enabled = false;
  econom.restrict_by_payment_type = {"card",         "corp",
                                     "applepay",     "googlepay",
                                     "coop_account", "personal_wallet"};
  econom.service_levels = std::vector<int>{154};
  econom.tanker_key = "name.econom";

  return econom;
}

}  // namespace

TEST(TestTariffsInfo, Simple) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  const auto& taxi_config = config.Get<taxi_config::TaxiConfig>();
  const auto& ts_category = MockCategory();
  HiddenFlagByCategories hidden_flag_by_categories = {{"econom", true}};
  TariffBasicInput tariffs_basic_input{std::nullopt};
  TariffBasicDeps tariff_basic_deps{ts_category, hidden_flag_by_categories,
                                    taxi_config, "izberbash"};

  const auto& result_econom =
      BuildTariffBasicInfo(tariffs_basic_input, tariff_basic_deps);

  ASSERT_EQ(result_econom.id, "econom");
  ASSERT_EQ(result_econom.class_name, "econom");
  ASSERT_EQ(result_econom.service_levels, std::vector<int>{154});

  ASSERT_EQ(result_econom.name->GetKey().keyset, "tariff");
  ASSERT_EQ(result_econom.name->GetKey().key, "name.econom");
  AssertTankerKey(result_econom.name->GetKey(), {"tariff", "name.econom"});
  ASSERT_EQ(result_econom.name->GetType(), TranslationType::kRequired);

  ASSERT_EQ(result_econom.description->GetKey().keyset, "client_messages");
  ASSERT_EQ(result_econom.description->GetKey().key,
            "mainscreen.description_econom_izberbash");
  ASSERT_EQ(result_econom.description->GetFallback()->keyset,
            "client_messages");
  ASSERT_EQ(result_econom.description->GetFallback()->key,
            "mainscreen.description_econom");
  ASSERT_EQ(result_econom.description->GetType(), TranslationType::kRequired);

  ASSERT_EQ(result_econom.short_description->GetKey().keyset,
            "client_messages");
  ASSERT_EQ(result_econom.short_description->GetKey().key,
            "mainscreen.short_description_econom");
  ASSERT_EQ(result_econom.short_description->GetType(),
            TranslationType::kOptional);

  ASSERT_EQ(result_econom.settings.can_be_default, true);
  ASSERT_EQ(result_econom.settings.comments_disabled, true);
  ASSERT_EQ(result_econom.settings.is_default, true);
  ASSERT_EQ(result_econom.settings.is_hidden, true);
  ASSERT_EQ(result_econom.settings.mark_as_new, false);
  ASSERT_EQ(result_econom.settings.max_route_points_count, 40);
  ASSERT_EQ(result_econom.settings.max_waiting_time, 3);
  ASSERT_EQ(result_econom.settings.only_for_soon_orders, false);
  ASSERT_EQ(result_econom.settings.toll_roads_enabled, false);
  std::vector<std::string> expected_restrict_by_payment_type = {
      "card",      "corp",         "applepay",
      "googlepay", "coop_account", "personal_wallet"};
  ASSERT_EQ(result_econom.settings.restrict_by_payment_type,
            expected_restrict_by_payment_type);
}

}  // namespace zoneinfo::core
