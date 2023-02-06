#include <userver/utest/utest.hpp>

#include <userver/formats/bson/inline.hpp>
#include <userver/formats/bson/types.hpp>

#include <db/models/usages.hpp>

namespace coupons::db::usages::models {

namespace {
const auto kId = formats::bson::Oid("602e4f828fe28d5ce4fa1c62");
const std::string kCouponCode = "coupon123";
const std::string kOrderId = "8c3cc391dd7c38ff9279bff8268e2b6c";
const std::string kOtherOrderId = "3f14648b4e3dc236951b7ead4c5a39cb";
const std::string kToken = "aaww94qOZTC3BF7ACAW8";
const std::string kOtherToken = "lpMxODsBZ7hSkjIrzFJt";
}  // namespace

namespace fb = formats::bson;

TEST(CheckCouponUsage, UsageReserved) {
  const auto source = fb::MakeDoc("reserve", kOrderId);
  const auto usage = CouponUsage(source);

  EXPECT_EQ(usage.GetReserveKey(), kOrderId);
  EXPECT_EQ(usage.IsCommited(), false);
  EXPECT_EQ(usage.IsRollbacked(), false);
  EXPECT_EQ(usage.IsCommitedOrRollbacked(), false);
}

TEST(CheckCouponUsage, UsageReservedToken) {
  const auto source = fb::MakeDoc("reserve", kOrderId,  //
                                  "idempotency_tokens", fb::MakeArray(kToken));
  const auto usage = CouponUsage(source);

  EXPECT_EQ(usage.GetReserveKey(), kOrderId);
  EXPECT_EQ(usage.IsCommited(), false);
  EXPECT_EQ(usage.IsRollbacked(), false);
  EXPECT_EQ(usage.IsCommitedOrRollbacked(), false);
}

TEST(CheckCouponUsage, UsageCommited) {
  const auto source = fb::MakeDoc("reserve", kOrderId,  //
                                  "cost_usage", 2.5);
  const auto usage = CouponUsage(source);

  EXPECT_EQ(usage.GetReserveKey(), kOrderId);
  EXPECT_EQ(usage.IsCommited(), true);
  EXPECT_EQ(usage.IsRollbacked(), false);
  EXPECT_EQ(usage.IsCommitedOrRollbacked(), true);
}

TEST(CheckCouponUsage, UsageRollbacked) {
  const auto source = fb::MakeDoc("reserve", kOrderId,  //
                                  "idempotency_tokens", fb::MakeArray(kToken),
                                  "cancel_tokens", fb::MakeArray(kToken));
  const auto usage = CouponUsage(source);

  EXPECT_EQ(usage.GetReserveKey(), kOrderId);
  EXPECT_EQ(usage.IsCommited(), false);
  EXPECT_EQ(usage.IsRollbacked(), true);
  EXPECT_EQ(usage.IsCommitedOrRollbacked(), true);
}

TEST(CheckCouponUsage, UsageRollbackedMultipleTokens) {
  const auto source = fb::MakeDoc(
      "reserve", kOrderId,  //
      "idempotency_tokens", fb::MakeArray(kToken, kToken, kOtherToken),
      "cancel_tokens", fb::MakeArray(kToken, kOtherToken, kOtherToken));
  const auto usage = CouponUsage(source);

  EXPECT_EQ(usage.GetReserveKey(), kOrderId);
  EXPECT_EQ(usage.IsCommited(), false);
  EXPECT_EQ(usage.IsRollbacked(), true);
  EXPECT_EQ(usage.IsCommitedOrRollbacked(), true);
}

TEST(CheckCouponUsage, UsageNotFullyRollbacked) {
  const auto source =
      fb::MakeDoc("reserve", kOrderId,  //
                  "idempotency_tokens", fb::MakeArray(kToken, kOtherToken),
                  "cancel_tokens", fb::MakeArray(kToken));
  const auto usage = CouponUsage(source);

  EXPECT_EQ(usage.GetReserveKey(), kOrderId);
  EXPECT_EQ(usage.IsCommited(), false);
  EXPECT_EQ(usage.IsRollbacked(), false);
  EXPECT_EQ(usage.IsCommitedOrRollbacked(), false);
}

TEST(CheckCouponUsage, UsageMoreCancelTokens) {
  const auto source =
      fb::MakeDoc("reserve", kOrderId,  //
                  "idempotency_tokens", fb::MakeArray(kToken), "cancel_tokens",
                  fb::MakeArray(kToken, kOtherToken));
  const auto usage = CouponUsage(source);

  EXPECT_EQ(usage.GetReserveKey(), kOrderId);
  EXPECT_EQ(usage.IsCommited(), false);
  EXPECT_EQ(usage.IsRollbacked(), true);
  EXPECT_EQ(usage.IsCommitedOrRollbacked(), true);
}

TEST(CheckCouponUsages, NoUsages) {
  const auto source = fb::MakeDoc("_id", kId,           //
                                  "code", kCouponCode,  //
                                  "rides", 0,           //
                                  "usages", fb::MakeArray());
  const auto usages = CouponUsagesDoc(source);

  EXPECT_EQ(usages.GetCouponCode(), kCouponCode);
  EXPECT_EQ(usages.GetNumOrders(), 0);
  EXPECT_EQ(usages.GetUsages().size(), 0);
}

TEST(CheckCouponUsages, SingleUsage) {
  const auto source_usage = fb::MakeDoc("reserve", kOrderId);
  const auto source = fb::MakeDoc("_id", kId,           //
                                  "code", kCouponCode,  //
                                  "rides", 1,           //
                                  "usages", fb::MakeArray(source_usage));
  const auto usages = CouponUsagesDoc(source);

  EXPECT_EQ(usages.GetCouponCode(), kCouponCode);
  EXPECT_EQ(usages.GetNumOrders(), 1);
  EXPECT_EQ(usages.GetUsages().size(), 1);

  const auto usage = usages.GetUsageByReserveKey(kOrderId);
  EXPECT_TRUE(usage.has_value());
  EXPECT_EQ(usage->GetReserveKey(), kOrderId);
}

TEST(CheckCouponUsages, MultipleUsagesReserved) {
  const auto usage_commited =
      fb::MakeDoc("reserve", kOrderId,                          //
                  "idempotency_tokens", fb::MakeArray(kToken),  //
                  "cost_usage", 5);
  const auto usage_reserved = fb::MakeDoc("reserve", kOtherOrderId);
  const auto source =
      fb::MakeDoc("_id", kId,           //
                  "code", kCouponCode,  //
                  "rides", 2,           //
                  "cost_usage", 5,      //
                  "usages", fb::MakeArray(usage_commited, usage_reserved));
  const auto usages = CouponUsagesDoc(source);

  EXPECT_EQ(usages.GetNumOrders(), 2);
  EXPECT_EQ(usages.GetUsages().size(), 2);
  EXPECT_EQ(usages.GetCostUsage(), 5);
}

TEST(CheckCouponUsages, MultipleUsagesCommited) {
  const auto usage_commited_0 =
      fb::MakeDoc("reserve", kOrderId,                          //
                  "idempotency_tokens", fb::MakeArray(kToken),  //
                  "cost_usage", 5);
  const auto usage_commited_1 =
      fb::MakeDoc("reserve", kOtherOrderId,                          //
                  "idempotency_tokens", fb::MakeArray(kOtherToken),  //
                  "cost_usage", 5);
  const auto source =
      fb::MakeDoc("_id", kId,           //
                  "code", kCouponCode,  //
                  "rides", 2,           //
                  "cost_usage", 10,     //
                  "usages", fb::MakeArray(usage_commited_0, usage_commited_1));
  const auto usages = CouponUsagesDoc(source);

  EXPECT_EQ(usages.GetNumOrders(), 2);
  EXPECT_EQ(usages.GetUsages().size(), 2);
  EXPECT_EQ(usages.GetCostUsage(), 10);
}

TEST(CheckCouponUsages, MultipleUsagesRollbacked) {
  const auto usage_commited =
      fb::MakeDoc("reserve", kOrderId,                          //
                  "idempotency_tokens", fb::MakeArray(kToken),  //
                  "cost_usage", 5);
  const auto usage_rollbacked =
      fb::MakeDoc("reserve", kOtherOrderId,                          //
                  "idempotency_tokens", fb::MakeArray(kOtherToken),  //
                  "cancel_tokens", fb::MakeArray(kOtherToken));
  const auto source =
      fb::MakeDoc("_id", kId,           //
                  "code", kCouponCode,  //
                  "rides", 1,           //
                  "cost_usage", 5,      //
                  "usages", fb::MakeArray(usage_commited, usage_rollbacked));
  const auto usages = CouponUsagesDoc(source);

  EXPECT_EQ(usages.GetNumOrders(), 1);
  EXPECT_EQ(usages.GetUsages().size(), 2);
  EXPECT_EQ(usages.GetCostUsage(), 5);
}

TEST(CheckCouponUsages, BrokenRollbackIdempotencyEmptyUsages) {
  // See TAXIBACKEND-36364 for details.
  const auto source = fb::MakeDoc("_id", kId,           //
                                  "code", kCouponCode,  //
                                  "rides", -1,          //
                                  "usages", fb::MakeArray());
  const auto usages = CouponUsagesDoc(source);

  EXPECT_EQ(usages.GetNumOrders(), 0);
  EXPECT_EQ(usages.GetUsages().size(), 0);
}

TEST(CheckCouponUsages, BrokenRollbackIdempotency) {
  // See TAXIBACKEND-36364 for details.
  const auto usage_commited =
      fb::MakeDoc("reserve", kOrderId,                          //
                  "idempotency_tokens", fb::MakeArray(kToken),  //
                  "cost_usage", 5);
  const auto usage_rollbacked =
      fb::MakeDoc("reserve", kOtherOrderId,                          //
                  "idempotency_tokens", fb::MakeArray(kOtherToken),  //
                  "cancel_tokens", fb::MakeArray(kOtherToken));
  const auto source =
      fb::MakeDoc("_id", kId,           //
                  "code", kCouponCode,  //
                  "rides", 0,           //
                  "usages", fb::MakeArray(usage_commited, usage_rollbacked));
  const auto usages = CouponUsagesDoc(source);

  EXPECT_EQ(usages.GetNumOrders(), 1);
  EXPECT_EQ(usages.GetUsages().size(), 2);
}

TEST(CheckCouponUsages, ReserveRollbackRaceNoCommitedUsage) {
  // See TAXIBACKEND-36344 for details.
  // The same order is reserved and rollbacked with the same token.
  const auto usage_reserved =
      fb::MakeDoc("reserve", kOrderId,  //
                  "idempotency_tokens", fb::MakeArray(kToken));
  const auto usage_rollbacked =
      fb::MakeDoc("reserve", kOrderId,                          //
                  "idempotency_tokens", fb::MakeArray(kToken),  //
                  "cancel_tokens", fb::MakeArray(kToken));
  const auto source =
      fb::MakeDoc("_id", kId,           //
                  "code", kCouponCode,  //
                  "rides", 1,           //
                  "usages", fb::MakeArray(usage_reserved, usage_rollbacked));
  const auto usages = CouponUsagesDoc(source);

  // This duplicate (by reserve key) usages should be merged into one,
  // which is rollbacked by cancel token.
  EXPECT_EQ(usages.GetNumOrders(), 0);
  EXPECT_EQ(usages.GetUsages().size(), 1);
}

TEST(CheckCouponUsages, ReserveRollbackRaceReserveWithoutToken) {
  // See TAXIBACKEND-36344 for details.
  // The same order is reserved and rollbacked with the same token.
  const auto usage_reserved = fb::MakeDoc("reserve", kOrderId);
  const auto usage_rollbacked =
      fb::MakeDoc("reserve", kOrderId,                          //
                  "idempotency_tokens", fb::MakeArray(kToken),  //
                  "cancel_tokens", fb::MakeArray(kToken));
  const auto source =
      fb::MakeDoc("_id", kId,           //
                  "code", kCouponCode,  //
                  "rides", 1,           //
                  "usages", fb::MakeArray(usage_reserved, usage_rollbacked));
  const auto usages = CouponUsagesDoc(source);

  // This duplicate (by reserve key) usages should be merged into one,
  // which is rollbacked by cancel token.
  EXPECT_EQ(usages.GetNumOrders(), 0);
  EXPECT_EQ(usages.GetUsages().size(), 1);
}

TEST(CheckCouponUsages, ReserveRollbackRaceMultipleTokens) {
  // See TAXIBACKEND-36344 for details.
  // The same order is reserved and rollbacked with two tokens.
  const auto usage_reserved_0 =
      fb::MakeDoc("reserve", kOrderId,  //
                  "idempotency_tokens", fb::MakeArray(kToken));
  const auto usage_rollbacked_0 =
      fb::MakeDoc("reserve", kOrderId,                          //
                  "idempotency_tokens", fb::MakeArray(kToken),  //
                  "cancel_tokens", fb::MakeArray(kToken));
  const auto usage_reserved_1 =
      fb::MakeDoc("reserve", kOrderId,  //
                  "idempotency_tokens", fb::MakeArray(kOtherToken));
  const auto usage_rollbacked_1 =
      fb::MakeDoc("reserve", kOrderId,                               //
                  "idempotency_tokens", fb::MakeArray(kOtherToken),  //
                  "cancel_tokens", fb::MakeArray(kOtherToken));
  const auto source =
      fb::MakeDoc("_id", kId,           //
                  "code", kCouponCode,  //
                  "rides", 2,           //
                  "usages",
                  fb::MakeArray(usage_reserved_0, usage_rollbacked_0,
                                usage_reserved_1, usage_rollbacked_1));
  const auto usages = CouponUsagesDoc(source);

  // This duplicate (by reserve key) usages should be merged into one,
  // which is rollbacked by cancel token.
  EXPECT_EQ(usages.GetNumOrders(), 0);
  EXPECT_EQ(usages.GetUsages().size(), 1);
}

TEST(CheckCouponUsages, ReserveRollbackRaceMultipleOrders) {
  // See TAXIBACKEND-36344 for details.
  // Two orders are reserved and rollbacked with the same tokens.
  const auto usage_reserved_0 =
      fb::MakeDoc("reserve", kOrderId,  //
                  "idempotency_tokens", fb::MakeArray(kToken));
  const auto usage_rollbacked_0 =
      fb::MakeDoc("reserve", kOrderId,                          //
                  "idempotency_tokens", fb::MakeArray(kToken),  //
                  "cancel_tokens", fb::MakeArray(kToken));
  const auto usage_reserved_1 =
      fb::MakeDoc("reserve", kOtherOrderId,  //
                  "idempotency_tokens", fb::MakeArray(kOtherToken));
  const auto usage_rollbacked_1 =
      fb::MakeDoc("reserve", kOtherOrderId,                          //
                  "idempotency_tokens", fb::MakeArray(kOtherToken),  //
                  "cancel_tokens", fb::MakeArray(kOtherToken));
  const auto source =
      fb::MakeDoc("_id", kId,           //
                  "code", kCouponCode,  //
                  "rides", 2,           //
                  "usages",
                  fb::MakeArray(usage_reserved_0, usage_rollbacked_0,
                                usage_reserved_1, usage_rollbacked_1));
  const auto usages = CouponUsagesDoc(source);

  // This duplicate (by reserve key) usages should be merged into one,
  // which is rollbacked by cancel token.
  EXPECT_EQ(usages.GetNumOrders(), 0);
  EXPECT_EQ(usages.GetUsages().size(), 2);
}

TEST(CheckCouponUsages, ReserveRollbackRaceWithCommitedUsage) {
  // See TAXIBACKEND-36344 for details.
  // The same order is reserved and rollbacked with the same token.
  const auto usage_commited =
      fb::MakeDoc("reserve", kOrderId,                          //
                  "idempotency_tokens", fb::MakeArray(kToken),  //
                  "cost_usage", 5);
  const auto usage_rollbacked =
      fb::MakeDoc("reserve", kOtherOrderId,                          //
                  "idempotency_tokens", fb::MakeArray(kOtherToken),  //
                  "cancel_tokens", fb::MakeArray(kOtherToken));
  const auto usage_reserved =
      fb::MakeDoc("reserve", kOtherOrderId,  //
                  "idempotency_tokens", fb::MakeArray(kOtherToken));
  const auto source = fb::MakeDoc(
      "_id", kId,           //
      "code", kCouponCode,  //
      "rides", 2,           //
      "cost_usage", 5,      //
      "usages",
      fb::MakeArray(usage_commited, usage_rollbacked, usage_reserved));
  const auto usages = CouponUsagesDoc(source);

  // This duplicate (by reserve key) usages should be merged into one,
  // which is rollbacked by cancel token.
  EXPECT_EQ(usages.GetNumOrders(), 1);
  EXPECT_EQ(usages.GetUsages().size(), 2);
}

}  // namespace coupons::db::usages::models
