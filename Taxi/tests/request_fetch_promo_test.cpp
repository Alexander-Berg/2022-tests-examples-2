#include <gtest/gtest.h>

#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

#include <userver/utils/datetime.hpp>

#include <clients/eats-discounts/definitions.hpp>
#include <eats-discounts-applicator/models.hpp>
#include <testing/taxi_config.hpp>

#include <eats-shared/types.hpp>
#include <requesters/discounts.hpp>
#include <requesters/utils.hpp>
#include <tests/utils.hpp>

namespace eats_discounts_applicator::requesters::tests {

namespace fetch_requests {

namespace {

StatsInfo MakeStatsInfo() {
  StatsInfo result{10, {}, {}, {}, {}, {}};

  result.by_brand.emplace(
      "2342", StatsInfoItem{10, std::chrono::system_clock::from_time_t(1000),
                            std::chrono::system_clock::now()});
  result.by_place.emplace(
      "199123", StatsInfoItem{6, std::chrono::system_clock::from_time_t(1345),
                              std::chrono::system_clock::now()});
  result.by_place.emplace(
      "199128", StatsInfoItem{4, std::chrono::system_clock::from_time_t(1023),
                              std::chrono::system_clock::now()});
  result.first_user_order_time =
      min(std::chrono::system_clock::from_time_t(1000),
          std::chrono::system_clock::from_time_t(1345));
  result.last_user_order_time = std::chrono::system_clock::now();

  return result;
}

std::vector<dynamic_config::KeyValue> DefaultConfigsForTests(
    size_t client_limits) {
  return {{
      taxi_config::EATS_DISCOUNTS_FETCH_PROMO_SETTINGS,
      {{"__default__", {{} /* limits */, {client_limits} /*client_limits*/}}},
  }};
}

struct RequestData {
  int64_t region_id;
  int64_t brand_id;
  int64_t place_id;
};

struct MockedData {
  std::vector<FullPlaceInfo> full_places_info;
  std::vector<RequestData> data_request;
};

MockedData MockData() {
  MockedData result;
  int64_t place_id = 0;
  for (int64_t region_id = 0; region_id < 2; ++region_id) {
    for (int64_t brand_id = 0; brand_id < 2; ++brand_id) {
      for (int64_t cnt_places = 0; cnt_places < 2; ++cnt_places) {
        result.full_places_info.push_back(
            {place_id, brand_id, region_id, "UTC" /*place_timezone*/,
             eats_shared::Business::kRestaurant /*place_business*/,
             std::nullopt /*surge*/, std::nullopt /*delivery_method*/,
             "RU" /*country*/});
        result.data_request.push_back(
            RequestData{region_id, brand_id, place_id++});
      }
    }
  }
  return result;
}

}  // namespace

TEST(TestGetEatsDiscountsFetchPlacePromoReq, WithStatsAndPlaceInfo) {
  std::vector<FullPlaceInfo> full_places_info;
  full_places_info.push_back({199123, 2342, 11, "Moscow",
                              eats_shared::Business::kRestaurant, Money{12},
                              DeliveryMethod::kVehicle, "RU"});
  full_places_info.push_back({199128, 2342, 11, "Moscow",
                              eats_shared::Business::kRestaurant, Money{3},
                              DeliveryMethod::kPedestrian, "RU"});

  StatsInfo stats_info = MakeStatsInfo();
  EaterTags eater_tags = {"tag1", "tag2", "tag3"};
  const auto snapshot = dynamic_config::GetDefaultSnapshot();
  auto delivery_time = utils::datetime::Stringtime("2019-01-21T16:29:00+0000");

  const auto& requests = GetEatsDiscountsFetchPlacePromoReq(
      full_places_info, std::nullopt, snapshot, stats_info, eater_tags,
      "delivery", {"one", "two"}, delivery_time);
  EXPECT_EQ(requests.size(), 1);
  EXPECT_TRUE(requests[0].body.user_conditions.orders_count.has_value());
  EXPECT_EQ(requests[0].body.user_conditions.orders_count, 10);
  EXPECT_TRUE(requests[0].body.user_conditions.experiments.has_value());
  EXPECT_TRUE(
      requests[0].body.user_conditions.time_from_last_order.has_value());

  EXPECT_EQ(requests[0].body.regions[0].id, 11);
  EXPECT_EQ(requests[0].body.time_zone, "Moscow");
  EXPECT_EQ(requests[0].body.time, delivery_time);

  EXPECT_EQ(requests[0].body.regions[0].brands.size(), 1);
  EXPECT_EQ(requests[0].body.regions[0].brands[0].id, 2342);
  EXPECT_TRUE(requests[0]
                  .body.regions[0]
                  .brands[0]
                  .user_conditions.orders_count.has_value());
  EXPECT_EQ(requests[0]
                .body.regions[0]
                .brands[0]
                .user_conditions.orders_count.value(),
            10);
  EXPECT_TRUE(requests[0]
                  .body.regions[0]
                  .brands[0]
                  .user_conditions.time_from_last_order.has_value());

  EXPECT_EQ(requests[0].body.regions[0].brands[0].places.size(), 2);
  EXPECT_EQ(requests[0].body.regions[0].brands[0].places[0].id, 199123);
  EXPECT_TRUE(
      requests[0].body.regions[0].brands[0].places[0].surge.has_value());
  EXPECT_EQ(requests[0].body.regions[0].brands[0].places[0].surge.value(),
            "12");
  EXPECT_TRUE(requests[0]
                  .body.regions[0]
                  .brands[0]
                  .places[0]
                  .delivery_method.has_value());
  EXPECT_EQ(
      requests[0].body.regions[0].brands[0].places[0].delivery_method.value(),
      "vehicle");
  EXPECT_TRUE(requests[0]
                  .body.regions[0]
                  .brands[0]
                  .places[0]
                  .user_conditions.orders_count.has_value());
  EXPECT_EQ(requests[0]
                .body.regions[0]
                .brands[0]
                .places[0]
                .user_conditions.orders_count.value(),
            6);
  EXPECT_TRUE(requests[0]
                  .body.regions[0]
                  .brands[0]
                  .places[0]
                  .user_conditions.time_from_last_order.has_value());

  EXPECT_EQ(requests[0].body.regions[0].brands[0].places[1].id, 199128);
  EXPECT_TRUE(
      requests[0].body.regions[0].brands[0].places[1].surge.has_value());
  EXPECT_EQ(requests[0].body.regions[0].brands[0].places[1].surge.value(), "3");
  EXPECT_TRUE(requests[0]
                  .body.regions[0]
                  .brands[0]
                  .places[1]
                  .delivery_method.has_value());
  EXPECT_EQ(
      requests[0].body.regions[0].brands[0].places[1].delivery_method.value(),
      "pedestrian");
  EXPECT_TRUE(requests[0]
                  .body.regions[0]
                  .brands[0]
                  .places[1]
                  .user_conditions.orders_count.has_value());
  EXPECT_EQ(requests[0]
                .body.regions[0]
                .brands[0]
                .places[1]
                .user_conditions.orders_count.value(),
            4);
  EXPECT_TRUE(requests[0]
                  .body.regions[0]
                  .brands[0]
                  .places[1]
                  .user_conditions.time_from_last_order.has_value());
}

struct FetchPlacePromoTestParams {
  int64_t client_limits;
  std::vector<std::vector<size_t>> exp_requests_size;
  std::string test_name;
};

class TestFetchPlacePromoRequestsBuilder
    : public testing::TestWithParam<FetchPlacePromoTestParams> {};

std::string PrintToString(const FetchPlacePromoTestParams& params) {
  return params.test_name;
}

const std::vector<FetchPlacePromoTestParams>
    kEatsDiscountsFetchPlacePromoTestParams = {
        {10, {{2, 2}}, "less_max_size"},

        {4, {{2, 2}, {2, 2}}, "exactly_max_size"},

        {3, {{2, 1}, {1}, {2}}, "more_max_size"},

        {2, {{2}, {2}, {2}, {2}}, "more_max_size_2"},

        {1, {{1}, {1}, {1}, {1}, {1}, {1}, {1}, {1}}, "more_max_size_3"},
};

TEST_P(TestFetchPlacePromoRequestsBuilder,
       EatsDiscountsFetchPlacePromoRequest) {
  const auto params = GetParam();

  auto config_storage = dynamic_config::MakeDefaultStorage(
      DefaultConfigsForTests(params.client_limits));
  auto config_snapshot = config_storage.GetSnapshot();

  auto mocked_data = MockData();
  auto delivery_time = utils::datetime::Stringtime("2019-01-21T16:29:00+0000");

  auto requests = GetEatsDiscountsFetchPlacePromoReq(
      mocked_data.full_places_info, "eats-discounts-applicator",
      config_snapshot, {} /*stats_info*/, {} /*tags*/, "delivery", {},
      delivery_time);

  ASSERT_EQ(requests.size(), params.exp_requests_size.size());
  EXPECT_EQ(requests[0].body.time, delivery_time);
  for (size_t i = 0; i < requests.size(); ++i) {
    const auto& request = requests[i];
    const auto& exp_brands = params.exp_requests_size[i];
    ASSERT_EQ(request.body.hierarchies_fetch_parameters.size(), 6);
    ASSERT_EQ(request.body.regions[0].brands.size(), exp_brands.size());
    for (size_t j = 0; j < request.body.regions[0].brands.size(); ++j) {
      const auto& brands = request.body.regions[0].brands[j];
      const auto& exp_place_size = exp_brands[j];
      ASSERT_EQ(brands.places.size(), exp_place_size);
      for (size_t k = 0; k < brands.places.size(); ++k) {
        RequestData data{request.body.regions[0].id, brands.id,
                         brands.places[k].id};
        auto it = std::find_if(
            mocked_data.data_request.begin(), mocked_data.data_request.end(),
            [&data](const auto& a) {
              return a.region_id == data.region_id &&
                     a.brand_id == data.brand_id && a.place_id == data.place_id;
            });
        ASSERT_NE(it, mocked_data.data_request.end());
      }
    }
  }
}

INSTANTIATE_TEST_SUITE_P(
    /* no prefix */, TestFetchPlacePromoRequestsBuilder,
    testing::ValuesIn(kEatsDiscountsFetchPlacePromoTestParams),
    testing::PrintToStringParamName());

}  // namespace fetch_requests

}  // namespace eats_discounts_applicator::requesters::tests
