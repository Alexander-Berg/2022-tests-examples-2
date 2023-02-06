#include <gtest/gtest.h>
#include <common/test_config.hpp>
#include <config/config.hpp>
#include <fstream>
#include <models/order.hpp>
#include <mongo/mongo.hpp>
#include <orderkit/calcinfo_processing.hpp>
#include <utils/geometry.hpp>

namespace orderkit {
namespace calcinfo_internal {

struct Deps {
  const config::Config& config;
  const utils::mongo::Collections* const collections;
  const models::requirements::Descriptions& requirements_descriptions;
  const models::tariff_settings_dict& tariff_settings;
};

bool OrderMatchesOffer(const Order& order,
                       const std::vector<utils::geometry::Point>& route,
                       const mongo::BSONObj& offer, bool id_matched,
                       const Deps& deps, const LogExtra& log_extra);

CalcInfo MakeCalcInfo(
    const std::chrono::system_clock::time_point& offer_valid_from,
    const mongo::BSONObj& offer, const LogExtra& log_extra);

CalcInfo ChooseCalcInfo(const Order& order, CalcInfo&& new_calc_info,
                        boost::optional<CalcInfo>&& old_calc_info,
                        const bool update_caused_by_decoupling,
                        const bool multiclass_with_failed_decoupling_enabled,
                        const LogExtra& log_extra);

}  // namespace calcinfo_internal
}  // namespace orderkit

static std::string Load(const std::string& filename) {
  std::ifstream stream(std::string(SOURCE_DIR) + "/tests/static/" + filename);
  assert(stream);
  std::string str((std::istreambuf_iterator<char>(stream)),
                  std::istreambuf_iterator<char>());
  return str;
}

TEST(calc_info, order_matches_offer) {
  using namespace orderkit;
  using namespace orderkit::calcinfo_internal;
  Order order;
  models::tariff_settings_dict tariff_settings;
  tariff_settings["moscow"] = {};
  order.request.due = std::chrono::system_clock::from_time_t(200);
  order.request.classes.Add("econom");
  std::vector<models::requirements::PrimeValue> reqs = {int64_t(3), int64_t(7)};
  order.request.requirements.emplace("childchair_moscow", reqs);
  order.request.requirements.emplace("applepay", true);
  order.request.requirements.emplace("yellowcarnumber", true);
  order.nearest_zone = "moscow";

  std::vector<utils::geometry::Point> route = {utils::geometry::Point(35, 57),
                                               utils::geometry::Point(36, 58)};

  std::string offer_docs = Load("order_matches_offer_offers.json");
  auto offers = mongo::fromjson(offer_docs);
  ASSERT_FALSE(offers.isEmpty());

  config::Config config(config::DocsMapForTest());

  for (const auto& offer : offers["data"].Array()) {
    bool expected = utils::mongo::ToBool(offer["expected"]);
    auto data = utils::mongo::ToDocument(offer["offer"]);
    std::cout << "***** TEST " << utils::mongo::ToString(data["_id"]) << " ****"
              << std::endl;
    Deps deps{config, nullptr, {}, tariff_settings};
    LogExtra log_extra;
    ASSERT_EQ(expected,
              OrderMatchesOffer(order, route, data, false, deps, log_extra));
  }
}

TEST(calc_info, order_matches_offer_paid_supply) {
  using namespace orderkit;
  using namespace orderkit::calcinfo_internal;
  Order order;
  models::tariff_settings_dict tariff_settings;
  tariff_settings["moscow"] = {};
  order.request.due = std::chrono::system_clock::from_time_t(200);
  order.request.classes.Add("econom");
  std::vector<models::requirements::PrimeValue> reqs = {int64_t(3), int64_t(7)};
  order.request.requirements.emplace("childchair_moscow", reqs);
  order.request.requirements.emplace("applepay", true);
  order.request.requirements.emplace("yellowcarnumber", true);
  order.nearest_zone = "moscow";

  std::vector<utils::geometry::Point> route = {utils::geometry::Point(35, 57),
                                               utils::geometry::Point(36, 58)};

  std::string offer_docs = Load("order_matches_offer_offers_paid_supply.json");
  auto offers = mongo::fromjson(offer_docs);
  ASSERT_FALSE(offers.isEmpty());

  config::Config config(config::DocsMapForTest());

  for (const auto& offer : offers["data"].Array()) {
    bool expected = utils::mongo::ToBool(offer["expected"]);
    auto data = utils::mongo::ToDocument(offer["offer"]);
    std::cout << "***** TEST " << utils::mongo::ToString(data["_id"]) << " ****"
              << std::endl;
    Deps deps{config, nullptr, {}, tariff_settings};
    LogExtra log_extra;
    ASSERT_EQ(expected,
              OrderMatchesOffer(order, route, data, true, deps, log_extra));
  }
}

TEST(calc_info, make_calc_info) {
  using namespace orderkit;
  using namespace orderkit::calcinfo_internal;
  const auto& offer_doc = Load("make_calc_info_offer.json");
  const auto& offer = mongo::fromjson(offer_doc);
  LogExtra log_extra;

  auto result = MakeCalcInfo(std::chrono::system_clock::from_time_t(100500),
                             offer, log_extra);
  ASSERT_FALSE(result.is_obsolete);
  ASSERT_EQ("offer_id", result.offer);
  ASSERT_EQ(1u, result.price_info.size());
  ASSERT_EQ(174., result.price_info[models::Classes::Econom].price);
  ASSERT_EQ(2.9, result.price_info[models::Classes::Econom].surge_params.surge);
  ASSERT_TRUE(result.price_info[models::Classes::Econom].is_fixed_price);
  ASSERT_TRUE(result.authorized);
  ASSERT_FALSE(result.destination_is_airport);
  ASSERT_TRUE(result.discount.is_initialized());
  ASSERT_EQ(discmod::DiscountMethod::kFullDriverLess, result.discount->method);
  ASSERT_EQ(discmod::DiscountReason::kForAll, result.discount->reason);
  ASSERT_EQ(1u, result.discount->by_classes.size());
  ASSERT_EQ(0.35,
            result.discount->by_classes.at(models::Classes::Econom).GetValue());
  ASSERT_EQ(408.,
            result.discount->by_classes[models::Classes::Econom].GetPrice());
  ASSERT_FALSE(result.recalculated);
  ASSERT_NEAR(2476.4198089683955, result.dist, 0.001);
  ASSERT_NEAR(386.91588771341986, result.time, 0.001);

  result = MakeCalcInfo(std::chrono::system_clock::from_time_t(7500000), offer,
                        log_extra);
  ASSERT_TRUE(result.is_obsolete);
}

const orderkit::CalcInfo kDefultCalcInfo = [] {
  orderkit::CalcInfo c;
  c.time = 100;
  c.dist = 200;
  c.recalculated = false;
  c.price_info = {{models::Classes::Econom,
                   orderkit::PriceInfo{
                       199, models::SurgeParams(), 199, boost::none,
                       boost::none, boost::none, true, false, "application",
                       "category_id", boost::none, boost::none, boost::none}}};
  c.offer = "old";
  return c;
}();

struct ChooseCalcInfoParams {
  orderkit::CalcInfo new_;
  boost::optional<orderkit::CalcInfo> old;
  bool expect_new;
};
class TestChooseCalcInfo
    : public ::testing::TestWithParam<ChooseCalcInfoParams> {};

namespace orderkit {
// this is only for TEST
bool operator==(const orderkit::CalcInfo& a, const orderkit::CalcInfo& b) {
  return a.offer == b.offer;
}
bool operator!=(const orderkit::CalcInfo& a, const orderkit::CalcInfo& b) {
  return !(a == b);
}

}  // namespace orderkit

TEST_P(TestChooseCalcInfo, choose_calc_info) {
  orderkit::Order order;
  order.request.classes = {models::Classes::Econom};
  LogExtra log_extra;

  auto new_ = GetParam().new_;
  auto old = GetParam().old;
  auto result = orderkit::calcinfo_internal::ChooseCalcInfo(
      order, std::move(new_), std::move(old), false, false, log_extra);

  if (GetParam().expect_new) {
    ASSERT_EQ(GetParam().new_, result);
    ASSERT_NE(GetParam().old, boost::make_optional(result));
  } else {
    ASSERT_EQ(GetParam().old, boost::make_optional(result));
    ASSERT_NE(GetParam().new_, result);
  }
}

INSTANTIATE_TEST_CASE_P(
    P1, TestChooseCalcInfo,
    ::testing::Values(ChooseCalcInfoParams{kDefultCalcInfo, boost::none, true},
                      ChooseCalcInfoParams{
                          [] {
                            auto c = kDefultCalcInfo;
                            c.offer = "new";
                            c.price_info = {
                                {models::Classes::Business,
                                 orderkit::PriceInfo{
                                     199, models::SurgeParams(), 199,
                                     boost::none, boost::none, boost::none,
                                     true, false, "application", "category_id",
                                     boost::none, boost::none, boost::none}}};
                            return c;
                          }(),
                          kDefultCalcInfo, true},
                      ChooseCalcInfoParams{
                          [] {
                            auto c = kDefultCalcInfo;
                            c.offer = "new";
                            c.price_info = {
                                {models::Classes::Econom,
                                 orderkit::PriceInfo{
                                     199, models::SurgeParams(2.0), 199,
                                     boost::none, boost::none, boost::none,
                                     true, false, "application", "category_id",
                                     boost::none, boost::none, boost::none}}};
                            return c;
                          }(),
                          kDefultCalcInfo, true},
                      ChooseCalcInfoParams{[] {
                                             auto c = kDefultCalcInfo;
                                             c.offer = "new";
                                             return c;
                                           }(),
                                           kDefultCalcInfo, false}), );
