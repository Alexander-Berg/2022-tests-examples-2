#include <gtest/gtest.h>

#include <optional>

#include <client-user-statistics/models.hpp>
#include <experiments3/user_statistics_params.hpp>
#include <models/pa_auth_context.hpp>
#include <userver/utils/datetime.hpp>

user_statistics::models::Identities MakeDefaultIdentity() {
  return {{clients::user_statistics::OrdersStatsIdentityType::kPhoneId,
           "phone_id"}};
}

user_statistics::models::Timerange MakeValidTimerange() {
  const auto shift = std::chrono::hours(1);
  const auto now = utils::datetime::Now();
  return user_statistics::models::Timerange{now - shift, std::nullopt};
}

user_statistics::models::Timerange MakeOutOfLimitTimerange() {
  const auto shift = std::chrono::hours(32 * 24);  // 32 days * 24 hours
  const auto now = utils::datetime::Now();
  return user_statistics::models::Timerange{now - shift, std::nullopt};
}

user_statistics::models::Timerange MakeInvalidTimerange() {
  const auto shift = std::chrono::hours(1);
  const auto now = utils::datetime::Now();
  return user_statistics::models::Timerange{now, now - shift};
}

TEST(TestClientUserStatistics, RequestParamsValidationTest) {
  {
    user_statistics::models::RequestParams params;
    ASSERT_FALSE(params.IsValid());
  }
  {
    user_statistics::models::RequestParams params;
    params.identities = MakeDefaultIdentity();
    ASSERT_TRUE(params.IsValid());
  }
  {
    user_statistics::models::RequestParams params;
    params.identities = MakeDefaultIdentity();
    params.timerange = MakeOutOfLimitTimerange();
    ASSERT_FALSE(params.IsValid());
  }
  {
    user_statistics::models::RequestParams params;
    params.identities = MakeDefaultIdentity();
    params.timerange = MakeInvalidTimerange();
    ASSERT_FALSE(params.IsValid());
  }
  {
    user_statistics::models::RequestParams params;
    params.identities = MakeDefaultIdentity();
    params.timerange = MakeValidTimerange();
    ASSERT_TRUE(params.IsValid());
  }
}

TEST(TestClientUserStatistics, RequestParamsMakeTest) {
  {
    const experiments3::user_statistics_params::RequestRule rr;
    const passenger_authorizer::models::AuthContext ac;
    const auto fact_value =
        user_statistics::models::RequestParams::Make(rr, ac);
    auto expected_value = user_statistics::models::RequestParams{};
    expected_value.group_by = user_statistics::models::PropertyNames{};
    ASSERT_EQ(expected_value, fact_value);
    ASSERT_FALSE(fact_value.IsValid());
  }

  {
    const auto identities =
        std::vector<experiments3::user_statistics_params::IdentityType>{
            experiments3::user_statistics_params::IdentityType::kPhoneId};
    experiments3::user_statistics_params::RequestRule rr;
    rr.identities = identities;

    const passenger_authorizer::models::AuthContext ac;
    const auto fact_value =
        user_statistics::models::RequestParams::Make(rr, ac);
    auto expected_value = user_statistics::models::RequestParams{};
    expected_value.group_by = user_statistics::models::PropertyNames{};
    ASSERT_EQ(expected_value, fact_value);
    ASSERT_FALSE(fact_value.IsValid());
  }

  {
    const auto identities =
        std::vector<experiments3::user_statistics_params::IdentityType>{
            experiments3::user_statistics_params::IdentityType::kPhoneId};
    experiments3::user_statistics_params::RequestRule rr;
    rr.identities = identities;

    passenger_authorizer::models::AuthContext ac;
    ac.yandex_taxi_phoneid = "test_taxi_phoneid";
    const auto fact_value =
        user_statistics::models::RequestParams::Make(rr, ac);
    const auto expected_value_identities = user_statistics::models::Identities{
        user_statistics::models::us::OrdersStatsIdentity{
            clients::user_statistics::OrdersStatsIdentityType::kPhoneId,
            "test_taxi_phoneid"}};
    auto expected_value = user_statistics::models::RequestParams{};
    expected_value.identities = expected_value_identities;
    expected_value.group_by = user_statistics::models::PropertyNames{};
    ASSERT_EQ(expected_value, fact_value);
    ASSERT_TRUE(fact_value.IsValid());
  }

  {
    const auto identities =
        std::vector<experiments3::user_statistics_params::IdentityType>{
            experiments3::user_statistics_params::IdentityType::kDeviceId};
    experiments3::user_statistics_params::RequestRule rr;
    rr.identities = identities;

    passenger_authorizer::models::AuthContext ac;
    const auto fact_value =
        user_statistics::models::RequestParams::Make(rr, ac, "test_device_id");
    const auto expected_value_identities = user_statistics::models::Identities{
        user_statistics::models::us::OrdersStatsIdentity{
            clients::user_statistics::OrdersStatsIdentityType::kDeviceId,
            "test_device_id"}};
    auto expected_value = user_statistics::models::RequestParams{};
    expected_value.identities = expected_value_identities;
    expected_value.group_by = user_statistics::models::PropertyNames{};
    ASSERT_EQ(expected_value, fact_value);
    ASSERT_TRUE(fact_value.IsValid());
  }

  {
    const auto identities = std::vector<
        experiments3::user_statistics_params::IdentityType>{
        experiments3::user_statistics_params::IdentityType::kCardPersistentId};
    experiments3::user_statistics_params::RequestRule rr;
    rr.identities = identities;

    passenger_authorizer::models::AuthContext ac;
    const auto fact_value = user_statistics::models::RequestParams::Make(
        rr, ac, std::nullopt, "test_card_persistent_id");
    const auto expected_value_identities = user_statistics::models::Identities{
        user_statistics::models::us::OrdersStatsIdentity{
            clients::user_statistics::OrdersStatsIdentityType::
                kCardPersistentId,
            "test_card_persistent_id"}};
    auto expected_value = user_statistics::models::RequestParams{};
    expected_value.identities = expected_value_identities;
    expected_value.group_by = user_statistics::models::PropertyNames{};
    ASSERT_EQ(expected_value, fact_value);
    ASSERT_TRUE(fact_value.IsValid());
  }
}

TEST(TestStatistics, MaxOrdersCount) {
  {
    const user_statistics::models::Statistics s;
    ASSERT_EQ(0, s.MaxOrdersCount());
  }

  auto make_order_response_data_item = [](std::vector<int> const& values) {
    std::vector<clients::user_statistics::OrdersIdentityCounter>
        ordersIdentityCounter(values.size());
    for (uint32_t i = 0; i < values.size(); ++i) {
      ordersIdentityCounter[i].value = values[i];
    }

    user_statistics::models::us::OrdersResponseDataItem ordersResponseDataItem;
    ordersResponseDataItem.counters = ordersIdentityCounter;
    return ordersResponseDataItem;
  };

  {
    auto ordersResponseDataItem = make_order_response_data_item({0, 42, 3});

    user_statistics::models::Statistics s;
    s.identities_counters =
        std::vector<user_statistics::models::us::OrdersResponseDataItem>{
            ordersResponseDataItem};
    ASSERT_EQ(42, s.MaxOrdersCount());
  }

  {
    auto ordersResponse1 = make_order_response_data_item({-3, -1, -2});
    auto ordersResponse2 = make_order_response_data_item({0, 42, 3});
    auto ordersResponse3 = make_order_response_data_item({1, 2, 3});

    user_statistics::models::Statistics s;
    s.identities_counters =
        std::vector<user_statistics::models::us::OrdersResponseDataItem>{
            ordersResponse1, ordersResponse2, ordersResponse3};
    ASSERT_EQ(42, s.MaxOrdersCount());
  }
}
