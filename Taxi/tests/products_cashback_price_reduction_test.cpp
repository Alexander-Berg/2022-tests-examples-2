#include <gtest/gtest.h>

#include <helpers/products.hpp>

TEST(ReduceProductsPrice, TrivialCase) {
  const std::vector<handlers::Product> initial_products = {
      {"big_mac_1", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"big_mac_2", "2.00", ::handlers::ProductTax::kX20, "Big Mac Burger 2",
       std::nullopt, "654321"}};

  const std::vector<models::ItemPaymentTypeRevision> items_wth_plus_amount = {};

  const std::vector<handlers::Product> expected_products = {
      {"big_mac_1", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"big_mac_2", "2.00", ::handlers::ProductTax::kX20, "Big Mac Burger 2",
       std::nullopt, "654321"}};

  const auto flattened_products =
      helpers::products::ReduceProductPriceByPersonalWalletAmount(
          initial_products, items_wth_plus_amount);
  ASSERT_EQ(flattened_products, expected_products);
}

TEST(ReduceProductsPrice, BasicReduction) {
  const std::vector<handlers::Product> initial_products = {
      {"big_mac_1", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"big_mac_2", "2.00", ::handlers::ProductTax::kX20, "Big Mac Burger 2",
       std::nullopt, "654321"},
      {"big_mac_3", "5.00", ::handlers::ProductTax::kX20, "Big Mac Burger 3",
       std::nullopt, "654321"}};

  const std::vector<models::ItemPaymentTypeRevision> items_wth_plus_amount = {
      {"big_mac_1", "test_order", "", models::PaymentType::kTrust,
       models::Decimal(1), std::nullopt},
      {"big_mac_2", "test_order", "", models::PaymentType::kTrust,
       models::Decimal(1), std::nullopt}};

  const std::vector<handlers::Product> expected_products = {
      {"big_mac_1", "0.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"big_mac_2", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 2",
       std::nullopt, "654321"},
      {"big_mac_3", "5.00", ::handlers::ProductTax::kX20, "Big Mac Burger 3",
       std::nullopt, "654321"}};

  const auto flattened_products =
      helpers::products::ReduceProductPriceByPersonalWalletAmount(
          initial_products, items_wth_plus_amount);
  ASSERT_EQ(flattened_products, expected_products);
}

TEST(ReduceProductsPrice, CompoundReduction) {
  const std::vector<handlers::Product> initial_products = {
      {"big_mac_1", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"big_mac_2", "2.00", ::handlers::ProductTax::kX20, "Big Mac Burger 2",
       "big_mac_1", "654321"}};

  const std::vector<models::ItemPaymentTypeRevision> items_wth_plus_amount = {
      {"big_mac_1", "test_order", "", models::PaymentType::kTrust,
       models::Decimal(1), std::nullopt},
      {"big_mac_2", "test_order", "", models::PaymentType::kTrust,
       models::Decimal(1), std::nullopt}};

  const std::vector<handlers::Product> expected_products = {
      {"big_mac_1", "0.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"big_mac_2", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 2",
       "big_mac_1", "654321"}};

  const auto flattened_products =
      helpers::products::ReduceProductPriceByPersonalWalletAmount(
          initial_products, items_wth_plus_amount);
  ASSERT_EQ(flattened_products, expected_products);
}
