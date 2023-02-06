#include <gtest/gtest.h>

#include <modules/zoneinfo-core/core/tariff_notifications/tariff_notifications.hpp>

#include "../test_utils/mock_translator.hpp"

namespace zoneinfo::core {

namespace {
clients::taxi_tariffs::Category MockCategory() {
  clients::taxi_tariffs::Category econom;
  econom.can_be_default = true;
  econom.comments_disabled = true;
  econom.is_default = true;
  econom.mark_as_new = false;
  econom.max_route_points_count = 40;
  econom.name = "econom";
  econom.only_for_soon_orders = false;
  econom.toll_roads_enabled = false;
  econom.restrict_by_payment_type = {"card",         "corp",
                                     "applepay",     "googlepay",
                                     "coop_account", "personal_wallet"};
  econom.service_levels = std::vector<int>{154};
  econom.tanker_key = "name.econom";

  clients::taxi_tariffs::Notification notification;
  notification.show_count = 3;
  notification.tanker_key = "key";
  notification.type = "type";
  clients::taxi_tariffs::NotificationTranslations translations;
  translations.extra["button"] = "notifications.button";
  notification.translations = translations;
  econom.notifications = {notification};

  return econom;
}

}  // namespace

TEST(TestNotifications, Simple) {
  const auto& category = MockCategory();

  TariffNotificationsDeps deps{category};

  const auto& result = GetTariffNotifications(deps);
  ASSERT_EQ(result.size(), 1);

  const auto& notification = result[0];
  ASSERT_EQ(notification.key, "key");
  ASSERT_EQ(notification.type, "type");
  ASSERT_EQ(notification.show_count, 3);

  const auto& translations = notification.translations;
  ASSERT_EQ(translations.size(), 1);
  ASSERT_NE(translations.find("button"), translations.end());

  const auto& translation = translations.at("button");
  AssertTankerKey(translation->GetKey(),
                  {"client_messages", "notifications.button"});
  ASSERT_EQ(translation->GetType(), TranslationType::kOptional);
}

}  // namespace zoneinfo::core
