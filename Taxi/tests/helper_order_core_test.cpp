#include <userver/utest/utest.hpp>

#include <helpers/complements/repositories/order_core.hpp>

namespace plus {

using Decimal = decimal64::Decimal<4>;

Complements CalculateComplements(Decimal wallet_balance, Decimal ride_price);

TEST(CalculateComplements, AllByWallet) {
  auto result = CalculateComplements(Decimal{215}, Decimal{135});
  ASSERT_EQ(result.by_wallet, Decimal{135});
  ASSERT_EQ(result.by_card, Decimal{0});
}

TEST(CalculateComplements, ByBoth) {
  auto result = CalculateComplements(Decimal{91}, Decimal{135});
  ASSERT_EQ(result.by_wallet, Decimal{91});
  ASSERT_EQ(result.by_card, Decimal{44});
}

TEST(CalculateComplements, EmptyByWallet) {
  auto result = CalculateComplements(Decimal{0}, Decimal{135});
  ASSERT_EQ(result.by_wallet, Decimal{0});
  ASSERT_EQ(result.by_card, Decimal{135});
}

}  // namespace plus
