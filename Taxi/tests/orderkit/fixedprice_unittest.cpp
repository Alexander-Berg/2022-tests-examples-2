#include <gtest/gtest.h>

#include <memory>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <orderkit/exceptions.hpp>
#include <orderkit/fixedprice.hpp>
#include <utils/known_apps.hpp>

namespace {

using ConfigPtr = std::shared_ptr<const config::Config>;

ConfigPtr GetConfig(bool enabled = false, double distance = 0.0) {
  config::DocsMap docs_map = config::DocsMapForTest();
  docs_map.Override("FIXED_PRICE_MAX_ALLOWED_DISTANCE_ENABLED", enabled);
  docs_map.Override("FIXED_PRICE_MAX_ALLOWED_DISTANCE", distance);
  docs_map.Override<size_t>("FIXED_PRICE_MAX_DISTANCE_FROM_B", 500);
  docs_map.Override<size_t>("FIXED_PRICE_ADDITIONAL_DISTANCE_FOR_AIRPORT",
                            1000);
  docs_map.Override<int>("URGENT_URGENCY", 18 * 60);
  return std::make_shared<config::Config>(docs_map);
}

models::orders::Order GetOrder(const std::string& offer = "foo") {
  models::orders::Order order;
  order.request.offer_id = offer;
  order.request.classes = {"econom"};
  order.request.due = utils::datetime::Now();
  order.request.source.geopoint = {37.612840, 55.762478};
  order.request.destinations.push_back({});
  order.request.destinations[0].geopoint = {37.610093, 55.843501};
  return order;
}

models::orders::Order GetOrderFarAway(const std::string& offer = "foo") {
  models::orders::Order order = GetOrder(offer);
  order.request.destinations[0].geopoint = {38.038560, 56.156131};
  return order;
}

models::orders::Order GetCorpOrder(const std::string& offer = "foo") {
  models::orders::Order order = GetOrder(offer);
  order.statistics.application = models::applications::CorpWeb;
  return order;
}

models::orders::Order GetOrderMultipleClasses(
    const std::string& offer = "foo") {
  models::orders::Order order = GetOrder(offer);
  order.request.classes = {"econom", "business", "vip"};
  return order;
}

orderkit::CalcInfo GetCalcInfoMultipleClasses(const std::string& offer = "foo",
                                              bool is_fixed_price = true) {
  orderkit::CalcInfo calc_info;
  calc_info.offer = offer;

  ::generated::pricing_data_preparer::api::CategoryInfo category_info;
  category_info.SetFixedPrice(is_fixed_price);
  ::generated::pricing_data_preparer::api::BackendVariables data;
  data["category_data"]["fixed_price"] = is_fixed_price;
  ::generated::pricing_data_preparer::api::UserCategoryData user;
  user.SetData(data);
  category_info.SetUser(user);
  ::generated::pricing_data_preparer::api::TaximeterMetadata meta;
  meta.SetMaxDistanceFromPointB(500);
  meta.SetShowPriceInTaximeter(true);
  category_info.SetTaximeterMetadata(meta);

  calc_info.price_info = {
      {models::Classes::Econom,
       {199, models::SurgeParams(), 199, boost::none, boost::none, boost::none,
        is_fixed_price, false, "application", "category_id",
        models::pricing::PricingData{category_info}, true, boost::none}},
      {models::Classes::Business,
       {299, models::SurgeParams(), 299, boost::none, boost::none, boost::none,
        is_fixed_price, false, "application", "category_id",
        models::pricing::PricingData{category_info}, true, boost::none}},
      {models::Classes::Vip,
       {499, models::SurgeParams(), 499, boost::none, boost::none, boost::none,
        is_fixed_price, false, "application", "category_id",
        models::pricing::PricingData{category_info}, true, boost::none}},
  };
  calc_info.is_obsolete = false;
  return calc_info;
}

orderkit::CalcInfo GetCalcInfo(int32_t max_distance_b = 500,
                               bool show_price = true,
                               const std::string& offer = "foo",
                               bool fixed_price = true) {
  orderkit::CalcInfo calc_info;
  calc_info.offer = offer;
  ::generated::pricing_data_preparer::api::CategoryInfo category_info;
  category_info.SetFixedPrice(fixed_price);
  ::generated::pricing_data_preparer::api::BackendVariables data;
  data["category_data"]["fixed_price"] = fixed_price;
  ::generated::pricing_data_preparer::api::UserCategoryData user;
  user.SetData(data);
  category_info.SetUser(user);
  ::generated::pricing_data_preparer::api::TaximeterMetadata meta;
  meta.SetMaxDistanceFromPointB(max_distance_b);
  meta.SetShowPriceInTaximeter(show_price);
  category_info.SetTaximeterMetadata(meta);
  calc_info.price_info = {
      {models::Classes::Econom,
       {199, models::SurgeParams(), 199, boost::none, boost::none, boost::none,
        true, false, "application", "category_id",
        models::pricing::PricingData{category_info}, true, boost::none}}};
  calc_info.is_obsolete = false;
  return calc_info;
}

orderkit::CalcInfo GetCalcInfoAirport(const std::string& offer = "foo") {
  orderkit::CalcInfo calc_info = GetCalcInfo(1500, true, offer);
  calc_info.destination_is_airport = true;
  return calc_info;
}

orderkit::CalcInfo GetCalcInfoNoFixedPrice(const std::string& offer = "foo") {
  orderkit::CalcInfo calc_info = GetCalcInfo(500, true, offer);
  calc_info.price_info[models::Classes::Econom].is_fixed_price = false;
  return calc_info;
}

orderkit::CalcInfo GetCalcInfoBusiness(const std::string& offer = "foo") {
  orderkit::CalcInfo calc_info = GetCalcInfo(500, true, offer);
  ::generated::pricing_data_preparer::api::CategoryInfo category_info;
  category_info.SetFixedPrice(true);
  ::generated::pricing_data_preparer::api::BackendVariables data;
  data["category_data"]["fixed_price"] = true;
  ::generated::pricing_data_preparer::api::UserCategoryData user;
  user.SetData(data);
  category_info.SetUser(user);
  ::generated::pricing_data_preparer::api::TaximeterMetadata meta;
  meta.SetMaxDistanceFromPointB(500);
  meta.SetShowPriceInTaximeter(true);
  category_info.SetTaximeterMetadata(meta);

  calc_info.price_info = {
      {models::Classes::Business,
       {199, models::SurgeParams(), 199, boost::none, boost::none, boost::none,
        true, false, "application", "category_id",
        models::pricing::PricingData{category_info}, true, boost::none}}};
  return calc_info;
}

auto GetEconomFixedPrice(uint64_t max_distance_from_b = 500,
                         bool show_price_in_taximeter = true) {
  return boost::optional<orderkit::FixedPriceInfo>({199.0,
                                                    199.0,
                                                    boost::none,
                                                    boost::none,
                                                    {37.610093, 55.843501},
                                                    max_distance_from_b,
                                                    show_price_in_taximeter});
}

class GetFixedPriceTestBasic
    : public ::testing::TestWithParam<
          std::tuple<ConfigPtr, models::orders::Order, orderkit::CalcInfo,
                     boost::optional<orderkit::FixedPriceInfo>>> {};

class GetFixedPriceTestPriceChanged
    : public ::testing::TestWithParam<
          std::tuple<ConfigPtr, models::orders::Order, orderkit::CalcInfo>> {};

TEST_P(GetFixedPriceTestBasic, Basic) {
  LogExtra log_extra;

  const config::Config& config = *std::get<0>(GetParam());
  const models::orders::Order& order = std::get<1>(GetParam());
  const orderkit::CalcInfo& calc_info = std::get<2>(GetParam());
  const boost::optional<orderkit::FixedPriceInfo>& expected_result =
      std::get<3>(GetParam());

  const auto& result_infos =
      orderkit::GetFixedPriceInfos(config, order, calc_info, false, log_extra);

  if (expected_result) {
    ASSERT_TRUE(bool(result_infos));
    const auto& result =
        result_infos->at(order.request.classes.GetFirstActive());
    EXPECT_NEAR(result.price, expected_result->price, 1e-6);
    EXPECT_NEAR(result.destination.lat, expected_result->destination.lat, 1e-6);
    EXPECT_NEAR(result.destination.lon, expected_result->destination.lon, 1e-6);
    EXPECT_EQ(result.max_distance_from_b, expected_result->max_distance_from_b);
    EXPECT_EQ(result.show_price_in_taximeter,
              expected_result->show_price_in_taximeter);
  } else {
    ASSERT_FALSE(bool(result_infos));
  }
}

TEST_P(GetFixedPriceTestPriceChanged, Basic) {
  LogExtra log_extra;
  boost::optional<orderkit::FixedPriceInfo> result;

  const config::Config& config = *std::get<0>(GetParam());
  const models::orders::Order& order = std::get<1>(GetParam());
  const orderkit::CalcInfo& calc_info = std::get<2>(GetParam());

  EXPECT_THROW(
      orderkit::GetFixedPriceInfos(config, order, calc_info, false, log_extra),
      orderkit::PriceChangedError);
}

INSTANTIATE_TEST_CASE_P(
    GetFixedPriceTestBasicValues, GetFixedPriceTestBasic,
    ::testing::Values(
        // regular
        std::make_tuple(GetConfig(true, 10000), GetOrder(), GetCalcInfo(),
                        GetEconomFixedPrice()),
        // regular with hide price
        std::make_tuple(GetConfig(true, 10000), GetOrder(), GetCalcInfo(),
                        GetEconomFixedPrice(500, true)),
        // regular with unset show price tariff option
        std::make_tuple(GetConfig(true, 10000), GetOrder(), GetCalcInfo(),
                        GetEconomFixedPrice(500, true)),
        // order to airport
        std::make_tuple(GetConfig(true, 10000), GetOrder(),
                        GetCalcInfoAirport(), GetEconomFixedPrice(1500)),
        // no fixed price flag set
        std::make_tuple(GetConfig(true, 10000), GetOrder(),
                        GetCalcInfoNoFixedPrice(), boost::none),
        // No offer id, order.request.offer empty
        std::make_tuple(GetConfig(true, 10000), GetOrder(""),
                        GetCalcInfo(500, true, ""), GetEconomFixedPrice()),
        // Distance is more than max allowed in config
        std::make_tuple(GetConfig(true, 10000), GetOrderFarAway(),
                        GetCalcInfo(500, true, "", false), boost::none),
        // No fixed price enabled
        std::make_tuple(GetConfig(false, 10000), GetOrder(),
                        GetCalcInfo(500, true, "", false), boost::none),
        // multiple classes given
        std::make_tuple(GetConfig(true, 10000), GetOrderMultipleClasses(),
                        GetCalcInfoMultipleClasses(), GetEconomFixedPrice()),
        // Corp order
        std::make_tuple(GetConfig(true, 10000), GetCorpOrder(), GetCalcInfo(),
                        GetEconomFixedPrice())), );

INSTANTIATE_TEST_CASE_P(GetFixedPriceTestPriceChangedValues,
                        GetFixedPriceTestPriceChanged,
                        ::testing::Values(
                            // calc_info without offer set
                            std::make_tuple(GetConfig(true, 10000), GetOrder(),
                                            GetCalcInfo(500, true, "")),
                            // no price for class
                            std::make_tuple(GetConfig(true, 10000), GetOrder(),
                                            GetCalcInfoBusiness())), );
}  // namespace
