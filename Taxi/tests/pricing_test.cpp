#include <grocery-discounts-calculator/pricing.hpp>

#include <userver/utest/utest.hpp>

namespace grocery_discounts_calculator {

using ProductId = grocery_shared::ProductId;
using grocery_pricing::Numeric;

// История созданных элементов находится, несозданных — не находится.
TEST(Pricing, contains_history_of_initialized_products) {
  const auto pricing = Pricing{
      {ProductPricing(ProductId{"product-1"}, Numeric{100}, Numeric{1}),
       ProductPricing(ProductId{"product-2"}, Numeric{200}, Numeric{1})},
      Numeric{1}};

  ASSERT_NE(History(pricing, ProductId{"product-1"}),
            pricing.product_pricings.end());
  ASSERT_NE(History(pricing, ProductId{"product-2"}),
            pricing.product_pricings.end());

  ASSERT_EQ(History(pricing, ProductId{"absent-product"}),
            pricing.product_pricings.end());
}

// При инициализации история содержит только начальную цену.
TEST(Pricing, initial_history_contains_only_initial_price) {
  const auto pricing =
      Pricing{{ProductPricing(ProductId{"product-1"}, Numeric{99}, Numeric{1})},
              Numeric{1}};

  ASSERT_EQ(History(pricing, ProductId{"product-1"})->steps.size(), 1);
  ASSERT_EQ((History(pricing, ProductId{"product-1"})->steps.front()),
            (Step{Bag{Pack{Numeric{99}, Numeric{1}}}}));
}

}  // namespace grocery_discounts_calculator
