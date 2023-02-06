#include <userver/utest/utest.hpp>

#include <experiments3/alt_offer_discount_cache_settings.hpp>

#include <defs/definitions/v1_pricing_params.hpp>
#include <query_cache/key.hpp>

namespace alt_offer_discount::query_cache {

namespace {

using ValueCheckdestination =
    experiments3::alt_offer_discount_cache_settings::ValueCheckdestination;

handlers::V1PricingParamsRequest BuildRequest(const bool user_id,
                                              const bool phone_id,
                                              const bool payment_type,
                                              const int points_quantity,
                                              const bool user_obj = false) {
  handlers::V1PricingParamsRequest request;
  request.categories = {"ultima", "comfort"};
  if (user_id) {
    if (!request.user) {
      request.user.emplace();
    }
    request.user->user_id = "test_user_id";
  }
  if (phone_id) {
    if (!request.user) {
      request.user.emplace();
    }
    request.user->phone_id = "test_phone_id";
  }
  if (payment_type) {
    request.payment.emplace();
    request.payment->type = "ya_pay";
  }
  request.route.resize(points_quantity);
  if (user_obj) {
    request.user.emplace();
  }

  return request;
}

experiments3::AltOfferDiscountCacheSettings::Value BuildExp(
    const bool check_user_id, const bool check_phone_id,
    const bool check_payment_type,
    const ValueCheckdestination check_destination) {
  experiments3::AltOfferDiscountCacheSettings::Value exp;
  exp.check_user_id = check_user_id;
  exp.check_phone_id = check_phone_id;
  exp.check_payment_type = check_payment_type;
  exp.check_destination = check_destination;
  exp.geohash_precision = 11;

  return exp;
}

}  // namespace

TEST(GetCacheKey, Base) {
  EXPECT_EQ(GetCacheKey(                            //
                BuildRequest(true, true, true, 3),  //
                BuildExp(true, true, true, ValueCheckdestination::kExistence)),
            "cache/"
            "categories:comfort,ultima;"
            "destination:true;"
            "order_point_geohash:7zzzzzzzzzz;"
            "payment_type:ya_pay;"
            "phone_id:test_phone_id;"
            "user_id:test_user_id");

  EXPECT_EQ(GetCacheKey(                            //
                BuildRequest(true, true, true, 1),  //
                BuildExp(true, true, true, ValueCheckdestination::kExistence)),
            "cache/"
            "categories:comfort,ultima;"
            "destination:false;"
            "order_point_geohash:7zzzzzzzzzz;"
            "payment_type:ya_pay;"
            "phone_id:test_phone_id;"
            "user_id:test_user_id");

  EXPECT_EQ(GetCacheKey(                               //
                BuildRequest(false, false, false, 1),  //
                BuildExp(true, true, true, ValueCheckdestination::kExistence)),
            "cache/"
            "categories:comfort,ultima;"
            "destination:false;"
            "order_point_geohash:7zzzzzzzzzz;"
            "payment_type:null;"
            "phone_id:null;"
            "user_id:null");

  EXPECT_EQ(GetCacheKey(                            //
                BuildRequest(true, true, true, 1),  //
                BuildExp(false, false, false, ValueCheckdestination::kIgnore)),
            "cache/"
            "categories:comfort,ultima;"
            "order_point_geohash:7zzzzzzzzzz");

  EXPECT_EQ(
      GetCacheKey(                            //
          BuildRequest(true, true, true, 3),  //
          BuildExp(false, false, false, ValueCheckdestination::kEquality)),
      "cache/"
      "categories:comfort,ultima;"
      "destination:7zzzzzzzzzz,7zzzzzzzzzz;"
      "order_point_geohash:7zzzzzzzzzz");

  EXPECT_EQ(
      GetCacheKey(                            //
          BuildRequest(true, true, true, 1),  //
          BuildExp(false, false, false, ValueCheckdestination::kEquality)),
      "cache/"
      "categories:comfort,ultima;"
      "destination:null;"
      "order_point_geohash:7zzzzzzzzzz");
}

TEST(GetCacheKey, UserIsNotNull) {
  EXPECT_EQ(GetCacheKey(                                     //
                BuildRequest(false, false, false, 1, true),  //
                BuildExp(true, true, false, ValueCheckdestination::kIgnore)),
            "cache/"
            "categories:comfort,ultima;"
            "order_point_geohash:7zzzzzzzzzz;"
            "phone_id:null;"
            "user_id:null");
}

}  // namespace alt_offer_discount::query_cache
