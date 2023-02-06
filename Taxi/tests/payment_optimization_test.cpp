#include <gtest/gtest.h>

#include <helpers/debt_collector/debt_product.hpp>
#include <helpers/debt_collector/payment_optimization.hpp>

using Product = helpers::debt_product::Product;

namespace {
std::pair<std::vector<Product>, std::vector<Product>> SortResult(
    const std::pair<std::vector<Product>, std::vector<Product>>& result) {
  auto sort_function = [](const Product& lhs, const Product& rhs) {
    return lhs.identity < rhs.identity;
  };
  auto to_eda_transactions = result.first;
  auto to_debt_collector = result.second;

  std::sort(to_eda_transactions.begin(), to_eda_transactions.end(),
            sort_function);
  std::sort(to_debt_collector.begin(), to_debt_collector.end(), sort_function);

  return std::make_pair(to_eda_transactions, to_debt_collector);
}

}  // namespace

TEST(PaymentOptimization, ExpensiveItems) {
  std::vector<Product> input;

  Product product1;
  product1.identity = "identity1";
  product1.cost_for_customer = Decimal{30};

  Product product2;
  product2.identity = "identity2";
  product2.cost_for_customer = Decimal{100};

  input.push_back(product1);
  input.push_back(product2);

  auto result = helpers::debt_collector::OptimizeHeldAmount(input, Decimal{20});

  std::pair<std::vector<Product>, std::vector<Product>> output = {
      {}, {product1, product2}};

  ASSERT_EQ(SortResult(std::move(result)), output);
}

TEST(PaymentOptimization, HeldAmountCoversAllProducts) {
  std::vector<Product> input;

  Product product1;
  product1.identity = "identity1";
  product1.cost_for_customer = Decimal{10};

  Product product2;
  product2.identity = "identity2";
  product2.cost_for_customer = Decimal{20};

  Product product3;
  product3.identity = "identity3";
  product3.cost_for_customer = Decimal{30};

  input.push_back(product1);
  input.push_back(product2);
  input.push_back(product3);

  auto result =
      helpers::debt_collector::OptimizeHeldAmount(input, Decimal{100});

  std::pair<std::vector<Product>, std::vector<Product>> output = {
      {product1, product2, product3}, {}};

  ASSERT_EQ(SortResult(std::move(result)), output);
}

TEST(PaymentOptimization, SimpleCase) {
  std::vector<Product> input;

  Product product1;
  product1.identity = "identity1";
  product1.cost_for_customer = Decimal{6};

  Product product2;
  product2.identity = "identity2";
  product2.cost_for_customer = Decimal{5};

  Product product3;
  product3.identity = "identity3";
  product3.cost_for_customer = Decimal{1};

  Product product4;
  product4.identity = "identity4";
  product4.cost_for_customer = Decimal{1};

  input.push_back(product1);
  input.push_back(product2);
  input.push_back(product3);
  input.push_back(product4);

  auto result = helpers::debt_collector::OptimizeHeldAmount(input, Decimal{12});

  std::pair<std::vector<Product>, std::vector<Product>> output = {
      {product1, product2, product3}, {product4}};

  ASSERT_EQ(SortResult(std::move(result)), output);
}

TEST(PaymentOptimization, CaseWithProductsWithSmallerAmount) {
  std::vector<Product> input;

  Product product1;
  product1.identity = "identity1";
  product1.cost_for_customer = Decimal{5};

  Product product2;
  product2.identity = "identity2";
  product2.cost_for_customer = Decimal{5};

  Product product3;
  product3.identity = "identity3";
  product3.cost_for_customer = Decimal{2};

  Product product4;
  product4.identity = "identity4";
  product4.cost_for_customer = Decimal{2};

  Product product5;
  product5.identity = "identity5";
  product5.cost_for_customer = Decimal{2};

  input.push_back(product1);
  input.push_back(product2);
  input.push_back(product3);
  input.push_back(product4);
  input.push_back(product5);

  auto result = helpers::debt_collector::OptimizeHeldAmount(input, Decimal{6});

  std::pair<std::vector<Product>, std::vector<Product>> output = {
      {product3, product4, product5}, {product1, product2}};

  ASSERT_EQ(SortResult(std::move(result)), output);
}

TEST(PaymentOptimization, CaseMixPrices) {
  std::vector<Product> input;

  Product product1;
  product1.identity = "identity1";
  product1.cost_for_customer = Decimal{100};

  Product product2;
  product2.identity = "identity2";
  product2.cost_for_customer = Decimal{20};

  Product product3;
  product3.identity = "identity3";
  product3.cost_for_customer = Decimal{12};

  Product product4;
  product4.identity = "identity4";
  product4.cost_for_customer = Decimal{20};

  Product product5;
  product5.identity = "identity5";
  product5.cost_for_customer = Decimal{6};

  Product product6;
  product6.identity = "identity6";
  product6.cost_for_customer = Decimal{6};

  Product product7;
  product7.identity = "identity7";
  product7.cost_for_customer = Decimal{6};

  Product product8;
  product8.identity = "identity8";
  product8.cost_for_customer = Decimal{6};

  input.push_back(product1);
  input.push_back(product2);
  input.push_back(product3);
  input.push_back(product4);
  input.push_back(product5);
  input.push_back(product6);
  input.push_back(product7);
  input.push_back(product8);

  auto result =
      helpers::debt_collector::OptimizeHeldAmount(input, Decimal{136});

  std::pair<std::vector<Product>, std::vector<Product>> output = {
      {product1, product3, product5, product6, product7, product8},
      {product2, product4}};

  ASSERT_EQ(SortResult(std::move(result)), output);
}

TEST(PaymentOptimization, DoublePrices) {
  std::vector<Product> input;

  Product product1;
  product1.identity = "identity1";
  product1.cost_for_customer = Decimal{"15.36"};

  Product product2;
  product2.identity = "identity2";
  product2.cost_for_customer = Decimal{"10.57"};

  Product product3;
  product3.identity = "identity3";
  product3.cost_for_customer = Decimal{"125.73"};

  Product product4;
  product4.identity = "identity4";
  product4.cost_for_customer = Decimal{"48.69"};

  input.push_back(product1);
  input.push_back(product2);
  input.push_back(product3);
  input.push_back(product4);

  auto result = helpers::debt_collector::OptimizeHeldAmount(input, Decimal{60});

  std::pair<std::vector<Product>, std::vector<Product>> output = {
      {product2, product4}, {product1, product3}};

  ASSERT_EQ(SortResult(std::move(result)), output);
}
