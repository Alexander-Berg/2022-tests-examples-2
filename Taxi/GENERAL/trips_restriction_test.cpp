#include <userver/utest/utest.hpp>

#include <userver/formats/parse/common_containers.hpp>

#include <models/trip_counter.hpp>
#include <models/trips_restriction.hpp>

namespace {

constexpr auto kYangoBrand = "yango";
constexpr auto kUberBrand = "uber";
constexpr auto kCashPaymentType = "cash";
constexpr auto kCardPaymentType = "card";
constexpr auto kEconom = "econom";
constexpr auto kVip = "vip";

constexpr auto kV1OrderResponseBody = R"(
[
    {
        "identity": {
            "type": "phone_id",
            "value": "test_phone_id"
        },
        "counters": [
            {
                "value": 10,
                "counted_from": "2021-01-01T00:00:00",
                "counted_to": "2022-01-01T00:00:00",
                "properties": [
                    {
                        "name": "brand",
                        "value": "yango"
                    },
                    {
                        "name": "payment_type",
                        "value": "card"
                    },
                    {
                        "name": "tariff_class",
                        "value": "econom"
                    }
                ]
            },
            {
                "value": 20,
                "counted_from": "2021-01-01T00:00:00",
                "counted_to": "2022-01-01T00:00:00",
                "properties": [
                    {
                        "name": "brand",
                        "value": "yango"
                    },
                    {
                        "name": "payment_type",
                        "value": "cash"
                    },
                    {
                        "name": "tariff_class",
                        "value": "econom"
                    }
                ]
            },
            {
                "value": 2,
                "counted_from": "2021-01-01T00:00:00",
                "counted_to": "2022-01-01T00:00:00",
                "properties": [
                    {
                        "name": "brand",
                        "value": "uber"
                    },
                    {
                        "name": "payment_type",
                        "value": "card"
                    },
                    {
                        "name": "tariff_class",
                        "value": "vip"
                    }
                ]
            }
        ]
    }
]
)";

using vector_orders =
    std::vector<clients::user_statistics::OrdersResponseDataItem>;
using vector_restriction =
    std::vector<handlers::libraries::discounts_match::TripsRestriction>;

auto MakeV1OrderResponseBody() {
  return formats::json::FromString(kV1OrderResponseBody).As<vector_orders>();
}

}  // namespace

TEST(TripCounter, Count) {
  const models::TripCounter trip_counter{MakeV1OrderResponseBody()};

  ASSERT_EQ(trip_counter.Count(kYangoBrand, kCardPaymentType, kEconom), 10);
  ASSERT_EQ(trip_counter.Count(kYangoBrand, kCashPaymentType, kEconom), 20);
  ASSERT_EQ(trip_counter.Count(kYangoBrand, std::nullopt, kEconom), 10 + 20);
  ASSERT_EQ(trip_counter.Count(kUberBrand, kCardPaymentType, kVip), 2);
  ASSERT_EQ(trip_counter.Count(kUberBrand, kCardPaymentType, kEconom), 0);
  ASSERT_EQ(trip_counter.Count(kUberBrand, kCashPaymentType, kEconom), 0);
  ASSERT_EQ(trip_counter.Count(kUberBrand, std::nullopt, std::nullopt), 2 + 0);
  ASSERT_EQ(trip_counter.Count(kUberBrand, std::nullopt, kVip), 2 + 0);
  ASSERT_EQ(trip_counter.Count(std::nullopt, kCardPaymentType, kEconom), 10);
  ASSERT_EQ(trip_counter.Count(std::nullopt, kCashPaymentType, kEconom), 20);
  ASSERT_EQ(trip_counter.Count(std::nullopt, std::nullopt, std::nullopt),
            10 + 20 + 2);
}

TEST(TripCounter, ParseSerialize) {
  const models::TripCounter trip_counter{MakeV1OrderResponseBody()};
  auto copy_trip_counter = formats::json::ValueBuilder(trip_counter)
                               .ExtractValue()
                               .As<models::TripCounter>();
  EXPECT_EQ(trip_counter.GetData(), MakeV1OrderResponseBody());
  EXPECT_EQ(copy_trip_counter.GetData(), MakeV1OrderResponseBody());
}

UTEST(TripsRestriction, TripCounterEmpty) {
  vector_restriction restriction_uber(
      {{{0, 4}, kUberBrand, kCashPaymentType, kVip}});
  models::TripCounter trip_counter(vector_orders({}));
  {
    models::TripsRestriction trips_restriction({});
    EXPECT_TRUE(trips_restriction.Select(trip_counter).empty());
  }
  {
    models::TripsRestriction trips_restriction(restriction_uber);
    EXPECT_EQ(trips_restriction.Select(trip_counter), restriction_uber);
  }
}

UTEST(TripsRestriction, TripCounterNotEmpty) {
  models::TripCounter trip_counter(MakeV1OrderResponseBody());
  {
    vector_restriction restriction_uber(
        {{{0, 4}, kUberBrand, kCashPaymentType, kVip}});
    models::TripsRestriction trips_restriction(restriction_uber);
    EXPECT_EQ(trips_restriction.Select(trip_counter), restriction_uber);
  }
  {
    models::TripsRestriction trips_restriction(
        {{{0, 1}, kUberBrand, kCardPaymentType, kVip},
         {{0, 1}, kUberBrand, std::nullopt, std::nullopt},
         {{4, 4}, kYangoBrand, kCardPaymentType, std::nullopt},
         {{4, 4}, kYangoBrand, std::nullopt, kEconom}});
    EXPECT_TRUE(trips_restriction.Select(trip_counter).empty());
  }
  {
    vector_restriction restriction_uber(
        {{{1, 2}, kUberBrand, kCardPaymentType, kVip}});
    models::TripsRestriction trips_restriction(restriction_uber);
    EXPECT_EQ(trips_restriction.Select(trip_counter), restriction_uber);
  }
  {
    vector_restriction restriction_yango(
        {{{0, 3}, kYangoBrand, kCardPaymentType, kEconom}});
    models::TripsRestriction trips_restriction(restriction_yango);
    EXPECT_TRUE(trips_restriction.Select(trip_counter).empty());
  }
  {
    vector_restriction restriction_yango(
        {{{5, 9}, kYangoBrand, kCardPaymentType, std::nullopt}});
    models::TripsRestriction trips_restriction(restriction_yango);
    EXPECT_TRUE(trips_restriction.Select(trip_counter).empty());
  }
}
