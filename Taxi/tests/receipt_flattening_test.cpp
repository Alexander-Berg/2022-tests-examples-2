#include <gtest/gtest.h>

#include <helpers/products.hpp>

TEST(FlattenProductList, TrivialCase) {
  const std::vector<handlers::Product> initial_products = {
      {"big_mac_1", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"big_mac_2", "2.00", ::handlers::ProductTax::kX20, "Big Mac Burger 2",
       std::nullopt, "654321"}};

  const std::vector<handlers::Product> required_products = {
      {"big_mac_1", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"big_mac_2", "2.00", ::handlers::ProductTax::kX20, "Big Mac Burger 2",
       std::nullopt, "654321"}};

  const auto flattened_products =
      helpers::products::FlattenProductList(initial_products);
  ASSERT_EQ(flattened_products, required_products);
}

TEST(FlattenProductList, SingleLevelInclusion) {
  const std::vector<handlers::Product> initial_products = {
      {"big_mac_1", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"meat", "2.00", ::handlers::ProductTax::kX20, "Meat", "big_mac_1",
       "123456"}};

  const std::vector<handlers::Product> required_products = {
      {"big_mac_1", "3.00", ::handlers::ProductTax::kX20,
       "Big Mac Burger 1 (Meat)", std::nullopt, "123456"}};

  const auto flattened_products =
      helpers::products::FlattenProductList(initial_products);

  ASSERT_EQ(flattened_products, required_products);
}

TEST(FlattenProductList, SingleLevelInclusionReverseOrder) {
  const std::vector<handlers::Product> initial_products = {
      {"meat", "2.00", ::handlers::ProductTax::kX20, "Meat", "big_mac_1",
       "123456"},
      {"big_mac_1", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"}};

  const std::vector<handlers::Product> required_products = {
      {"big_mac_1", "3.00", ::handlers::ProductTax::kX20,
       "Big Mac Burger 1 (Meat)", std::nullopt, "123456"}};

  const auto flattened_products =
      helpers::products::FlattenProductList(initial_products);
  ASSERT_EQ(flattened_products, required_products);
}

TEST(FlattenProductList, SingleLevelInclusionSeveralProducts) {
  const std::vector<handlers::Product> initial_products = {
      {"big_mac_1", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"meat", "2.00", ::handlers::ProductTax::kX20, "Meat", "big_mac_1",
       "123456"},
      {"cheese", "4.00", ::handlers::ProductTax::kX20, "Cheese", "big_mac_1",
       "123456"}};

  const std::vector<handlers::Product> required_products = {
      {"big_mac_1", "7.00", ::handlers::ProductTax::kX20,
       "Big Mac Burger 1 (Cheese, Meat)", std::nullopt, "123456"}};

  const auto flattened_products =
      helpers::products::FlattenProductList(initial_products);

  ASSERT_EQ(flattened_products, required_products);
}

TEST(FlattenProductList, SingleLevelInclusionSeveralCopiesOfProduct) {
  const std::vector<handlers::Product> initial_products = {
      {"big_mac_1", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"beat", "2.00", ::handlers::ProductTax::kX20, "Meat", "big_mac_1",
       "123456"},
      {"cheese", "4.00", ::handlers::ProductTax::kX20, "Cheese", "big_mac_1",
       "123456"},
      {"beat_2", "3.00", ::handlers::ProductTax::kX20, "Meat", "big_mac_1",
       "123456"},
      {"pasta", "2.00", ::handlers::ProductTax::kX20, "Pasta", std::nullopt,
       "654321"}};

  const std::vector<handlers::Product> required_products = {
      {"big_mac_1", "10.00", ::handlers::ProductTax::kX20,
       "Big Mac Burger 1 (Cheese, Meat (2 шт.))", std::nullopt, "123456"},
      {"pasta", "2.00", ::handlers::ProductTax::kX20, "Pasta", std::nullopt,
       "654321"}};

  const auto flattened_products =
      helpers::products::FlattenProductList(initial_products);

  LOG_INFO() << flattened_products;
  ASSERT_EQ(flattened_products, required_products);
}

TEST(FlattenProductList, SingleLevelInclusionOnlySeveralCopiesOfProduct) {
  const std::vector<handlers::Product> initial_products = {
      {"big_mac_1", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"beat", "2.00", ::handlers::ProductTax::kX20, "Meat", "big_mac_1",
       "123456"},
      {"other_meat", "4.00", ::handlers::ProductTax::kX20, "Meat", "big_mac_1",
       "123456"},
      {"beat_2", "3.00", ::handlers::ProductTax::kX20, "Meat", "big_mac_1",
       "123456"}};

  const std::vector<handlers::Product> required_products = {
      {"big_mac_1", "10.00", ::handlers::ProductTax::kX20,
       "Big Mac Burger 1 (Meat (3 шт.))", std::nullopt, "123456"}};

  const auto flattened_products =
      helpers::products::FlattenProductList(initial_products);

  LOG_INFO() << flattened_products;
  ASSERT_EQ(flattened_products, required_products);
}

TEST(FlattenProductList, SingleLevelInclusionSeveralCopiesOfProductWrongTax) {
  const std::vector<handlers::Product> initial_products = {
      {"big_mac_1", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"beat", "2.00", ::handlers::ProductTax::kX20, "Meat", "big_mac_1",
       "123456"},
      {"other_meat", "4.00", ::handlers::ProductTax::kX20, "Meat", "big_mac_1",
       "123456"},
      {"beat_2", "3.00", ::handlers::ProductTax::kX20, "Meat", "big_mac_1",
       "654321"}};

  const std::vector<handlers::Product> required_products = {
      {"big_mac_1", "7.00", ::handlers::ProductTax::kX20,
       "Big Mac Burger 1 (Meat (2 шт.))", std::nullopt, "123456"},
      {"beat_2", "3.00", ::handlers::ProductTax::kX20, "Meat", "big_mac_1",
       "654321"}};

  const auto flattened_products =
      helpers::products::FlattenProductList(initial_products);

  LOG_INFO() << flattened_products;
  ASSERT_EQ(flattened_products, required_products);
}

TEST(FlattenProductList, MultipleLevelInclusion) {
  const std::vector<handlers::Product> initial_products = {
      {"big_mac_1", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"meat", "2.05", ::handlers::ProductTax::kX20, "Meat", "big_mac_1",
       "123456"},
      {"big_mac_2", "2.00", ::handlers::ProductTax::kX20, "Big Mac Burger 2",
       std::nullopt, "654321"},
      {"ketchup", "4.16", ::handlers::ProductTax::kX20, "Heinz Ketchup", "meat",
       "123456"}};

  const std::vector<handlers::Product> required_products = {
      {"big_mac_1", "7.21", ::handlers::ProductTax::kX20,
       "Big Mac Burger 1 (Meat (Heinz Ketchup))", std::nullopt, "123456"},
      {"big_mac_2", "2.00", ::handlers::ProductTax::kX20, "Big Mac Burger 2",
       std::nullopt, "654321"}};

  const auto flattened_products =
      helpers::products::FlattenProductList(initial_products);
  ASSERT_EQ(flattened_products, required_products);
}

TEST(FlattenProductList, SingleLevelInclusionDifferentTaxInfo) {
  const std::vector<handlers::Product> initial_products = {
      {"big_mac_1", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"meat", "2.00", ::handlers::ProductTax::kX20, "Meat", "big_mac_1",
       "654321"},
      {"cheese", "3.00", ::handlers::ProductTax::kX10, "Cheese", "big_mac_1",
       "123456"}};

  const std::vector<handlers::Product> required_products = initial_products;

  const auto flattened_products =
      helpers::products::FlattenProductList(initial_products);
  ASSERT_EQ(flattened_products, required_products);
}

TEST(FlattenProductList, WrongParentItem) {
  const std::vector<handlers::Product> initial_products = {
      {"big_mac_1", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"meat", "2.00", ::handlers::ProductTax::kX20, "Meat", "small_mac_1",
       "123456"}};

  const std::vector<handlers::Product> required_products = initial_products;

  const auto flattened_products =
      helpers::products::FlattenProductList(initial_products);
  ASSERT_EQ(flattened_products, required_products);
}

TEST(FlattenProductList, MultipleLevelInclusionDifferentTaxInfo) {
  const std::vector<handlers::Product> initial_products = {
      {"big_mac_1", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"meat", "2.05", ::handlers::ProductTax::kX20, "Meat", "big_mac_1",
       "123456"},
      {"big_mac_2", "2.00", ::handlers::ProductTax::kX20, "Big Mac Burger 2",
       std::nullopt, "654321"},
      {"ketchup", "4.16", ::handlers::ProductTax::kX20, "Heinz Ketchup", "meat",
       "654321"}};

  const std::vector<handlers::Product> required_products = {
      {"big_mac_1", "3.05", ::handlers::ProductTax::kX20,
       "Big Mac Burger 1 (Meat)", std::nullopt, "123456"},
      {"big_mac_2", "2.00", ::handlers::ProductTax::kX20, "Big Mac Burger 2",
       std::nullopt, "654321"},
      {"ketchup", "4.16", ::handlers::ProductTax::kX20, "Heinz Ketchup", "meat",
       "654321"}};

  const auto flattened_products =
      helpers::products::FlattenProductList(initial_products);

  ASSERT_EQ(flattened_products, required_products);
}

TEST(FlattenProductList, VeryLongResultingName) {
  const std::vector<handlers::Product> initial_products = {
      {"big_mac_1", "1.00", ::handlers::ProductTax::kX20, "Big Mac Burger 1",
       std::nullopt, "123456"},
      {"meat", "2.00", ::handlers::ProductTax::kX20,
       "meatallworkandnoplaymakesjohnyadullbovallworkandnoplaymakesjohnyadullbo"
       "yallworkandnoplaymakesjohnyadullboyallworkandnoplaymakesjohnyadullboy",
       "big_mac_1", "123456"}};

  const std::vector<handlers::Product> required_products = {
      {"big_mac_1", "3.00", ::handlers::ProductTax::kX20,
       "Big Mac Burger 1 "
       "(meatallworkandnoplaymakesjohnyadullbovallworkandnoplaymakesjohnyadullb"
       "oyallworkandnoplaymakesjohnyadullboya...",
       std::nullopt, "123456"}};

  const auto flattened_products =
      helpers::products::FlattenProductList(initial_products);

  LOG_INFO() << "TEST";
  LOG_INFO() << flattened_products;
  ASSERT_EQ(flattened_products, required_products);
}
