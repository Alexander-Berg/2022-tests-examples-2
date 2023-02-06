#include <gtest/gtest.h>

#include <taxi_config/variables/CANDIDATES_SKIP_PAYMENT_METHOD_BY_CORP.hpp>

#include <filters/grocery/fetch_shifts/fetch_shifts.hpp>
#include <filters/infrastructure/fetch_payment_methods/fetch_payment_methods.hpp>
#include <filters/partners/fetch_eats_shifts/fetch_eats_shifts.hpp>
#include <testing/taxi_config.hpp>
#include "driver_payment_type/models/models.hpp"
#include "payment_method.hpp"

namespace cf = candidates::filters;
namespace cfi = cf::infrastructure;
namespace dpt = driver_payment_type;

using cf::Result;

static cf::FilterInfo kEmptyInfo;

TEST(PaymentMethodTest, TestCashAndCard) {
  cf::Context context;
  cfi::FetchPaymentMethods::Set(
      context, {dpt::OrderPaymentType::kCard, dpt::OrderPaymentType::kCash});
  {
    auto s = dpt::order_types::kCard;
    cfi::PaymentMethod filter(kEmptyInfo, s, {});
    EXPECT_EQ(Result::kAllow, filter.Process({}, context));
  }
  {
    cfi::PaymentMethod filter(kEmptyInfo, "cash", {});
    EXPECT_EQ(Result::kAllow, filter.Process({}, context));
  }
  {
    cfi::PaymentMethod filter(kEmptyInfo, "corp", {});
    EXPECT_EQ(Result::kDisallow, filter.Process({}, context));
  }
  {
    cfi::PaymentMethod filter(kEmptyInfo, "coupon", {});
    EXPECT_EQ(Result::kDisallow, filter.Process({}, context));
  }
}

TEST(PaymentMethodTest, TestCorp) {
  cf::Context context;
  cfi::FetchPaymentMethods::Set(context, {dpt::OrderPaymentType::kCorp});
  {
    cfi::PaymentMethod filter(kEmptyInfo, "card", {});
    EXPECT_EQ(Result::kDisallow, filter.Process({}, context));
  }
  {
    cfi::PaymentMethod filter(kEmptyInfo, "cash", {});
    EXPECT_EQ(Result::kDisallow, filter.Process({}, context));
  }
  {
    cfi::PaymentMethod filter(kEmptyInfo, "corp", {});
    EXPECT_EQ(Result::kAllow, filter.Process({}, context));
  }
  {
    cfi::PaymentMethod filter(kEmptyInfo, "coupon", {});
    EXPECT_EQ(Result::kDisallow, filter.Process({}, context));
  }
}

TEST(PaymentMethodTest, TestEatsShift) {
  cf::Context context;
  cfi::FetchPaymentMethods::Set(context, {dpt::OrderPaymentType::kCoupon});

  cfi::PaymentMethod filter(kEmptyInfo, "corp", {},
                            cfi::PaymentMethod::ShiftType::kEats);
  EXPECT_EQ(Result::kDisallow, filter.Process({}, context));

  cf::grocery::FetchShifts::Set(
      context, std::make_shared<models::GroceryShift>(models::GroceryShift{}));
  EXPECT_EQ(Result::kDisallow, filter.Process({}, context));

  cf::partners::FetchEatsShifts::Set(
      context, std::make_shared<models::EatsShift>(models::EatsShift{}));
  EXPECT_EQ(Result::kAllow, filter.Process({}, context));
}

TEST(PaymentMethodTest, TestGroceryShift) {
  cf::Context context;
  cfi::FetchPaymentMethods::Set(context, {dpt::OrderPaymentType::kCoupon});

  cfi::PaymentMethod filter(kEmptyInfo, "corp", {},
                            cfi::PaymentMethod::ShiftType::kGrocery);
  EXPECT_EQ(Result::kDisallow, filter.Process({}, context));

  cf::partners::FetchEatsShifts::Set(
      context, std::make_shared<models::EatsShift>(models::EatsShift{}));
  // TODO disallow after LAVKALOGDEV-644
  EXPECT_EQ(Result::kAllow, filter.Process({}, context));

  cf::grocery::FetchShifts::Set(
      context, std::make_shared<models::GroceryShift>(models::GroceryShift{}));
  EXPECT_EQ(Result::kAllow, filter.Process({}, context));
}
