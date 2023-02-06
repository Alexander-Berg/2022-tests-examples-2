#include <current_prices/calculator.hpp>

#include <functional>

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include <clients/plus-wallet/client_mock_base.hpp>
#include <taxi_config/variables/MARKETING_CASHBACK_CEIL_ENABLED.hpp>

namespace current_prices {

Decimal GetCoupon(const Coupon& coupon, Decimal price);
Decimal GetTotalPrice(const OrderProc& proc);
std::string GetKind(const OrderProc& proc);
Decimal SubstractWalletPaymentSum(
    Decimal base, const std::vector<BreakdownItem>& cost_breakdown);
std::optional<Decimal> CalculateCashbackPrice(
    const OrderProc& proc, Decimal total_price,
    const dynamic_config::Snapshot& config);
Decimal CalculateUserTotalPrice(Decimal total_price,
                                std::optional<Decimal> cashback_price);
std::optional<Decimal> CalculateDiscountCashback(
    const OrderProc& proc, Decimal total_price,
    const dynamic_config::Snapshot& config);
std::optional<Decimal> CalculatePossibleCashback(
    const OrderProc& proc, Decimal total_price,
    const dynamic_config::Snapshot& config);
bool NeedToCalculate(const OrderProc& proc);

namespace test {
using SplitRequest =
    clients::plus_wallet::v1_internal_payment_split::post::Request;
using SplitResponse =
    clients::plus_wallet::v1_internal_payment_split::post::Response;
using SplitHandler = std::function<SplitResponse()>;
struct SplitError : public clients::plus_wallet::Exception {
  std::string_view HandleInfo() const noexcept override { return "error"; }
};

class MockPlusWalletClient : public clients::plus_wallet::ClientMockBase {
 public:
  MockPlusWalletClient(SplitHandler split_handler)
      : split_handler_(std::move(split_handler)) {}

  SplitResponse V1InternalPaymentSplit(
      const SplitRequest&,
      const clients::plus_wallet::CommandControl&) const override {
    return split_handler_();
  }

 private:
  SplitHandler split_handler_;
};

OrderProc MakeDefaultOrderProc() {
  OrderProc proc;
  proc.pricing_data.price_total = Decimal{"121"};
  proc.using_new_pricing = true;
  proc.pricing_data.currency = "RUB";
  proc.fixed_price = true;
  proc.payment.type = "card";
  proc.payment.payment_id = "123";
  proc.taxi_status = "driving";
  return proc;
}

}  // namespace test

TEST(GetCoupon, Invalid) {
  Coupon coupon{false, {}, {}, {}};
  auto result = GetCoupon(coupon, Decimal{"135"});
  ASSERT_EQ(result, Decimal{"0"});
}

TEST(GetCoupon, AbsoluteValue) {
  Coupon coupon{true, {}, {}, Decimal{"50"}};
  auto result = GetCoupon(coupon, Decimal{"135"});
  ASSERT_EQ(result, Decimal{"50"});
}

TEST(GetCoupon, WithoutLimit) {
  Coupon coupon{true, Decimal{"10"}, {}, Decimal{"50"}};
  auto result = GetCoupon(coupon, Decimal{"135"});
  ASSERT_EQ(result, Decimal{"13.5"});
}

TEST(GetCoupon, WithLimit) {
  Coupon coupon{true, Decimal{"10"}, Decimal{"7"}, Decimal{"50"}};
  auto result = GetCoupon(coupon, Decimal{"135"});
  ASSERT_EQ(result, Decimal{"7"});
}

TEST(GetTotalPrice, NoCurrentCost) {
  OrderProc proc;
  proc.current_cost = std::nullopt;
  proc.pricing_data.price_total = Decimal{"100"};
  auto result = GetTotalPrice(proc);
  ASSERT_EQ(result, Decimal{"100"});
}

TEST(GetTotalPrice, HasCurrentCost) {
  OrderProc proc;
  proc.current_cost = Decimal{"135"};
  proc.pricing_data.price_total = Decimal{"100"};
  auto result = GetTotalPrice(proc);
  ASSERT_EQ(result, Decimal{"135"});
}

TEST(GetTotalPrice, FinishedOrder) {
  OrderProc proc;
  proc.status = "finished";
  proc.toll_road = TollRoad{false, Decimal{"15"}};
  proc.current_cost = Decimal{"135"};
  proc.pricing_data.price_total = Decimal{"100"};
  proc.cost = Decimal{"50"};
  proc.pricing_data.coupon_applied = false;
  proc.pricing_data.unite_total_price_enabled = false;
  proc.coupon.valid = false;
  auto result = GetTotalPrice(proc);
  ASSERT_EQ(result, Decimal{"65"});
}

TEST(GetTotalPrice, FinishedOrderWithCoupon) {
  OrderProc proc;
  proc.status = "finished";
  proc.current_cost = Decimal{"135"};
  proc.pricing_data.price_total = Decimal{"100"};
  proc.cost = Decimal{"50"};
  proc.pricing_data.coupon_applied = false;
  proc.pricing_data.unite_total_price_enabled = false;
  proc.coupon = Coupon{true, Decimal{"10"}, Decimal{"7"}, Decimal{"50"}};
  auto result = GetTotalPrice(proc);
  ASSERT_EQ(result, Decimal{"45"});
}

TEST(GetTotalPrice, FinishedOrderWithAppliedCoupon) {
  OrderProc proc;
  proc.status = "finished";
  proc.current_cost = Decimal{"135"};
  proc.pricing_data.price_total = Decimal{"100"};
  proc.pricing_data.coupon_applied = true;
  proc.pricing_data.unite_total_price_enabled = false;
  proc.cost = Decimal{"50"};
  proc.coupon = Coupon{true, Decimal{"10"}, Decimal{"7"}, Decimal{"50"}};
  auto result = GetTotalPrice(proc);
  ASSERT_EQ(result, Decimal{"50"});
}

TEST(GetKind, Fixed) {
  OrderProc proc;
  proc.current_cost = std::nullopt;
  proc.fixed_price = true;
  auto result = GetKind(proc);
  ASSERT_EQ(result, "fixed");
}

TEST(GetKind, Taximeter) {
  OrderProc proc;
  proc.current_cost = Decimal{"100"};
  auto result = GetKind(proc);
  ASSERT_EQ(result, "taximeter");
}

TEST(GetKind, Prediction) {
  OrderProc proc;
  proc.current_cost = std::nullopt;
  proc.fixed_price = false;
  auto result = GetKind(proc);
  ASSERT_EQ(result, "prediction");
}

TEST(GetKind, Finished) {
  OrderProc proc;
  proc.status = "finished";
  auto result = GetKind(proc);
  ASSERT_EQ(result, "final_cost");
}

TEST(GetKind, Cancelled) {
  OrderProc proc;
  proc.status = "cancelled";
  auto result = GetKind(proc);
  ASSERT_EQ(result, "final_cost");
}

TEST(SubstractWalletPaymentSum, HappyPathWalletPayment) {
  auto base = Decimal("100.00");
  std::vector<BreakdownItem> cost_breakdown = {
      {"card", Decimal("70.00")}, {"personal_wallet", Decimal("30.00")}};
  auto result = SubstractWalletPaymentSum(base, cost_breakdown);
  ASSERT_EQ(result, Decimal("70.00"));
}

TEST(CalculateCashbackPrice, NotUsingNewPricing) {
  OrderProc proc;
  proc.using_new_pricing = false;
  auto result = CalculateCashbackPrice(proc, Decimal{"300"},
                                       dynamic_config::GetDefaultSnapshot());
  ASSERT_FALSE(result);
}

TEST(CalculateCashbackPrice, GetFixedFromPricing) {
  OrderProc proc;
  proc.using_new_pricing = true;
  proc.pricing_data.cashback_fixed_price = Decimal{"17"};
  auto result = CalculateCashbackPrice(proc, Decimal{"300"},
                                       dynamic_config::GetDefaultSnapshot());
  ASSERT_EQ(result, Decimal{"17"});
}

TEST(CalculateCashbackPrice, NoCashbackMultiplier) {
  OrderProc proc;
  proc.using_new_pricing = true;
  proc.current_cost = Decimal{"270"};
  auto result = CalculateCashbackPrice(proc, Decimal{"300"},
                                       dynamic_config::GetDefaultSnapshot());
  ASSERT_FALSE(result);
}

TEST(CalculateCashbackPrice, PaymentTypeCash) {
  OrderProc proc;
  proc.using_new_pricing = true;
  proc.current_cost = Decimal{"270"};
  proc.pricing_data.cashback_multiplier = Decimal{"0.9"};
  proc.payment.type = "cash";
  auto result = CalculateCashbackPrice(proc, Decimal{"355"},
                                       dynamic_config::GetDefaultSnapshot());
  ASSERT_EQ(result.value(), Decimal("0"));
}

TEST(CalculateCashbackPrice, HappyPath) {
  OrderProc proc;
  proc.using_new_pricing = true;
  proc.current_cost = Decimal{"270"};
  proc.pricing_data.cashback_multiplier = Decimal{"0.9"};
  auto result = CalculateCashbackPrice(proc, Decimal{"355"},
                                       dynamic_config::GetDefaultSnapshot());
  ASSERT_EQ(result.value(), Decimal("40"));
}

TEST(CalculateUserTotalPrice, HappyPath) {
  auto result = CalculateUserTotalPrice(Decimal{"355"}, Decimal{"20"});
  ASSERT_EQ(result, Decimal{"375"});
}

TEST(CalculateCurrentPrices, HappyPath) {
  Order order;
  OrderProc proc;
  proc.pricing_data.price_total = Decimal{"121"};
  proc.using_new_pricing = true;
  proc.toll_road = TollRoad{false, Decimal{"15"}};
  proc.pricing_data.cashback_fixed_price = Decimal{"14"};
  proc.pricing_data.currency = "RUB";
  proc.fixed_price = true;
  proc.pricing_data.discount_cashback_rate = Decimal{"0.2"};
  proc.pricing_data.possible_cashback_rate = Decimal{"0.1"};
  proc.pricing_data.possible_cashback_fixed_price = Decimal{"100"};
  proc.pricing_data.discount_cashback_sponsor = "mastercard";

  order.order_id = "order_id";
  order.proc = proc;

  auto result =
      CalculateCurrentPrices(order, {dynamic_config::GetDefaultSnapshot(),
                                     clients::plus_wallet::ClientMockBase()});
  const std::unordered_map<std::string, Decimal> exp_cashback_by_sponsor = {
      {"mastercard", Decimal{"24"}}};
  ASSERT_EQ(result.user_total_price, Decimal{"135"});
  ASSERT_EQ(result.user_total_display_price, Decimal{"135"});
  ASSERT_EQ(result.user_ride_display_price, Decimal{"135"});
  ASSERT_EQ(result.cashback_price, Decimal{"14"});
  ASSERT_EQ(result.toll_road_price, Decimal{"15"});
  ASSERT_EQ(result.kind, "fixed");
  ASSERT_EQ(result.discount_cashback, Decimal{"24"});
  ASSERT_EQ(result.possible_cashback, Decimal{"100"});
  ASSERT_EQ(result.cashback_by_sponsor, exp_cashback_by_sponsor);
}

TEST(CalculateDiscountCashback, HappyPath) {
  OrderProc proc;
  proc.using_new_pricing = true;
  proc.pricing_data.discount_cashback_rate = Decimal{"0.2"};
  auto result = CalculateDiscountCashback(proc, Decimal{"355"},
                                          dynamic_config::GetDefaultSnapshot());
  ASSERT_EQ(result.value(), Decimal("71"));
}

TEST(CalculateDiscountCashback, MaxDiscountCashback) {
  OrderProc proc;
  proc.using_new_pricing = true;
  proc.pricing_data.discount_cashback_rate = Decimal{"0.2"};
  proc.pricing_data.max_discount_cashback = Decimal{"40"};

  auto result = CalculateDiscountCashback(proc, Decimal{"355"},
                                          dynamic_config::GetDefaultSnapshot());
  ASSERT_EQ(result.value(), Decimal("40"));
}

TEST(CalculateDiscountCashback, NoCashbackForCash) {
  OrderProc proc;
  proc.using_new_pricing = true;
  proc.pricing_data.discount_cashback_rate = Decimal{"0.2"};
  proc.payment.type = "cash";

  auto result = CalculateDiscountCashback(proc, Decimal{"355"},
                                          dynamic_config::GetDefaultSnapshot());
  ASSERT_EQ(result.value(), Decimal("0"));
}

TEST(CalculateDiscountCashback, RoundingFloor) {
  const auto config = dynamic_config::MakeDefaultStorage(
      {{taxi_config::MARKETING_CASHBACK_CEIL_ENABLED, false}});

  OrderProc proc;
  proc.using_new_pricing = true;
  proc.pricing_data.discount_cashback_rate = Decimal{"0.1"};
  auto result =
      CalculateDiscountCashback(proc, Decimal{"355"}, config.GetSnapshot());
  ASSERT_EQ(result.value(), Decimal{"35"});
}

TEST(CalculateDiscountCashback, RoundingCeil) {
  const auto config = dynamic_config::MakeDefaultStorage(
      {{taxi_config::MARKETING_CASHBACK_CEIL_ENABLED, true}});

  OrderProc proc;
  proc.using_new_pricing = true;
  proc.pricing_data.discount_cashback_rate = Decimal{"0.1"};
  auto result =
      CalculateDiscountCashback(proc, Decimal{"355"}, config.GetSnapshot());
  ASSERT_EQ(result.value(), Decimal("36"));
}

TEST(CalculatePossibleCashback, NoCashbackForCash) {
  OrderProc proc;

  proc.using_new_pricing = true;
  proc.pricing_data.possible_cashback_rate = Decimal{"0.1"};
  proc.pricing_data.possible_cashback_fixed_price = Decimal{"100"};
  proc.payment.type = "cash";
  proc.current_cost = Decimal{"270"};

  auto result = CalculatePossibleCashback(proc, Decimal{"355"},
                                          dynamic_config::GetDefaultSnapshot());
  ASSERT_EQ(result.value(), Decimal{"0"});
}

TEST(CalculatePossibleCashback, HappyPathUseFixPrice) {
  OrderProc proc;

  proc.using_new_pricing = true;
  proc.pricing_data.possible_cashback_rate = Decimal{"0.1"};
  proc.pricing_data.possible_cashback_fixed_price = Decimal{"100"};

  auto result = CalculatePossibleCashback(proc, Decimal{"355"},
                                          dynamic_config::GetDefaultSnapshot());
  ASSERT_EQ(result.value(), Decimal("100"));
}

TEST(CalculatePossibleCashback, HappyPathUsePossibleCashbackRate) {
  OrderProc proc;

  proc.using_new_pricing = true;
  proc.pricing_data.possible_cashback_rate = Decimal{"0.1"};
  proc.pricing_data.possible_cashback_fixed_price = Decimal{"100"};
  proc.current_cost = Decimal{"1000"};

  auto result = CalculatePossibleCashback(proc, Decimal{"1000"},
                                          dynamic_config::GetDefaultSnapshot());
  ASSERT_EQ(result.value(), Decimal("100"));
}

}  // namespace current_prices
