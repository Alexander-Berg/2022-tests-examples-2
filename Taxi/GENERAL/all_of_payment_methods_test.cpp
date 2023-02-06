#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_payment_methods/fetch_payment_methods.hpp>
#include "all_of_payment_methods.hpp"
#include "driver_payment_type/models/models.hpp"

namespace cf = candidates::filters;
namespace cfi = cf::infrastructure;
namespace dpt = driver_payment_type;

using cf::Result;
using dpt::OrderPaymentType;

static cf::FilterInfo kEmptyInfo;

TEST(AllOfPaymentMethodTest, Test) {
  {
    cf::Context context;
    cfi::FetchPaymentMethods::Set(context, {OrderPaymentType::kCorp});
    cfi::AllOfPaymentMethods filter(kEmptyInfo, {OrderPaymentType::kCard});
    EXPECT_EQ(Result::kDisallow, filter.Process({}, context));
    cfi::FetchPaymentMethods::Set(
        context, {OrderPaymentType::kCorp, OrderPaymentType::kCard});
    EXPECT_EQ(Result::kAllow, filter.Process({}, context));
  }
  {
    cf::Context context;
    cfi::FetchPaymentMethods::Set(context, {OrderPaymentType::kCorp});
    cfi::AllOfPaymentMethods filter(
        kEmptyInfo, {OrderPaymentType::kCard, OrderPaymentType::kCorp});
    EXPECT_EQ(Result::kDisallow, filter.Process({}, context));
    cfi::FetchPaymentMethods::Set(
        context, {OrderPaymentType::kCorp, OrderPaymentType::kCash});
    EXPECT_EQ(Result::kDisallow, filter.Process({}, context));
    cfi::FetchPaymentMethods::Set(
        context, {OrderPaymentType::kCorp, OrderPaymentType::kCash,
                  OrderPaymentType::kCard});
    EXPECT_EQ(Result::kAllow, filter.Process({}, context));
  }
  {
    cf::Context context;
    cfi::FetchPaymentMethods::Set(
        context, {OrderPaymentType::kCorp, OrderPaymentType::kCash,
                  OrderPaymentType::kCard, OrderPaymentType::kCoupon});
    cfi::AllOfPaymentMethods filter(
        kEmptyInfo, {OrderPaymentType::kCard, OrderPaymentType::kCorp,
                     OrderPaymentType::kCoupon, OrderPaymentType::kCash});
    EXPECT_EQ(Result::kAllow, filter.Process({}, context));
  }
}
