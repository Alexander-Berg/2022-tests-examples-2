#include <gtest/gtest.h>

#include <helpers/products.hpp>
#include <helpers/transactions/items.hpp>

TEST(DiffTwoRevisions, TrivialCase) {
  const std::vector<models::ItemPaymentTypeRevision> old_revision = {
      {"big_mac_1", "test_order", "", models::PaymentType::kTrust,
       models::Decimal(1), std::nullopt},
      {"big_mac_2", "test_order", "", models::PaymentType::kTrust,
       models::Decimal(1), std::nullopt}};

  const std::vector<models::ItemPaymentTypeRevision> new_revision = {
      {"big_mac_1", "test_order", "", models::PaymentType::kTrust,
       models::Decimal(1), std::nullopt},
      {"big_mac_2", "test_order", "", models::PaymentType::kTrust,
       models::Decimal(1), std::nullopt}};

  const std::vector<models::ItemPaymentTypeRevision> expected_diff = {};

  const auto diff = helpers::products::GetCashbackDiffBetweenRevisions(
      old_revision, new_revision);
  ASSERT_EQ(diff, expected_diff);
}

TEST(DiffTwoRevisions, BasicReduction) {
  const std::vector<models::ItemPaymentTypeRevision> old_revision = {
      {"big_mac_1", "test_order", "", models::PaymentType::kTrust,
       models::Decimal(1), std::nullopt},
      {"big_mac_2", "test_order", "", models::PaymentType::kTrust,
       models::Decimal(2), std::nullopt},
      {"big_mac_3", "test_order", "", models::PaymentType::kTrust,
       models::Decimal(3), std::nullopt}};

  const std::vector<models::ItemPaymentTypeRevision> new_revision = {
      {"big_mac_1", "test_order", "", models::PaymentType::kTrust,
       models::Decimal(1), std::nullopt},
      {"big_mac_2", "test_order", "", models::PaymentType::kTrust,
       models::Decimal(1), std::nullopt}};

  const std::vector<models::ItemPaymentTypeRevision> expected_diff = {
      {"big_mac_2", "test_order", "", models::PaymentType::kTrust,
       models::Decimal(1), std::nullopt},
      {"big_mac_3", "test_order", "", models::PaymentType::kTrust,
       models::Decimal(3), std::nullopt}};

  const auto diff = helpers::products::GetCashbackDiffBetweenRevisions(
      old_revision, new_revision);
  LOG_INFO() << diff.size();
  LOG_INFO() << diff.at(0).item_id << " " << diff.at(0).plus_amount;

  ASSERT_EQ(diff, expected_diff);
}

TEST(FixCollisions, TrivialCase) {
  helpers::uniform_discount::UniformDiscountRules rules = {
      models::Decimal{1}, models::Decimal{1}, 0};
  std::vector<int> complement_amount = {496, 400};
  std::vector<std::pair<int, int>> tests = {{63, 439}, {200, 200}};
  for (std::size_t i = 0; i < complement_amount.size(); i++) {
    std::vector<helpers::transactions::PaymentTypeCustomerServices> items = {
        {"personal_wallet",
         {{"delivery-1", {models::Decimal{tests[i].first}}},
          {"composition-products", {models::Decimal{tests[i].second}}}}},
        {"card",
         {{"delivery-1", {models::Decimal{1}}},
          {"composition-products", {models::Decimal{1}}}}}};

    helpers::transactions::FixPersonalWalletSum(
        models::Decimal{complement_amount[i]}, items, rules);
    models::Decimal check_sum{0};
    for (auto item : items[0].items) {
      check_sum += item.second.amount;
    }
    ASSERT_TRUE(check_sum <= models::Decimal{complement_amount[i]});
  }
}
