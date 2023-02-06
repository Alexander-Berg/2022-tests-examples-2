#include <set>

#include <gtest/gtest.h>

#include <clients/router_exceptions.hpp>
#include <clients/router_fallback.hpp>
#include <common/mock_handlers_context.hpp>
#include <common/test_config.hpp>
#include <orderkit/forcedsurge.hpp>
#include <utils/known_apps.hpp>

namespace {

const config::Config GetConfig() {
  config::DocsMap docs_map = config::DocsMapForTest();
  docs_map.Override<int>("URGENT_URGENCY", 18 * 60);
  return config::Config(docs_map);
}

orderkit::CalcInfo GetCalcInfo(
    const std::string& offer,
    const models::ClassType tariff_class = models::Classes::Econom,
    double price = 199, double surge = 2.5) {
  orderkit::CalcInfo calcinfo;
  calcinfo.offer = offer;
  calcinfo.price_info[tariff_class] = {
      price,         models::SurgeParams(surge),
      price,         boost::none,
      boost::none,   boost::none,
      true,          false,
      "application", "category_id",
      boost::none,   boost::none,
      boost::none};
  return calcinfo;
}

models::orders::Order GetOrder() {
  models::orders::Order order;
  order.request.classes = {"econom"};
  order.request.source.geopoint = {37.612840, 55.762478};
  order.request.destinations.push_back({});
  order.request.destinations[0].geopoint = {37.610093, 55.843501};
  order.request.payment.type = models::payment_types::Card;
  return order;
}

class TestGetOfferSurge
    : public ::testing::TestWithParam<std::tuple<
          orderkit::CalcInfo, std::string, boost::optional<double>>> {};

TEST_P(TestGetOfferSurge, Basic) {
  const orderkit::CalcInfo& calc_info = std::get<0>(GetParam());
  const std::string& tariff_class_name = std::get<1>(GetParam());
  const boost::optional<double>& expected_result = std::get<2>(GetParam());

  boost::optional<models::SurgeParams> result =
      orderkit::forcedsurge_internal::GetOfferSurge(
          calc_info, models::ClassesMapper::Parse(tariff_class_name));
  if (expected_result) {
    ASSERT_TRUE(bool(result));

    // FIXME: check surcharge here
    EXPECT_NEAR(result->surge, *expected_result, 1e-6);
  } else {
    ASSERT_FALSE(bool(result));
  }
}

INSTANTIATE_TEST_CASE_P(
    TestGetOfferSurgeValues, TestGetOfferSurge,
    ::testing::Values(
        std::make_tuple(GetCalcInfo("offer"), "business", boost::none),
        std::make_tuple(GetCalcInfo("offer"), "econom",
                        boost::optional<double>(2.5)),
        std::make_tuple(GetCalcInfo("offer", models::Classes::Business, 250, 1),
                        "business", boost::optional<double>(1.0))), );

class TestCheckForcedSurge
    : public ::testing::TestWithParam<
          std::tuple<models::orders::Order, orderkit::CalcInfo,
                     boost::optional<orderkit::ForcedSurgeInfo>>>,
      public MockHeadersContext {};

TEST_P(TestCheckForcedSurge, Basic) {
  const auto& order = std::get<0>(GetParam());
  const auto& calc_info = std::get<1>(GetParam());
  const auto& expected_result = std::get<2>(GetParam());
  const auto& config = GetConfig();

  clients::routing::RouterFallback router;

  if (expected_result) {
    const auto& result = orderkit::CheckForcedSurgeForClass(
        order.request.classes.GetFirstActive(), order, config, calc_info,
        GetContext().log_extra);

    if (expected_result->price) {
      ASSERT_TRUE(!!(result.price));
      EXPECT_NEAR(result.price->surge, expected_result->price->surge, 1e-6);
    } else {
      ASSERT_FALSE(result.price);
    }

    if (expected_result->price_required) {
      ASSERT_TRUE(!!(result.price_required));
      EXPECT_NEAR(result.price_required->surge,
                  expected_result->price_required->surge, 1e-6);
    } else {
      ASSERT_FALSE(result.price_required);
    }
  } else {
    ASSERT_THROW(orderkit::CheckForcedSurgeForClass(
                     order.request.classes.GetFirstActive(), order, config,
                     calc_info, GetContext().log_extra),
                 orderkit::ForcedSurgeChangedError);
  }
}

// FIXME: use surge params here
boost::optional<orderkit::ForcedSurgeInfo> MakeForcedSurgeInfo(
    const boost::optional<double> price,
    const boost::optional<double> required) {
  boost::optional<models::SurgeParams> price_params;
  if (price) price_params = models::SurgeParams(*price, boost::none);
  boost::optional<models::SurgeParams> required_params;
  if (required) required_params = models::SurgeParams(*required, boost::none);
  return orderkit::ForcedSurgeInfo{price_params, required_params};
}

models::orders::Order GetOrderOldSoon() {
  models::orders::Order order = GetOrder();
  order.type = models::orders::types::Soon;
  order.request.offer_id = "offer";
  return order;
}

models::orders::Order GetOrderOldUrgent() {
  models::orders::Order order = GetOrder();
  order.type = models::orders::types::Urgent;
  order.request.due = utils::datetime::Now();
  order.request.offer_id = "offer";
  return order;
}

models::orders::Order GetOrderOldExactUrgent() {
  models::orders::Order order = GetOrder();
  order.type = models::orders::types::ExactUrgent;
  order.request.due = utils::datetime::Now() + std::chrono::hours(2);
  order.request.offer_id = "offer";
  return order;
}

models::orders::Order GetOrderNewSoon1() {
  models::orders::Order order = GetOrder();
  order.type = models::orders::types::Soon;
  order.request.offer_id = "offer";
  order.request.surge_price = models::SurgeParams();
  return order;
}

models::orders::Order GetOrderNewSoon2() {
  models::orders::Order order = GetOrder();
  order.type = models::orders::types::Soon;
  order.request.offer_id = "offer";
  order.request.surge_price = models::SurgeParams(2.5);
  return order;
}

models::orders::Order GetOrderNewUrgent1() {
  models::orders::Order order = GetOrderOldUrgent();
  order.request.surge_price = models::SurgeParams();
  return order;
}

models::orders::Order GetOrderNewUrgent2() {
  models::orders::Order order = GetOrderOldUrgent();
  order.request.surge_price = models::SurgeParams(2.5);
  return order;
}

models::orders::Order GetOrderNewExcatUrgent1() {
  models::orders::Order order = GetOrderOldExactUrgent();
  order.request.surge_price = models::SurgeParams();
  return order;
}

models::orders::Order GetOrderNewExcatUrgent2() {
  models::orders::Order order = GetOrderOldExactUrgent();
  order.request.surge_price = models::SurgeParams(2.5);
  return order;
}

models::orders::Order GetOrderCorp() {
  models::orders::Order order = GetOrder();
  order.statistics.application = models::applications::CorpWeb;
  return order;
}

INSTANTIATE_TEST_CASE_P(
    TestCheckForcedSurgeValues, TestCheckForcedSurge,
    ::testing::Values(
        // old soon
        std::make_tuple(GetOrderOldSoon(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 1.0),
                        MakeForcedSurgeInfo(1.0, boost::none)),
        std::make_tuple(GetOrderOldSoon(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 2.5),
                        MakeForcedSurgeInfo(2.5, boost::none)),
        // old urgent
        std::make_tuple(GetOrderOldUrgent(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 1.0),
                        MakeForcedSurgeInfo(1.0, boost::none)),
        std::make_tuple(GetOrderOldUrgent(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 2.5),
                        MakeForcedSurgeInfo(2.5, boost::none)),
        // old exacturgent
        std::make_tuple(GetOrderOldExactUrgent(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 1.0),
                        MakeForcedSurgeInfo(1.0, boost::none)),
        std::make_tuple(GetOrderOldExactUrgent(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 2.5),
                        MakeForcedSurgeInfo(2.5, boost::none)),
        // new soon 1
        std::make_tuple(GetOrderNewSoon1(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 1.0),
                        MakeForcedSurgeInfo(1.0, boost::none)),
        std::make_tuple(GetOrderNewSoon1(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 2.5),
                        MakeForcedSurgeInfo(2.5, boost::none)),
        // new soon 2
        std::make_tuple(GetOrderNewSoon2(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 1.0),
                        MakeForcedSurgeInfo(1.0, boost::none)),
        std::make_tuple(GetOrderNewSoon2(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 2.5),
                        MakeForcedSurgeInfo(2.5, boost::none)),
        // new urgent 1
        std::make_tuple(GetOrderNewUrgent1(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 1.0),
                        MakeForcedSurgeInfo(1.0, boost::none)),
        std::make_tuple(GetOrderNewUrgent1(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 2.5),
                        MakeForcedSurgeInfo(2.5, boost::none)),
        // new urgent 2
        std::make_tuple(GetOrderNewUrgent2(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 1.0),
                        MakeForcedSurgeInfo(1.0, boost::none)),
        std::make_tuple(GetOrderNewUrgent2(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 2.5),
                        MakeForcedSurgeInfo(2.5, boost::none)),
        // new exact urgent 1
        std::make_tuple(GetOrderNewExcatUrgent1(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 1.0),
                        MakeForcedSurgeInfo(1.0, boost::none)),
        std::make_tuple(GetOrderNewExcatUrgent1(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 2.5),
                        MakeForcedSurgeInfo(2.5, boost::none)),
        // new exact urgent 2
        std::make_tuple(GetOrderNewExcatUrgent2(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 1.0),
                        MakeForcedSurgeInfo(1.0, boost::none)),
        std::make_tuple(GetOrderNewExcatUrgent2(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 2.5),
                        MakeForcedSurgeInfo(2.5, boost::none)),
        // corp
        std::make_tuple(GetOrderCorp(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 1.0),
                        MakeForcedSurgeInfo(1.0, boost::none)),
        std::make_tuple(GetOrderCorp(),
                        GetCalcInfo("offer", models::Classes::Econom, 199, 2.5),
                        MakeForcedSurgeInfo(2.5, boost::none))), );

}  // namespace
