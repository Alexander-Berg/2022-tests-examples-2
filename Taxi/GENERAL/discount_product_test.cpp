#include <helpers/discount_product.hpp>

#include <gtest/gtest.h>

#include <clients/eats-nomenclature/definitions.hpp>

namespace {
using ProductV1 = clients::eats_nomenclature::ItemResult;
using ProductV2 = clients::eats_nomenclature::ProductDetailsV2;

struct Products {
  ProductV1 product;
  ProductV2 product_v2;
};

template <class Product>
Product MakeProduct(double price, std::optional<double> old_price) {
  Product product;
  product.price = price;
  product.old_price = old_price;
  return product;
}

Products MakeProducts(double price, std::optional<double> old_price) {
  Products products;
  products.product = MakeProduct<ProductV1>(price, old_price);
  products.product_v2 = MakeProduct<ProductV2>(price, old_price);
  return products;
}

void AssertProducts(const Products& products, bool expected_value) {
  EXPECT_EQ(eats_products::helpers::HasValidDiscount(products.product),
            expected_value);
  EXPECT_EQ(eats_products::helpers::HasValidDiscount(products.product),
            expected_value);
}

}  // namespace

TEST(HasValidDiscount, HasDiscount) {
  AssertProducts(MakeProducts(100, 150), true);
  AssertProducts(MakeProducts(100, 101), true);
  AssertProducts(MakeProducts(99, 100), true);
}

TEST(HasValidDiscount, NoDiscount) {
  AssertProducts(MakeProducts(100, std::nullopt), false);
}

TEST(HasValidDiscount, NoDiscountEqualPrices) {
  AssertProducts(MakeProducts(100, 100), false);
}

TEST(HasValidDiscount, NoDiscountWrongPrices) {
  AssertProducts(MakeProducts(150, 100), false);
  AssertProducts(MakeProducts(101, 100), false);
  AssertProducts(MakeProducts(100, 99), false);
}
