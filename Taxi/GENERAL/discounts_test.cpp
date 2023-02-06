#include <gtest/gtest.h>

#include <clients/eats-order-revision/definitions.hpp>

#include "discounts.hpp"
#include "models/order_history.hpp"

namespace eats_retail_order_history::models {

bool operator==(const models::DiscountInfo& lhs,
                const models::DiscountInfo& rhs) {
  return std::tie(lhs.id, lhs.discriminator_type, lhs.discount_type,
                  lhs.discount_provider, lhs.code, lhs.discount_percents,
                  lhs.discount_limit, lhs.discount_money) ==
         std::tie(rhs.id, rhs.discriminator_type, rhs.discount_type,
                  rhs.discount_provider, rhs.code, rhs.discount_percents,
                  rhs.discount_limit, rhs.discount_money);
}

}  // namespace eats_retail_order_history::models

using namespace eats_retail_order_history;

TEST(TestDiscountVisitor, EdaCorePromo) {
  using namespace clients::eats_order_revision;
  EdaCorePromo eda_core_promo{EdaCorePromoDiscriminatortype::kEdaCorePromo,
                              "promo"};
  DiscountInfo client_discount_info(eda_core_promo);
  auto discount_info = discounts::ParseDiscountInfo(client_discount_info);
  ASSERT_TRUE(discount_info.has_value());
  models::DiscountInfo expected_discount_info;
  expected_discount_info.discriminator_type = "eda_core_promo";
  expected_discount_info.discount_type = "promo";
  ASSERT_EQ(discount_info.value(), expected_discount_info);
}

TEST(TestDiscountVisitor, EdaCorePromocode) {
  using namespace clients::eats_order_revision;
  EdaCorePromocode eda_core_promocode{
      EdaCorePromocodeDiscriminatortype::kEdaCorePromocode, "promocode"};
  DiscountInfo client_discount_info(eda_core_promocode);
  auto discount_info = discounts::ParseDiscountInfo(client_discount_info);
  ASSERT_TRUE(discount_info.has_value());
  models::DiscountInfo expected_discount_info;
  expected_discount_info.discriminator_type = "eda_core_promocode";
  expected_discount_info.code = "promocode";
  ASSERT_EQ(discount_info.value(), expected_discount_info);
}

TEST(TestDiscountVisitor, EatsDiscount) {
  using namespace clients::eats_order_revision;
  EatsDiscount eats_discount{EatsDiscountDiscriminatortype::kEatsDiscount,
                             "eats_discount", DiscountProvider::kOwn, "id",
                             "external_id"};
  DiscountInfo client_discount_info(eats_discount);
  auto discount_info = discounts::ParseDiscountInfo(client_discount_info);
  ASSERT_TRUE(discount_info.has_value());
  models::DiscountInfo expected_discount_info;
  expected_discount_info.id = "id";
  expected_discount_info.external_id = "external_id";
  expected_discount_info.discriminator_type = "eats_discount";
  expected_discount_info.discount_type = "eats_discount";
  expected_discount_info.discount_provider = "own";
  ASSERT_EQ(discount_info.value(), expected_discount_info);
}

TEST(TestDiscountVisitor, UnknownDiscount) {
  using namespace clients::eats_order_revision;
  struct UnknownDiscount {};
  std::variant<EdaCorePromo, EdaCorePromocode, UnknownDiscount>
      client_discount_info(UnknownDiscount{});
  // Проверяем, что код компилируется (была ситуация, когда в соседнем ПР
  // добавили новый тип в DiscountInfo)
  auto discount_info =
      std::visit(discounts::DiscountVisitor{}, client_discount_info);
  ASSERT_FALSE(discount_info.has_value());
}
