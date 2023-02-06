#include <userver/utest/utest.hpp>

#include <helpers/cashback/repositories/get_from_request.hpp>

namespace plus {

using Decimal = decimal64::Decimal<4>;

bool PriceIsValid(const std::string& price_kind,
                  const std::string& order_status);

TEST(PriceIsValid, Valid) {
  auto result = PriceIsValid("final_cost", "complete");
  ASSERT_TRUE(result);
}

TEST(PriceIsValid, InValid) {
  auto result = PriceIsValid("fixed", "complete");
  ASSERT_FALSE(result);
}

auto build_request(const std::optional<double> agent_cashback,
                   const std::optional<double> marketing_cashback,
                   const std::string kind) {
  handlers::CurrentPrices price{0, agent_cashback, marketing_cashback,
                                marketing_cashback, "final_cost"};
  handlers::TotwRequestObj body{"", std::nullopt, std::nullopt, kind,
                                "", "",           price};
  return body;
}

TEST(GetOrderCashback, AgentCashbackFromRequest) {
  auto cashback_storage =
      CashbackFromRequest(build_request(99, std::nullopt, "complete"));
  auto result = cashback_storage.GetOrderCashback(CashbackOrder{});
  ASSERT_EQ(result.value, Decimal(99));
}

TEST(GetOrderCashback, MarketingCashbackFromRequest) {
  auto cashback_storage =
      CashbackFromRequest(build_request(std::nullopt, 11, "complete"));
  auto result = cashback_storage.GetOrderCashback(CashbackOrder{});
  ASSERT_EQ(result.value, Decimal(11));
}

TEST(GetOrderCashback, BothCashbacksFromRequest) {
  auto cashback_storage =
      CashbackFromRequest(build_request(99, 11, "complete"));
  auto result = cashback_storage.GetOrderCashback(CashbackOrder{});
  ASSERT_EQ(result.value, Decimal(110));
}

TEST(GetOrderCashback, NoCashbackInRequest) {
  auto cashback_storage = CashbackFromRequest(
      build_request(std::nullopt, std::nullopt, "complete"));
  auto result = cashback_storage.GetOrderCashback(CashbackOrder{});
  ASSERT_EQ(result.value, Decimal(0));
}

TEST(GetOrderCashback, InvalidPrice) {
  auto cashback_storage =
      CashbackFromRequest(build_request(99, std::nullopt, "pending"));
  auto result = cashback_storage.GetOrderCashback(CashbackOrder{});
  ASSERT_EQ(result.value, Decimal(0));
}

}  // namespace plus
