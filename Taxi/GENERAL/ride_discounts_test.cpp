#include <optional>

#include <gtest/gtest.h>

#include <defs/all_definitions.hpp>
#include <helpers/ride_discounts.hpp>

namespace {
constexpr auto kEconom = "econom";
constexpr auto kDiscountId = "test_discount_id";
}  // namespace

TEST(GetDiscount, DoesNotHaveDiscounts) {
  helpers::ride_discounts::Response response;
  EXPECT_FALSE(helpers::GetDiscount(response, kEconom));
}

TEST(GetDiscount, HasMoney) {
  helpers::ride_discounts::Response response;
  auto& discount = response.discounts[kEconom];
  discount.money_value = clients::ride_discounts::MatchedDiscount{};
  EXPECT_TRUE(helpers::GetDiscount(response, kEconom));
}

TEST(GetDiscount, HasCashback) {
  helpers::ride_discounts::Response response;
  auto& discount = response.discounts[kEconom];
  discount.cashback_value = clients::ride_discounts::MatchedDiscount{};

  EXPECT_FALSE(helpers::GetDiscount(response, kEconom));
}

TEST(GetCashbackDiscount, DoesNotHaveDiscounts) {
  helpers::ride_discounts::Response response;
  EXPECT_FALSE(helpers::GetCashbackDiscount(response, kEconom));
}

TEST(GetCashbackDiscount, HasMoney) {
  helpers::ride_discounts::Response response;
  auto& discount = response.discounts[kEconom];
  discount.money_value = clients::ride_discounts::MatchedDiscount{};
  EXPECT_FALSE(helpers::GetCashbackDiscount(response, kEconom));
}

TEST(GetCashbackDiscount, HasCashback) {
  helpers::ride_discounts::Response response;
  auto& discount = response.discounts[kEconom];
  discount.cashback_value = clients::ride_discounts::MatchedDiscount{};
  EXPECT_TRUE(helpers::GetCashbackDiscount(response, kEconom));
}

TEST(GetDiscountOffers, Ok) {
  helpers::ride_discounts::Response response;
  EXPECT_FALSE(helpers::GetDiscountOffers(response, kEconom));
  EXPECT_FALSE(helpers::GetCashbackDiscountOffers(response, kEconom));

  auto now = utils::datetime::Now();
  auto& discount = response.discounts[kEconom];

  clients::ride_discounts::MatchedDiscount value;
  value.discount_id = kDiscountId;
  value.usage_restrictions.emplace();
  value.usage_restrictions->current = 2;
  value.usage_restrictions->maximum = 5;
  value.budget_per_person.emplace();
  value.budget_per_person->spent = 301.5;
  value.budget_per_person->maximum = 1000.1;
  value.active_period_end = now;

  handlers::DiscountOffer expected_offer;
  expected_offer.discount_id = kDiscountId;
  expected_offer.usage_restrictions.emplace();
  expected_offer.usage_restrictions->current = 2;
  expected_offer.usage_restrictions->maximum = 5;
  expected_offer.budget_per_person.emplace();
  expected_offer.budget_per_person->spent = 301.5;
  expected_offer.budget_per_person->maximum = 1000.1;
  expected_offer.active_period_end = now;
  std::vector<handlers::DiscountOffer> expected{expected_offer};

  discount.money_value = value;
  EXPECT_FALSE(helpers::GetCashbackDiscountOffers(response, kEconom));
  EXPECT_EQ(helpers::GetDiscountOffers(response, kEconom), expected);

  discount.cashback_value = value;
  EXPECT_EQ(helpers::GetCashbackDiscountOffers(response, kEconom), expected);
  EXPECT_EQ(helpers::GetDiscountOffers(response, kEconom), expected);

  discount.money_value = std::nullopt;
  EXPECT_EQ(helpers::GetCashbackDiscountOffers(response, kEconom), expected);
  EXPECT_FALSE(helpers::GetDiscountOffers(response, kEconom));
}
