#include <userver/utest/utest.hpp>

#include <endpoints/full/plugins/drive_order_flow/drive_sort_offers.hpp>

#include "tests/endpoints/common/service_level_mock_test.hpp"

#include "drive_order_flow_common_test.hpp"

namespace routestats::plugins::drive_order_flow {

namespace {

selector_settings::Algorithm kDefaultAlgo{
    false,     // enabled
    "econom",  // reference_class
    {},        // thresholds
    {},        // rangings
};

selector_settings::Algorithm kAlgoSortRideMin{
    true,      // enabled
    "econom",  // reference_class
    {},        // thresholds
    {{
        selector_settings::AlgorithmParam::kRideDurationMin,
        std::nullopt,
        selector_settings::AlgorithmRangingOrder::kAscending,
    }},  // rangings
};

selector_settings::Algorithm kAlgoSortDrivePriceMinWalk{
    true,      // enabled
    "econom",  // reference_class
    {},        // thresholds
    {{
         selector_settings::AlgorithmParam::kDrivePriceRub,
         std::nullopt,
         selector_settings::AlgorithmRangingOrder::kAscending,
     },
     {
         selector_settings::AlgorithmParam::kWalkDurationMin,
         20,
         selector_settings::AlgorithmRangingOrder::kDescending,
     }},  // rangings
};

selector_settings::ValueSettings MakeSettings(
    const std::optional<selector_settings::Algorithm>& algo) {
  return {"drive", false, algo};
}

std::vector<DriveOffer> kDefaultOffers{
    {
        "too_expensive",  //
        Decimal{500},     // price
        "some_car", "к500ек777", "http://example.com/some_car.png",
        Decimal{"1.5"},   // walk
        Decimal{"16"},    // ride
        15,               // walk original
        "8 мин",          // localized_walking_duration_min
        "too_expensive",  // short_name
        std::nullopt,     // localized_free_reservation_duration_min
        std::nullopt,     // localized_riding_duration_min
        std::nullopt,     // cashback_prediction
        Decimal{"1.8"},   // price_undiscounted
    },
    {
        "too_cheap",  //
        Decimal{50},  // price
        "some_car", "к050ек777", "http://example.com/some_car.png",
        Decimal{"1.5"},  // walk
        Decimal{"13"},   // ride
        15,              // walk original
        "8 мин",         // localized_walking_duration_min
        "too_cheap",     // short_name
        std::nullopt,    // localized_free_reservation_duration_min
        std::nullopt,    // localized_riding_duration_min
        std::nullopt,    // cashback_prediction
        std::nullopt,    // price_undiscounted
    },
    {
        // least drive/taxi price ratio
        "ratio_0.25x",  //
        Decimal{70},    // price
        "some_car", "к250ек777", "http://example.com/some_car.png",
        Decimal{"10"},  // walk
        Decimal{"14"},  // ride
        10,             // walk original
        "8 мин",        // localized_walking_duration_min
        "ratio_0.25x",  // short_name
        std::nullopt,   // localized_free_reservation_duration_min
        std::nullopt,   // localized_riding_duration_min
        std::nullopt,   // cashback_prediction
        std::nullopt,   // price_undiscounted
    },
    {
        // little more expensive, but walk duration is less
        "ratio_0.255x",  //
        Decimal{90},     // price
        "some_car", "к255ек777", "http://example.com/some_car.png",
        Decimal{"5"},    // walk
        Decimal{"15"},   // ride
        5,               // walk original
        "8 мин",         // localized_walking_duration_min
        "ratio_0.255x",  // short_name
        std::nullopt,    // localized_free_reservation_duration_min
        std::nullopt,    // localized_riding_duration_min
        std::nullopt,    // cashback_prediction
        std::nullopt,    // price_undiscounted
    },
    {
        // very fast walk, but bad drive/taxi price ratio (diff is 0.02 > 0.01)
        "too_fast_ride",  //
        Decimal{150},     // price
        "some_car", "к270ек777", "http://example.com/some_car.png",
        Decimal{"0.5"},   // walk
        Decimal{"10"},    // ride
        1,                // walk original
        "8 мин",          // localized_walking_duration_min
        "too_fast_ride",  // short_name
        std::nullopt,     // localized_free_reservation_duration_min
        std::nullopt,     // localized_riding_duration_min
        std::nullopt,     // cashback_prediction
        std::nullopt,     // price_undiscounted
    },
};

core::Decimal kTaxiTariffOfferPriceRub{1000};

}  // namespace

struct SortOffersTestInput {
  selector_settings::Algorithm algo;
  std::string offer_id;
};

const std::vector<SortOffersTestInput> kSortOffersTestInputs{
    {// experiment disabled, return first
     kDefaultAlgo, "too_cheap"},
    {// experiment enabled, sort by drive price
     kAlgoSortRideMin, "too_fast_ride"},
    {// experiment enabled, sort by drive price and min walk with max diff
     kAlgoSortDrivePriceMinWalk, "ratio_0.25x"},
};

class DriveSortOffers : public testing::TestWithParam<SortOffersTestInput> {};

UTEST_P(DriveSortOffers, AllCases) {
  std::vector<DriveOffer> offers;
  offers.reserve(kDefaultOffers.size());
  std::copy(kDefaultOffers.begin(), kDefaultOffers.end(),
            std::back_inserter(offers));
  auto [algo, offer_id] = GetParam();
  SortOffers(offers, kTaxiTariffOfferPriceRub, MakeSettings(algo));
  ASSERT_EQ(offers[0].offer_id.value(), offer_id);
  ASSERT_EQ(offers.size(), kDefaultOffers.size());
}

INSTANTIATE_UTEST_SUITE_P(/* no prefix */, DriveSortOffers,
                          testing::ValuesIn(kSortOffersTestInputs));

}  // namespace routestats::plugins::drive_order_flow
