#include <gtest/gtest.h>
#include <mongo/bson/bson.h>
#include <mongo/db/json.h>

#include <ios>
#include <sstream>

#include <clients/cardstorage.hpp>
#include <common/test_config.hpp>
#include <config/config.hpp>
#include <orderkit/commitstate.hpp>
#include <orderkit/commitstate_internal.hpp>
#include <utils/helpers/json.hpp>
#include "orderkit/models/auction.hpp"

namespace {
config::Config GetConfig(int time) {
  config::DocsMap docs_map = config::DocsMapForTest();
  docs_map.Override<int>("URGENT_URGENCY", time);
  docs_map.Override<int>("DEFAULT_URGENCY", 600);
  return config::Config(docs_map);
}

bool SameJson(const Json::Value& a, const Json::Value& b) {
  if (a == b) {
    return true;
  }
  std::cout << "SameJson: json differs:" << std::endl;
  std::cout << "Got:" << std::endl << a << std::endl;
  std::cout << "Expected:" << std::endl << b << std::endl;
  return false;
}
}  // namespace

TEST(CheckCommitStates, PrepareOrderUpdate) {
  using namespace orderkit;
  Json::Value set;
  set["set_something"] = "set_value";

  Json::Value unset;
  unset["unset_something"] = "unset_value";

  Json::Value date;
  date["date_something"] = "date_value";

  mongo::BSONObj set_update = mongo::fromjson(set.toStyledString());
  mongo::BSONObj unset_update = mongo::fromjson(unset.toStyledString());
  mongo::BSONObj date_update = mongo::fromjson(date.toStyledString());
  internal::Update update{set_update, unset_update, date_update,
                          utils::mongo::empty_obj, std::nullopt};
  mongo::BSONObj prepared_obj = internal::PrepareOrderUpdate(
      update, models::orders::commit_states::Reserved);

  Json::Value res = utils::helpers::ParseJson(mongo::tojson(prepared_obj));

  Json::Value expected;
  expected["$set"]["commit_state"] = "reserved";
  expected["$set"]["set_something"] = "set_value";
  expected["$unset"]["unset_something"] = "unset_value";
  expected["$currentDate"]["updated"] = true;
  expected["$currentDate"]["date_something"] = "date_value";

  ASSERT_TRUE(SameJson(res, expected));
}

TEST(CheckCommitStates, DetectType) {
  using namespace orderkit;
  config::Config config = GetConfig(100);

  models::orders::Order order;
  order.type = models::orders::types::Soon;
  ASSERT_EQ(internal::DetectType(config, order), "soon");

  order.type = models::orders::types::Exact;
  order.request.due = utils::datetime::Now();
  ASSERT_EQ(internal::DetectType(config, order), "urgent");

  order.type = models::orders::types::Exact;
  order.request.due = utils::datetime::Now() + std::chrono::seconds(110);
  ASSERT_EQ(internal::DetectType(config, order), "exacturgent");
}

TEST(CheckCommitStates, PrepareDoneUpdate) {
  using namespace orderkit;

  config::Config config = GetConfig(100);

  models::order_proc::OrderProc order_proc;
  LogExtra log_extra;
  auto update = internal::PrepareDoneUpdate(order_proc, {}, {}, {}, log_extra);
  mongo::BSONObj prepared_obj = internal::PrepareOrderUpdate(
      update, models::orders::commit_states::Type::Done, log_extra);

  Json::Value res = utils::helpers::ParseJson(mongo::tojson(prepared_obj));

  ASSERT_FALSE(res["$set"]["order.request.due"]["$date"].asString().empty());
  res["$set"]["order.request.due"]["$date"] = "should_be_valid";

  Json::Value event;  // Extra payload in new ProcaaS flow
  event["s"] = "pending";
  Json::Value expected;
  expected["$push"]["order_info.statistics.status_updates"] = event;
  expected["$set"]["commit_state"] = "done";
  expected["$set"]["free_cancel_for_reason"] = false;
  expected["$set"]["fwd_driver_phone"] = false;
  expected["$set"]["status"] = "pending";
  expected["$set"]["order.status"] = "pending";
  expected["$set"]["order.rsk"] = "";
  expected["$set"]["order.request.due"]["$date"] = "should_be_valid";
  expected["$set"]["processing.need_start"] = true;
  expected["$currentDate"]["updated"] = true;
  expected["$currentDate"]["order.status_updated"] = true;
  ASSERT_TRUE(SameJson(res, expected));
}

TEST(CheckCommitStates, UpdateWithCoupon) {
  using namespace orderkit;

  mongo::BSONObjBuilder builder1;
  mongo::BSONObjBuilder builder2;
  mongo::BSONObjBuilder builder3;
  mongo::BSONObjBuilder builder4;
  mongo::BSONObjBuilder builder5;
  Json::Value res;
  Json::Value expected;
  ReserveCouponInfo coupon_info;

  coupon_info.exists = true;
  coupon_info.valid = false;
  coupon_info.valid_any = true;
  internal::UpdateWithCoupon(builder1, coupon_info, "");
  res = utils::helpers::ParseJson(mongo::tojson(builder1.obj()));

  expected["coupon.valid"] = false;
  expected["coupon.valid_any"] = true;
  ASSERT_TRUE(SameJson(res, expected));

  coupon_info.valid = true;
  coupon_info.value = 666;
  internal::UpdateWithCoupon(builder2, coupon_info, "");
  res = utils::helpers::ParseJson(mongo::tojson(builder2.obj()));

  expected.removeMember("coupon.valid");
  expected.removeMember("coupon.valid_any");
  expected["coupon.value"] = 666;
  expected["coupon.was_used"] = true;
  ASSERT_TRUE(SameJson(res, expected));

  coupon_info.percent = 66;
  internal::UpdateWithCoupon(builder3, coupon_info, "");
  res = utils::helpers::ParseJson(mongo::tojson(builder3.obj()));

  expected["coupon.percent"] = 66;
  ASSERT_TRUE(SameJson(res, expected));

  coupon_info.limit = 999;
  internal::UpdateWithCoupon(builder4, coupon_info, "");
  res = utils::helpers::ParseJson(mongo::tojson(builder4.obj()));

  expected["coupon.limit"] = 999;
  ASSERT_TRUE(SameJson(res, expected));

  coupon_info.series = "coupon";
  internal::UpdateWithCoupon(builder5, coupon_info, "");
  res = utils::helpers::ParseJson(mongo::tojson(builder5.obj()));

  expected["coupon.series"] = "coupon";
  ASSERT_TRUE(SameJson(res, expected));
}

TEST(CheckCommitStates, UpdateWithCard) {
  using namespace orderkit;

  card_operations::CardEx card;
  card.billing_card_id = "billing_id";
  card.card_id = "card_id";
  card.number = "card_number";
  card.system = "card_system";
  card.possible_moneyless = true;
  card.valid = false;
  card.persistent_id = "persistent_id";
  card.family = models::orders::FamilyCardInfo{};
  card.family->is_owner = false;

  mongo::BSONObjBuilder builder;
  internal::UpdateWithCard(builder, card, "");
  Json::Value res = utils::helpers::ParseJson(mongo::tojson(builder.obj()));

  Json::Value expected;
  expected["payment_tech.main_card_billing_id"] = "billing_id";
  expected["payment_tech.main_card_payment_id"] = "card_id";
  expected["payment_tech.main_card_persistent_id"] = "persistent_id";
  expected["payment_tech.main_card_possible_moneyless"] = true;
  expected["creditcard.credentials.card_number"] = "card_number";
  expected["creditcard.credentials.card_system"] = "card_system";
  expected["payment_tech.family"] = Json::objectValue;
  expected["payment_tech.family"]["is_owner"] = false;
  ASSERT_TRUE(SameJson(res, expected));
}

TEST(CheckCommitStates, UpdateWithCalc) {
  using namespace orderkit;

  mongo::BSONObjBuilder builder;
  mongo::BSONObjBuilder builder1;
  mongo::BSONObjBuilder builder2;
  mongo::BSONObjBuilder builder3;
  Json::Value res;
  Json::Value expected;
  CalcInfo calc_info;

  calc_info.dist = 666;
  calc_info.time = 999;
  calc_info.recalculated = true;
  internal::UpdateWithCalc(builder, calc_info, "");
  res = utils::helpers::ParseJson(mongo::tojson(builder.obj()));

  expected["route.distance"] = 666;
  expected["route.time"] = 999;
  expected["calc.distance"] = 666;
  expected["calc.time"] = 999;
  expected["calc.recalculated"] = true;
  expected["calc.allowed_tariffs.__park__"] = Json::objectValue;
  ASSERT_TRUE(SameJson(res, expected));

  calc_info.price_info.emplace(
      std::pair<models::ClassType, orderkit::PriceInfo>(
          models::Classes::Minivan,
          {666.66, models::SurgeParams(333.33), 666.66, boost::none,
           boost::none, boost::none, true, false, "application", "category_id",
           boost::none, boost::none, boost::none}));
  internal::UpdateWithCalc(builder1, calc_info, "");
  res = utils::helpers::ParseJson(mongo::tojson(builder1.obj()));

  expected["calc.allowed_tariffs.__park__"]["minivan"] = 2;
  ASSERT_TRUE(SameJson(res, expected));

  discmod::Discount discount;
  discount.value = 333;
  discount.price = 666;
  discount.reason = discmod::DiscountReason::kAnalytics;
  discount.method = discmod::DiscountMethod::kFullDriverLess;
  discount.driver_less_coeff = 0.5;

  calc_info.discount = discount;

  internal::UpdateWithCalc(builder2, calc_info, "");
  res = utils::helpers::ParseJson(mongo::tojson(builder2.obj()));

  Json::Value discount_val;
  discount_val["by_classes"] = Json::arrayValue;
  discount_val["cashbacks"] = Json::arrayValue;
  discount_val["limited_rides"] = false;
  discount_val["driver_less_coeff"] = 0.5;
  discount_val["method"] = "full-driver-less";
  discount_val["price"] = 666;
  discount_val["reason"] = "analytics";
  discount_val["value"] = 333;
  discount_val["with_restriction_by_usages"] = false;
  expected["discount"] = discount_val;
  ASSERT_TRUE(SameJson(res, expected));

  generated::discounts::api::CalculatedDiscount d;
  d.SetValue(666.66);
  d.SetPrice(333.33);
  d.SetMethod(discmod::DiscountMethod::kSubventionFix);
  d.SetReason(discmod::DiscountReason::kForAll);
  d.SetIsCashback(false);
  d.SetLimitedRides(false);
  d.SetIsPriceStrikethrough(false);

  discount.by_classes.emplace(std::make_pair(models::Classes::Minivan, d));
  calc_info.discount = discount;
  internal::UpdateWithCalc(builder3, calc_info, "");
  res = utils::helpers::ParseJson(mongo::tojson(builder3.obj()));

  Json::Value by_classes(Json::arrayValue);
  Json::Value item;
  item["class"] = "minivan";
  item["is_cashback"] = false;
  item["price"] = 333.33;
  item["value"] = 666.66;
  item["method"] = "subvention-fix";
  item["reason"] = "for_all";
  item["limited_rides"] = false;
  item["is_price_strikethrough"] = false;
  by_classes.append(item);
  discount_val["by_classes"] = by_classes;
  expected["discount"] = discount_val;
  ASSERT_TRUE(SameJson(res, expected));
}

TEST(CheckCommitStates, UpdateWithFixedPrice) {
  using namespace orderkit;

  for (const auto& with_max_distance_from_b : {false, true}) {
    FixedPriceInfo fixed_price;
    fixed_price.price = 666;
    fixed_price.destination = {13, 13};
    fixed_price.show_price_in_taximeter = true;
    if (with_max_distance_from_b) fixed_price.max_distance_from_b = 999;

    mongo::BSONObjBuilder builder;
    internal::UpdateWithFixedPrice(builder, fixed_price, "");
    Json::Value res = utils::helpers::ParseJson(mongo::tojson(builder.obj()));

    Json::Value expected;
    expected["fixed_price.price"] = 666;
    expected["fixed_price.price_original"] = 666;
    expected["fixed_price.show_price_in_taximeter"] = true;
    if (with_max_distance_from_b)
      expected["fixed_price.max_distance_from_b"] = 999;

    Json::Value destination(Json::arrayValue);
    destination.append(13);
    destination.append(13);
    expected["fixed_price.destination"] = destination;

    ASSERT_TRUE(SameJson(res, expected));
  }
}

TEST(CheckCommitStates, UpdateWithCorp) {
  using namespace orderkit;

  mongo::BSONObjBuilder builder;
  mongo::BSONObjBuilder builder1;
  Json::Value res;
  Json::Value expected;
  models::corp::CorpInfo corp_info;

  corp_info.user_id = "some_userid";
  corp_info.client_comment = "some user comment";
  corp_info.client_id = "some_client_id";

  internal::UpdateWithCorp(builder, corp_info, "");
  res = utils::helpers::ParseJson(mongo::tojson(builder.obj()));

  expected["request.corp.user_id"] = "some_userid";
  expected["request.corp.client_comment"] = "some user comment";
  expected["request.corp.client_id"] = "some_client_id";
  expected["payment_tech.main_card_billing_id"] = "some_client_id";
  ASSERT_TRUE(SameJson(res, expected));

  corp_info.cost_center = "whatever should be here";
  internal::UpdateWithCorp(builder1, corp_info, "");
  res = utils::helpers::ParseJson(mongo::tojson(builder1.obj()));

  expected["request.corp.cost_center"] = "whatever should be here";
  ASSERT_TRUE(SameJson(res, expected));
}

TEST(CheckCommitStates, UpdateWithApplepay) {
  using namespace orderkit;

  mongo::BSONObjBuilder builder;
  mongo::BSONObjBuilder builder1;
  mongo::BSONObjBuilder builder2;
  Json::Value res;
  Json::Value expected(Json::objectValue);
  LogExtra log_extra;
  models::orders::Order order;

  order.payment_tech.type = models::payment_types::ApplePay;

  internal::MaybeUpdateWithOneTokenpay(builder, order, log_extra);
  res = utils::helpers::ParseJson(mongo::tojson(builder.obj()));

  ASSERT_TRUE(SameJson(res, expected));

  order.payment_tech.main_card_payment_id = "singleword";

  internal::MaybeUpdateWithOneTokenpay(builder1, order, log_extra);
  res = utils::helpers::ParseJson(mongo::tojson(builder1.obj()));

  expected["payment_tech.main_card_billing_id"] = "singleword";
  ASSERT_TRUE(SameJson(res, expected));

  order.payment_tech.main_card_payment_id = "not_a_single_word";

  internal::MaybeUpdateWithOneTokenpay(builder2, order, log_extra);
  res = utils::helpers::ParseJson(mongo::tojson(builder2.obj()));

  expected["payment_tech.main_card_billing_id"] = "word";
  ASSERT_TRUE(SameJson(res, expected));
}

TEST(CheckCommitStates, UpdateWithSurge) {
  using namespace orderkit;

  mongo::BSONObjBuilder builder1;
  mongo::BSONObjBuilder builder2;
  mongo::BSONObjBuilder builder3;
  mongo::BSONObjBuilder builder4;
  Json::Value res1;
  Json::Value res2;
  Json::Value expected1(Json::objectValue);
  Json::Value expected2(Json::objectValue);
  ForcedSurgeInfo surge;

  surge.price = models::SurgeParams(666.66);

  internal::UpdateWithSurge(builder1, builder2, surge, "");
  res1 = utils::helpers::ParseJson(mongo::tojson(builder1.obj()));
  res2 = utils::helpers::ParseJson(mongo::tojson(builder2.obj()));

  expected1["request.sp"] = 666.66;
  ASSERT_TRUE(SameJson(res1, expected1));
  ASSERT_TRUE(SameJson(res2, expected2));

  surge.price_required = models::SurgeParams(999.99);
  surge.price = boost::none;

  internal::UpdateWithSurge(builder3, builder4, surge, "");
  res1 = utils::helpers::ParseJson(mongo::tojson(builder3.obj()));
  res2 = utils::helpers::ParseJson(mongo::tojson(builder4.obj()));

  expected1["request.sp"] = true;
  expected1["request.sp_alpha"] = true;
  expected1["request.sp_beta"] = true;
  expected1["request.sp_surcharge"] = true;
  expected2["request.spr"] = 999.99;
  ASSERT_TRUE(SameJson(res2, expected1));
  ASSERT_TRUE(SameJson(res1, expected2));
}

TEST(CheckCommitStates, PrepareReservedUpdate) {
  using namespace orderkit;

  models::order_proc::OrderProc order_proc;
  order_proc.order.payment_tech.type = models::payment_types::Undefined;

  config::Config config = GetConfig(100);
  std::set<std::string> experiments_set({"direct_assignment"});
  std::set<std::string> user_experiments_set({"driver_phone_totw_forwarding"});
  ForcedSurgeInfo surge;
  LogExtra log_extra;

  CalcInfo calc_info;
  calc_info.recalculated = true;
  calc_info.time = 660.660;
  calc_info.dist = 6000.6;

  const orderkit::FullAuctionInfo full_auction_info{false, std::nullopt,
                                                    std::nullopt};
  const orderkit::AuctionFeatures auction_features{false, full_auction_info};
  mongo::BSONObj prepared_obj = internal::PrepareReservedUpdate(
      order_proc, config, experiments_set, user_experiments_set, boost::none,
      true, boost::none, calc_info, boost::none, boost::none, boost::none,
      boost::none, boost::none, boost::none, surge, auction_features,
      log_extra);
  Json::Value res = utils::helpers::ParseJson(mongo::tojson(prepared_obj));

  Json::Value expected;
  expected["$set"]["commit_state"] = "reserved";
  expected["$set"]["order._type"] = "urgent";
  expected["$set"]["order.calc.allowed_tariffs.__park__"] = Json::objectValue;
  expected["$set"]["order.calc.recalculated"] = calc_info.recalculated;
  expected["$set"]["order.calc.time"] = expected["$set"]["order.route.time"] =
      calc_info.time;
  expected["$set"]["order.calc.distance"] =
      expected["$set"]["order.route.distance"] = calc_info.dist;
  expected["$set"]["order.experiments"] = Json::arrayValue;
  expected["$set"]["order.experiments"].append("direct_assignment");
  expected["$set"]["order.user_experiments"] = Json::arrayValue;
  expected["$set"]["order.user_experiments"].append(
      "driver_phone_totw_forwarding");
  expected["$set"]["order.need_sync_grades"] = true;
  expected["$set"]["order.no_cars_order"] = false;
  expected["$currentDate"]["updated"] = true;
  ASSERT_TRUE(SameJson(res, expected));
}
