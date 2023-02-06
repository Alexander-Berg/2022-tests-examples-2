#include <gtest/gtest.h>

#include <string>
#include <vector>

#include <eats-shared/types.hpp>
#include <requesters/stats.hpp>
#include <requesters/utils.hpp>
#include <tests/utils.hpp>

namespace eats_discounts_applicator::tests {

namespace {

clients::eats_order_stats::OrdersIdentityCounter AddCounter(
    int conter_value, const std::string& business_type,
    const std::string& place_id, const std::string& brand_id) {
  clients::eats_order_stats::OrdersIdentityCounter counter;
  counter.first_order_at = "2022-01-24T14:27:07+0000";
  counter.last_order_at = "2022-01-24T14:27:07+0000";
  counter.value = conter_value;
  {
    clients::eats_order_stats::OrdersStatsProperty property;
    property.name =
        clients::eats_order_stats::OrdersStatsPropertyName::kBusinessType;
    property.value = business_type;
    counter.properties.push_back(property);
  }
  {
    clients::eats_order_stats::OrdersStatsProperty property;
    property.name =
        clients::eats_order_stats::OrdersStatsPropertyName::kBrandId;
    property.value = brand_id;
    counter.properties.push_back(property);
  }
  {
    clients::eats_order_stats::OrdersStatsProperty property;
    property.name =
        clients::eats_order_stats::OrdersStatsPropertyName::kPlaceId;
    property.value = place_id;
    counter.properties.push_back(property);
  }
  return counter;
}

std::vector<clients::eats_order_stats::OrdersResponseDataItem> CreateStats(
    bool add_counter_for_eater_id, bool add_counter_for_phone_id,
    bool create_grocery_stats) {
  std::vector<clients::eats_order_stats::OrdersResponseDataItem> result;
  clients::eats_order_stats::OrdersStatsIdentity identity_eater_id = {
      clients::eats_order_stats::OrdersStatsIdentityType::kEaterId,
      "177047349"};
  std::vector<clients::eats_order_stats::OrdersIdentityCounter> counters;
  if (add_counter_for_eater_id) {
    counters.push_back(AddCounter(3, "restaurant", "86140", "105916"));
  }
  if (create_grocery_stats) {
    counters.push_back(AddCounter(2, "grocery", "81516", "162342"));
  }
  result.push_back({identity_eater_id, counters});

  counters.clear();

  clients::eats_order_stats::OrdersStatsIdentity identity_phone_id = {
      clients::eats_order_stats::OrdersStatsIdentityType::kPhoneId,
      "1d7b19a7e5af43e29ef5a6a8d6e19af9"};
  if (add_counter_for_phone_id) {
    counters.push_back(AddCounter(5, "restaurant", "86140", "105916"));
  }
  result.push_back({identity_phone_id, counters});
  return result;
}

std::vector<FullPlaceInfo> CreatePlaces() {
  std::vector<FullPlaceInfo> result;
  result.push_back({
      86140,                               // place_id
      105916,                              // brand_id
      1,                                   // region_id
      "UTC",                               // place_timezone
      eats_shared::Business::kRestaurant,  // place_business
      std::nullopt,                        // surge
      std::nullopt,                        // delivery_method
      "RU",                                // country
  });
  return result;
}

}  // namespace

namespace statistic {

struct TestParams {
  bool by_eater_id;
  bool by_phone_id;
  bool add_grocery_stats;
  int orders_total;
  std::string test_name;
};

class TestBuildStatistic : public testing::TestWithParam<TestParams> {};

std::string PrintToString(const TestParams& params) { return params.test_name; }

const std::vector<TestParams> kBasicTestParams = {
    {false, false, false, 0,
     "by_eater_id_false_by_phone_id_false_without_grocery"},
    {true, false, false, 3,
     "by_eater_id_true_by_phone_id_false_without_grocery"},
    {false, true, false, 5,
     "by_eater_id_false_by_phone_id_true_without_grocery"},
    {true, true, false, 5, "by_eater_id_true_by_phone_id_true_without_grocery"},
    {false, false, true, 0, "by_eater_id_false_by_phone_id_false_with_grocery"},
    {true, false, true, 3, "by_eater_id_true_by_phone_id_false_with_grocery"},
    {false, true, true, 5, "by_eater_id_false_by_phone_id_true_with_grocery"},
    {true, true, true, 5, "by_eater_id_true_by_phone_id_true_with_grocery"},
};

TEST_P(TestBuildStatistic, EmptyEaterIdStats) {
  const auto& params = GetParam();
  auto stats = CreateStats(params.by_eater_id, params.by_phone_id,
                           params.add_grocery_stats);
  auto places = CreatePlaces();
  auto response = requesters::StatsTransform(stats, places, {});
  ASSERT_EQ(response.orders_total, params.orders_total);
  if (!params.by_eater_id && !params.by_phone_id) {
    ASSERT_TRUE(response.by_brand.empty());
    ASSERT_TRUE(response.by_place.empty());
  } else {
    ASSERT_FALSE(response.by_brand.empty());
    ASSERT_FALSE(response.by_place.empty());
    ASSERT_EQ(response.by_brand.begin()->second.orders, params.orders_total);
    ASSERT_EQ(response.by_place.begin()->second.orders, params.orders_total);
  }
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestBuildStatistic,
                         testing::ValuesIn(kBasicTestParams),
                         testing::PrintToStringParamName());

}  // namespace statistic

}  // namespace eats_discounts_applicator::tests
