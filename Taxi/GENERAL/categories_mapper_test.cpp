#include "categories_mapper.hpp"

#include <userver/utest/utest.hpp>

namespace utils {

typedef taxi_config::opteum_report_payouts_transaction_products::
    AdditionalPrefixes AdditionalPrefixes;

auto mapper = CategoriesMapper({
    {
        {
            {
                "ALFA",
            },
            {
                "VTB",
            },
            {
                "RBK_MONEY",
            },
        },
        "cashless",
        "category_cashless",
    },
    {
        {
            {
                "ECOMMPAY",
                "tips",
            },
            {
                "VTB",
                "tips",
            },
            {
                "SBERBANK",
                "tips",
            },
        },
        "tips",
        "category_tips",
    },
    {
        {
            {
                "YA_CORPORATE",
            },
            {"client_b2b_trip_payment",
             "client_b2b_trip_payment",
             {{AdditionalPrefixes::kCargo}}},
            {"park_b2b_trip_payment",
             "rebate_b2b_trip_payment_test",
             {{AdditionalPrefixes::kCargo, AdditionalPrefixes::kDelivery}}},
        },
        "corporate",
        "category_corporate",
    },
});

TEST(CategoriesMapperTest, GetCategoryByProduct) {
  EXPECT_EQ(mapper.GetCategoryByProduct("VTB"), "cashless");
  EXPECT_EQ(mapper.GetCategoryByProduct("VTB", "tips"), "tips");
  EXPECT_EQ(mapper.GetCategoryByProduct("delivery_park_b2b_trip_payment",
                                        "rebate_b2b_trip_payment_test"),
            "corporate");
  EXPECT_EQ(mapper.GetCategoryByProduct("bla-bla-bla"), "other");
}

TEST(CategoriesMapperTest, GetProductsByCategory) {
  auto products = mapper.GetProductsByCategory("corporate");
  EXPECT_EQ(products.size(), 6);
  EXPECT_EQ(products[0].first, "YA_CORPORATE");
  EXPECT_EQ(products[0].second, std::nullopt);
  EXPECT_EQ(products[1].first, "client_b2b_trip_payment");
  EXPECT_EQ(products[1].second, "client_b2b_trip_payment");
  EXPECT_EQ(products[2].first, "cargo_client_b2b_trip_payment");
  EXPECT_EQ(products[2].second, "client_b2b_trip_payment");
  EXPECT_EQ(products[3].first, "park_b2b_trip_payment");
  EXPECT_EQ(products[3].second, "rebate_b2b_trip_payment_test");
  EXPECT_EQ(products[4].first, "cargo_park_b2b_trip_payment");
  EXPECT_EQ(products[4].second, "rebate_b2b_trip_payment_test");
  EXPECT_EQ(products[5].first, "delivery_park_b2b_trip_payment");
  EXPECT_EQ(products[5].second, "rebate_b2b_trip_payment_test");
}

}  // namespace utils
