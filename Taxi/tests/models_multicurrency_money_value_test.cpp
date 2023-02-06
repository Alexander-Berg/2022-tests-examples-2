#include <gtest/gtest.h>

#include <models/multicurrency_money_value.hpp>

namespace std {

std::ostream& operator<<(std::ostream& os,
                         const models::MulticurrencyMoneyValue& v) {
  return os << v.ToString();
}

}  // namespace std

TEST(ModelsMulticurrencyMoneyValue, Test) {
  models::MulticurrencyMoneyValue v1({{"RUB", 20.0f}, {"ILS", 0.0f}});

  v1.Add({{"RUB", 35.0f}, {"USD", 1.75f}});
  ASSERT_EQ(v1, models::MulticurrencyMoneyValue(
                    {{"RUB", 55.0f}, {"USD", 1.75f}, {"ILS", 0.0f}}));

  EXPECT_EQ(v1.Get("RUB"), 55.0f);
  EXPECT_EQ(v1.Get("EUR"), 0.0f);

  v1.Subtract({{"USD", 0.75f}});
  ASSERT_EQ(v1, models::MulticurrencyMoneyValue(
                    {{"RUB", 55.0f}, {"USD", 1.0f}, {"ILS", 0.0f}}));

  v1.Multiply(2.0f);
  ASSERT_EQ(v1, models::MulticurrencyMoneyValue(
                    {{"RUB", 110.0f}, {"USD", 2.0f}, {"ILS", 0.0f}}));

  v1.ApplyThreshold(2.0f);
  ASSERT_EQ(v1,
            models::MulticurrencyMoneyValue({{"RUB", 110.0f}, {"USD", 2.0f}}));
}
