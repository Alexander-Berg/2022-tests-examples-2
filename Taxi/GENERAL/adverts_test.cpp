#include <eats-adverts-goods/models/adverts.hpp>

#include <eats-adverts-goods/utils/tests.hpp>

#include <userver/dump/test_helpers.hpp>

#include <gtest/gtest.h>

namespace eats_adverts_goods::models {

bool operator==(const Place& lhs, const Place& rhs) {
  return std::tie(lhs.place_id, lhs.products) ==
         std::tie(rhs.place_id, rhs.products);
}

}  // namespace eats_adverts_goods::models

namespace eats_adverts_goods::models {

namespace {

struct ProductIsSuitableTestCase {
  std::string name{};
  Product product{};
  CategoryId category_id{};
  bool expected{};
};

}  // namespace

class ProductIsSuitableTest
    : public ::testing::TestWithParam<ProductIsSuitableTestCase> {};

TEST_P(ProductIsSuitableTest, Test) {
  const auto param = GetParam();
  const auto actual = IsSuitable(param.product, param.category_id);
  ASSERT_EQ(param.expected, actual);
}

std::vector<ProductIsSuitableTestCase> MakeProductIsSuitableTestCases();

INSTANTIATE_TEST_SUITE_P(ProductIsSuitable, ProductIsSuitableTest,
                         ::testing::ValuesIn(MakeProductIsSuitableTestCases()),
                         [](const auto& test_case) -> std::string {
                           return utils::tests::GetName(test_case.param);
                         });

std::vector<ProductIsSuitableTestCase> MakeProductIsSuitableTestCases() {
  return {
      {
          "suitable because no suitable and no non-suitable categories",  // name
          Product{
              ProductId{"1"},  // product_id
              {},              // suitable_categories
              {},              // non_suitable_categories
          },                   // product
          CategoryId{"1"},     // category_id
          true,                // expected
      },
      {
          "has suitable categories",  // name
          Product{
              ProductId{"1"},     // product_id
              {CategoryId{"1"}},  // suitable_categories
              {},                 // non_suitable_categories
          },                      // product
          CategoryId{"1"},        // category_id
          true,                   // expected
      },
      {
          "has non-matching non-suitable categories",  // name
          Product{
              ProductId{"1"},     // product_id
              {},                 // suitable_categories
              {CategoryId{"2"}},  // non_suitable_categories
          },                      // product
          CategoryId{"1"},        // category_id
          true,                   // expected
      },
      {
          "has matching non-suitable categories",  // name
          Product{
              ProductId{"1"},     // product_id
              {},                 // suitable_categories
              {CategoryId{"1"}},  // non_suitable_categories
          },                      // product
          CategoryId{"1"},        // category_id
          false,                  // expected
      },
      {
          "has non-matching suitable categories",  // name
          Product{
              ProductId{"1"},     // product_id
              {CategoryId{"2"}},  // suitable_categories
              {},                 // non_suitable_categories
          },                      // product
          CategoryId{"1"},        // category_id
          false,                  // expected
      },
  };
}

TEST(Product, IsDumpable) {
  const Product product{
      ProductId{"1"},     // product_id
      {CategoryId{"2"}},  // suitable_categories
      {CategoryId{"3"}},  // non_suitable_categories
  };

  dump::TestWriteReadCycle(product);
}

TEST(Place, IsDumpable) {
  const Place place{
      PlaceId{1},  // place_id
      {
          {
              ProductId{"1"},     // product_id
              {CategoryId{"2"}},  // suitable_categories
              {CategoryId{"3"}},  // non_suitable_categories
          },
          {
              ProductId{"2"},                      // product_id
              {CategoryId{"3"}, CategoryId{"4"}},  // suitable_categories
              {},                                  // non_suitable_categories
          },
          {
              ProductId{"3"},                        // product_id
              {},                                    // suitable_categories
              {CategoryId{"10"}, CategoryId{"20"}},  // non_suitable_categories
          },
      },  // products
  };

  dump::TestWriteReadCycle(place);
}

}  // namespace eats_adverts_goods::models
