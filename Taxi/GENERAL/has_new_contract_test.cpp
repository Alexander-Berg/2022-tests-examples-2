#include <filters/logistic/has_new_contract/has_new_contract.hpp>

#include <userver/utest/utest.hpp>

#include <taxi_config/variables/CANDIDATES_SHIFT_SETTINGS.hpp>

#include <filters/infrastructure/fetch_final_classes/fetch_final_classes.hpp>
#include <filters/infrastructure/fetch_park_activation/fetch_park_activation.hpp>

#include "configs/logistic_classes.hpp"

using candidates::GeoMember;
using namespace candidates::filters;
using namespace candidates::filters::infrastructure;
using namespace candidates::filters::logistic;

namespace {

const candidates::filters::FilterInfo kEmptyInfo;

const std::string kSettingsConfig = R"(
{
  "logistic_cargo": {
    "client": "cargo_client_b2b_logistics_payment",
    "partner": "cargo_park_b2b_logistics_payment"
  },
  "logistic_courier": {
    "client": "delivery_client_b2b_logistics_payment",
    "partner": "delivery_park_b2b_logistics_payment"
  },
  "logistic_eda": {
    "client": "delivery_client_b2b_logistics_payment",
    "partner": "delivery_park_b2b_logistics_payment"
  }
}
)";

}  // namespace

struct TestData {
  std::vector<std::string> driver_classes;
  std::unordered_set<std::string> banned_parks;
  bool can_logistic = false;
  bool check_banned = false;
  bool allow = false;
};

class DriverClassesParametric : public ::testing::TestWithParam<TestData> {};

UTEST_P(DriverClassesParametric, TestHasNewContract) {
  Context context;

  auto park = parks_activation::models::Park();
  auto params = GetParam();
  park.can_logistic = params.can_logistic;
  park.park_id = "park_id";
  FetchParkActivation::Set(context, std::move(park));
  const auto member = GeoMember{{0, 0}, "dbid_uuid"};

  FetchFinalClasses::Set(context, params.driver_classes);

  const auto logistic_classes = formats::json::FromString(kSettingsConfig)
                                    .As<configs::LogisticClasses>()
                                    .allowed_classes;
  std::vector<std::string> classes{"eda", "grocery"};
  const taxi_config::candidates_shift_settings::CandidatesShiftSettings
      shift_classes{{classes}, {classes}};
  const auto& allowed_classes = logistic_classes - shift_classes.eats.classes -
                                shift_classes.grocery.classes;

  HasNewContract filter(kEmptyInfo, allowed_classes, params.banned_parks,
                        params.check_banned);
  EXPECT_EQ(filter.Process(member, context),
            (params.allow ? Result::kAllow : Result::kDisallow));
}

INSTANTIATE_UTEST_SUITE_P(
    HasNewContractTest, DriverClassesParametric,
    ::testing::Values(
        TestData{{"econom"}, {"park_id"}, false, false, true},
        TestData{{"econom"}, {"park_id"}, false, true, true},
        TestData{{"cargo"}, {"park_id"}, false, false, false},
        TestData{
            {"econom", "cargo", "courier"}, {"park_id"}, false, false, true},
        TestData{
            {"econom", "cargo", "courier"}, {"park_id"}, false, true, true},
        TestData{{"cargo", "courier"}, {"park_id"}, false, false, false},
        TestData{{"econom"}, {"park_id"}, true, false, true},
        TestData{{"econom"}, {"park_id"}, true, true, true},
        TestData{{"cargo"}, {"park_id"}, true, false, true},
        TestData{{"cargo"}, {"park_id"}, true, true, false},
        TestData{
            {"econom", "cargo", "courier"}, {"park_id"}, true, false, true},
        TestData{{"econom", "cargo", "courier"}, {"park_id"}, true, true, true},
        TestData{{"cargo", "courier"}, {"park_id"}, true, false, true},
        TestData{{"cargo", "courier"}, {"park_id"}, true, true, false},
        TestData{{"cargo", "courier", "eda"}, {"park_id"}, true, true, true}));
