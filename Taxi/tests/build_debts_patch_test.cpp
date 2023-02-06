#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/formats/bson/inline.hpp>
#include <userver/formats/json/inline.hpp>
#include <userver/utest/utest.hpp>

#include <modules/debts_processing/build_debts_patch.hpp>
#include "mock_account_accessor.hpp"
#include "mock_invoice_accessor.hpp"

namespace debts::processing {

using Decimal = decimal64::Decimal<4>;

DebtsAction MapEventToAction(const std::string& event);
void CheckReasonCode(const std::optional<std::string>& reason_code,
                     DebtsAction action);
std::optional<decimal64::Decimal<4>> GetDebtValue(
    const invoice::Invoice& invoice, DebtsAction action);
Account GetAccount(const debts::coop_account::AccountAccessor& account_accessor,
                   const std::optional<std::string>& locked_phone_id,
                   const models::OrderDoc& order_doc);
std::string GetBrand(const models::OrderDoc& order_doc,
                     const taxi_config::TaxiConfig& config);
DebtsPatch BuildDebtsPatch(const DebtsPatchDeps& deps,
                           const DebtsPatchInput& input);

TEST(MapEventToAction, AllCases) {
  ASSERT_EQ(MapEventToAction("set_debt"), DebtsAction::kSet);
  ASSERT_EQ(MapEventToAction("reset_debt"), DebtsAction::kReset);
  ASSERT_THROW(MapEventToAction("twice_debt"), DoNotProcessPatch);
}

TEST(CheckReasonCode, AllCases) {
  ASSERT_NO_THROW(CheckReasonCode(std::nullopt, DebtsAction::kSet));
  ASSERT_NO_THROW(CheckReasonCode("by_admin", DebtsAction::kReset));
  ASSERT_THROW(CheckReasonCode(std::nullopt, DebtsAction::kReset),
               ProcessingError);
}

TEST(GetDebtValue, HappyPath) {
  auto invoice = debts::invoice::Invoice{Decimal{50}, "RUB", {}, {}};
  auto result = GetDebtValue(invoice, DebtsAction::kSet);
  ASSERT_EQ(result, std::make_optional(Decimal{50}));
}

TEST(GetDebtValue, ZeroDebtSet) {
  auto invoice = debts::invoice::Invoice{Decimal{0}, "RUB", {}, {}};
  ASSERT_THROW(GetDebtValue(invoice, DebtsAction::kSet), DoNotProcessPatch);
}

TEST(GetDebtValue, ResetDebt) {
  auto invoice = debts::invoice::Invoice{Decimal{125}, "RUB", {}, {}};
  auto result = GetDebtValue(invoice, DebtsAction::kReset);
  ASSERT_FALSE(result);
}

TEST(GetAccount, HappyPath) {
  auto account_accessor = debts::coop_account::MockAccountAccessor(
      debts::coop_account::Account{"shared_yandex_uid", "shared_phone_id"});
  auto order_doc = models::OrderDoc{};
  order_doc.yandex_uid = "yandex_uid";
  order_doc.phone_id = "phone_id";

  auto result = GetAccount(account_accessor, std::nullopt, order_doc);
  ASSERT_EQ(result.yandex_uid, "yandex_uid");
  ASSERT_EQ(result.phone_id, "phone_id");

  order_doc.payment_type = "coop_account";
  result = GetAccount(account_accessor, std::nullopt, order_doc);
  ASSERT_EQ(result.yandex_uid, "shared_yandex_uid");
  ASSERT_EQ(result.phone_id, "shared_phone_id");
}

TEST(GetAccount, NoAccount) {
  auto account_accessor =
      debts::coop_account::MockAccountAccessor(std::nullopt);
  auto order_doc = models::OrderDoc{};
  order_doc.yandex_uid = "yandex_uid";
  order_doc.phone_id = "phone_id";
  order_doc.payment_type = "coop_account";
  ASSERT_THROW(GetAccount(account_accessor, std::nullopt, order_doc),
               ProcessingError);
}

TEST(GetAccount, FamilyMember) {
  auto account_accessor =
      debts::coop_account::MockAccountAccessor(std::nullopt);
  auto order_doc = models::OrderDoc{};
  order_doc.yandex_uid = "member_yandex_uid";
  order_doc.phone_id = "member_phone_id";
  order_doc.family_owner_uid = "owner_yandex_uid";

  auto result = GetAccount(account_accessor, "owner_phone_id", order_doc);
  ASSERT_EQ(result.yandex_uid, "owner_yandex_uid");
  ASSERT_EQ(result.phone_id, "owner_phone_id");

  // w/o locked_phone_id
  result = GetAccount(account_accessor, std::nullopt, order_doc);
  ASSERT_EQ(result.yandex_uid, "member_yandex_uid");
  ASSERT_EQ(result.phone_id, "member_phone_id");
}

auto build_config() {
  auto config =
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>();
  config.application_map_brand = dynamic_config::ValueDict<std::string>{
      "name", {{"__default__", "yataxi"}, {"lavka_android", "lavka"}}};
  return config;
}

TEST(GetBrand, HappyPath) {
  auto order_doc = models::OrderDoc{};
  order_doc.application = "lavka_android";
  auto result = GetBrand(order_doc, build_config());
  ASSERT_EQ(result, "lavka");
}

TEST(GetBrand, Default) {
  auto order_doc = models::OrderDoc{};
  order_doc.application = "";
  auto result = GetBrand(order_doc, build_config());
  ASSERT_EQ(result, "yataxi");
}

TEST(BuildDebtsPatch, Noinvoice) {
  auto invoice_accessor = debts::invoice::MockInvoiceAccessor(std::nullopt);
  auto deps = DebtsPatchDeps{
      invoice_accessor,
      debts::coop_account::MockAccountAccessor(
          debts::coop_account::Account{"shared_yandex_uid", "shared_phone_id"}),
      build_config()};
  auto order_doc = models::OrderDoc{};
  order_doc.application = "lavka";
  order_doc.yandex_uid = "yandex_uid";
  order_doc.phone_id = "phone_id";
  auto input =
      DebtsPatchInput{"set_debt", "order_id", {}, std::nullopt, order_doc};
  ASSERT_THROW(BuildDebtsPatch(deps, input), DoNotProcessPatch);
}

TEST(BuildDebtsPatch, HappyPath) {
  auto deps = DebtsPatchDeps{
      debts::invoice::MockInvoiceAccessor(
          debts::invoice::Invoice{Decimal{20}, "RUB", {}, {}}),
      debts::coop_account::MockAccountAccessor(
          debts::coop_account::Account{"shared_yandex_uid", "shared_phone_id"}),
      build_config()};
  auto order_doc = models::OrderDoc{};
  order_doc.application = "lavka";
  order_doc.yandex_uid = "yandex_uid";
  order_doc.phone_id = "phone_id";
  auto input =
      DebtsPatchInput{"set_debt", "order_id", {}, std::nullopt, order_doc};
  auto result = BuildDebtsPatch(deps, input);
  ASSERT_EQ(result.action, DebtsAction::kSet);
  ASSERT_EQ(result.brand, "yataxi");
  ASSERT_EQ(result.account.phone_id, "phone_id");
  ASSERT_EQ(result.account.yandex_uid, "yandex_uid");
  ASSERT_EQ(result.debt_value.value(), Decimal{20});
  ASSERT_EQ(result.currency, "RUB");
}

}  // namespace debts::processing
