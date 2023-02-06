#include "any_billing_event.hpp"

#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/utils/datetime.hpp>

#include "amount_type.hpp"

namespace helper::tests {

TEST(BillingEventsVersion, PaymentV1) {
  auto payment_v1 = formats::json::FromString(R"(
    {
      "client_id": "1",
      "payment": {
        "amount": "100",
        "currency": "RUB",
        "payment_method": "card",
        "payment_terminal_id": "1111",
        "product_id": "some_product_id",
        "product_type": "delivery",
        "payment_service": "some_service"
      },
      "external_payment_id": "ext1",
      "transaction_date": "2021-03-24T12:11:00+00:00"
    }
  )");

  auto event = helper::ParseBillingEvent(payment_v1);
  EXPECT_EQ(helper::GetKind(event), helper::BillingEventKind::kPayment);
  const auto& data = std::get<handlers::BillingPayment>(event);
  EXPECT_EQ(data.client.id, "1");
  EXPECT_EQ(data.payment.amount, helpers::AmountType(100));
  EXPECT_EQ(data.payment.currency, "RUB");
  EXPECT_EQ(data.payment.payment_method, handlers::PaymentType::kCard);
  EXPECT_EQ(*data.payment.payment_terminal_id, "1111");
  EXPECT_EQ(data.payment.product_id, "some_product_id");
  EXPECT_EQ(data.payment.product_type, handlers::ProductType::kDelivery);
  EXPECT_EQ(*data.payment.payment_service, "some_service");
  EXPECT_EQ(data.external_payment_id, "ext1");
  EXPECT_EQ(data.transaction_date,
            utils::datetime::GuessStringtime(
                "2021-03-24T12:11:00+00:00",
                utils::datetime::kDefaultDriverTimezone));
}

TEST(BillingEventsVersion, RefundV1) {
  auto refund_v1 = formats::json::FromString(R"(
    {
      "client_id": "2",
      "refund": {
        "amount": "200",
        "currency": "BYN",
        "payment_method": "our_refund",
        "payment_terminal_id": "2222",
        "product_id": "another_product_id",
        "product_type": "product",
        "payment_service": "another_service"
      },
      "external_payment_id": "ext2",
      "transaction_date": "2021-03-24T12:11:00+00:00"
    }
  )");

  auto event = helper::ParseBillingEvent(refund_v1);
  EXPECT_EQ(helper::GetKind(event), helper::BillingEventKind::kRefund);
  const auto& data = std::get<handlers::BillingRefund>(event);
  EXPECT_EQ(data.client.id, "2");
  EXPECT_EQ(data.refund.amount, helpers::AmountType(200));
  EXPECT_EQ(data.refund.currency, "BYN");
  EXPECT_EQ(data.refund.payment_method, handlers::PaymentType::kOurRefund);
  EXPECT_EQ(*data.refund.payment_terminal_id, "2222");
  EXPECT_EQ(data.refund.product_id, "another_product_id");
  EXPECT_EQ(data.refund.product_type, handlers::ProductType::kProduct);
  EXPECT_EQ(*data.refund.payment_service, "another_service");
  EXPECT_EQ(data.external_payment_id, "ext2");
  EXPECT_EQ(data.transaction_date,
            utils::datetime::GuessStringtime(
                "2021-03-24T12:11:00+00:00",
                utils::datetime::kDefaultDriverTimezone));
}

TEST(BillingEventsVersion, CommissionV1) {
  auto commission_v1 = formats::json::FromString(R"(
    {
      "client_id": "3",
      "commission": {
        "amount": "300",
        "currency": "KZT",
        "type": "plus_cashback",
        "product_id": "assembly_id",
        "product_type": "assembly",
        "payment_service": "commission_service"
      },
      "external_payment_id": "ext3",
      "transaction_date": "2021-03-24T12:11:00+00:00"
    }
  )");

  auto event = helper::ParseBillingEvent(commission_v1);
  EXPECT_EQ(helper::GetKind(event), helper::BillingEventKind::kCommission);
  const auto& data = std::get<handlers::BillingCommission>(event);
  EXPECT_EQ(data.client.id, "3");
  EXPECT_EQ(data.commission.amount, helpers::AmountType(300));
  EXPECT_EQ(data.commission.currency, "KZT");
  EXPECT_EQ(*data.commission.type, handlers::CommissionType::kPlusCashback);
  EXPECT_EQ(data.commission.product_id, "assembly_id");
  EXPECT_EQ(data.commission.product_type, handlers::ProductType::kAssembly);
  EXPECT_EQ(*data.commission.payment_service, "commission_service");
  EXPECT_EQ(data.external_payment_id, "ext3");
  EXPECT_EQ(data.transaction_date,
            utils::datetime::GuessStringtime(
                "2021-03-24T12:11:00+00:00",
                utils::datetime::kDefaultDriverTimezone));
}

TEST(BillingEventsVersion, CommissionV2) {
  auto commission_v2 = formats::json::FromString(R"(
    {
      "client": {
        "id": "80874256",
        "mvp": "br_moscow_adm",
        "contract_id": "73605",
        "country_code": "RU"
      },
      "version": "2",
      "commission": {
        "type": "goods",
        "amount": "139.5",
        "currency": "RUB",
        "product_id": "product__002",
        "product_type": "product"
      },
      "transaction_date": "2021-10-05T15:59:33+00:00",
      "external_payment_id": "52814954316b47499456076e49293edd"
    }
    )");

  auto event = helper::ParseBillingEvent(commission_v2);
  EXPECT_EQ(helper::GetKind(event), helper::BillingEventKind::kCommission);
  const auto& data = std::get<handlers::BillingCommission>(event);
  EXPECT_EQ(data.client.id, "80874256");
  EXPECT_EQ(data.client.mvp, "br_moscow_adm");
  EXPECT_EQ(data.client.contract_id, "73605");
  EXPECT_EQ(data.client.country_code, handlers::CountryCode::kRu);
  EXPECT_EQ(data.commission.amount, helpers::AmountType("139.5"));
  EXPECT_EQ(data.commission.currency, "RUB");
  EXPECT_EQ(*data.commission.type, handlers::CommissionType::kGoods);
  EXPECT_EQ(data.commission.product_id, "product__002");
  EXPECT_EQ(data.commission.product_type, handlers::ProductType::kProduct);
  EXPECT_EQ(data.external_payment_id, "52814954316b47499456076e49293edd");
  EXPECT_EQ(data.transaction_date,
            utils::datetime::GuessStringtime(
                "2021-10-05T15:59:33+00:00",
                utils::datetime::kDefaultDriverTimezone));
}

}  // namespace helper::tests
