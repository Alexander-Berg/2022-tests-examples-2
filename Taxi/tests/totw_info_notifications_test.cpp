#include <userver/utest/utest.hpp>

#include <experiments3/models/cache_manager.hpp>
#include <modules/totw_info/notifications/notifications.hpp>
#include "mock_services/payment_info_service_test.hpp"

namespace internal_totw::info::notifications {

static const std::string kExpInformerNotEnoughBalance =
    "plus_totw_informer_not_enough_balance";

using Decimal = decimal64::Decimal<4>;
namespace exp3 = experiments3::models;

auto build_exp_data(
    const std::optional<std::vector<std::string>>& exps = std::nullopt) {
  exp3::ClientsCache::MappedData exp_data{};
  for (const auto& item : exps.value_or(std::vector<std::string>{})) {
    exp3::ExperimentResult expResult;
    if (item == kExpInformerNotEnoughBalance) {
      formats::json::ValueBuilder valueBuilder;
      valueBuilder["type"] = "payment_informer";
      valueBuilder["enabled"] = true;

      formats::json::ValueBuilder informer;
      informer["icon_tag"] = "yandex_card_with_mark";
      informer["need_send_replenish_amount"] = true;
      valueBuilder["informer"] = informer;

      formats::json::ValueBuilder translations;
      translations["title_key"] =
          "taxiontheway.cashback.notifications.yandex_card.title";
      translations["subtitle_key"] =
          "taxiontheway.cashback.notifications.yandex_card.subtitle";
      valueBuilder["translations"] = translations;

      expResult = {
          "kExpInformerNotEnoughBalance", valueBuilder.ExtractValue(), {}};
    }
    exp_data.insert({item, expResult});
  }
  return exp_data;
}

plus::PaymentInfo GetDefaultPaymentInfo() {
  plus::PaymentInfo payment_info;
  payment_info.status = plus::PaymentStatus::kInit;
  payment_info.held = std::vector{
      plus::PaymentItems{plus::PaymentType::kYandexCard,
                         std::vector{plus::Item{"ride", Decimal(200)}}}};
  payment_info.cleared = {};

  return payment_info;
}

OrderInfo GetDefaultOrderInfo() {
  Payment payment;
  payment.currency = "RUB";
  payment.payment_type = "yandex_card";

  OrderInfo order_info;
  order_info.payment = payment;
  order_info.fixed_price = Decimal(400);
  order_info.id = "order_id";

  BreakdownItem breakdown_item;
  order_info.cost_breakdown =
      std::vector{BreakdownItem{"yandex_card", Decimal(300)},
                  BreakdownItem{"card", Decimal(100)}};

  return order_info;
}

TEST(BuildNotifications, HappyPath) {
  auto payment_info = GetDefaultPaymentInfo();
  auto payment_info_mock =
      std::make_shared<plus::PaymentInfoServiceMock>(payment_info);
  NotificationsDeps deps{
      build_exp_data(std::vector<std::string>{kExpInformerNotEnoughBalance}),
      payment_info_mock};

  NotificationsInput input;
  input.order_info = GetDefaultOrderInfo();

  auto result = BuildNotifications(deps, input);
  ASSERT_TRUE(result.yandex_card);

  auto yandex_card = *result.yandex_card;
  ASSERT_EQ(yandex_card.type, "payment_informer");

  auto informer = yandex_card.informer;
  ASSERT_EQ(informer.icon_tag, "yandex_card_with_mark");
  ASSERT_TRUE(informer.need_send_replenish_amount);

  auto card_balance = informer.conditions.card_balance;
  ASSERT_EQ(card_balance.currency, "RUB");
  ASSERT_EQ(card_balance.amount, Decimal(100));

  auto translations = yandex_card.translations;
  ASSERT_EQ(translations.title_key,
            "taxiontheway.cashback.notifications.yandex_card.title");
  ASSERT_EQ(translations.subtitle_key,
            "taxiontheway.cashback.notifications.yandex_card.subtitle");
}

TEST(BuildNotifications, DontShouldReturnYandexCardNotification) {
  auto payment_info = GetDefaultPaymentInfo();
  auto payment_info_mock =
      std::make_shared<plus::PaymentInfoServiceMock>(payment_info);
  NotificationsDeps deps{
      build_exp_data(std::vector<std::string>{kExpInformerNotEnoughBalance}),
      payment_info_mock};

  NotificationsInput input;
  input.order_info = GetDefaultOrderInfo();

  auto new_input = input;
  new_input.order_info.fixed_price = std::nullopt;
  auto result = BuildNotifications(deps, new_input);
  ASSERT_FALSE(result.yandex_card);

  new_input = input;
  new_input.order_info.payment.payment_type = std::nullopt;
  result = BuildNotifications(deps, new_input);
  ASSERT_FALSE(result.yandex_card);

  new_input = input;
  new_input.order_info.payment.payment_type = "card";
  result = BuildNotifications(deps, new_input);
  ASSERT_FALSE(result.yandex_card);

  new_input = input;
  new_input.order_info.cost_breakdown = std::nullopt;
  result = BuildNotifications(deps, new_input);
  ASSERT_FALSE(result.yandex_card);

  new_input = input;
  new_input.order_info.cost_breakdown =
      std::vector{BreakdownItem{"card", Decimal(100)}};
  result = BuildNotifications(deps, new_input);
  ASSERT_FALSE(result.yandex_card);
}

}  // namespace internal_totw::info::notifications
