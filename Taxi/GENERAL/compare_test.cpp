#include "compare.hpp"

#include <gtest/gtest.h>

namespace umlaas_eats::utils::catalog::impl {

namespace {

using ml::eats::places_ranking::api::v2::Place;

template <typename... Apply>
Place MakePlace(Apply... apply) {
  Place result;

  (apply(result), ...);

  return result;
}

[[maybe_unused]] auto WithId(const int id) {
  return [id](Place& place) { place.id = id; };
}

[[maybe_unused]] auto WithAvailable(const bool available) {
  return [available](Place& place) { place.is_available = available; };
}

[[maybe_unused]] auto WithEtaMin(const unsigned int eta_min) {
  return [eta_min](Place& place) { place.eta_minutes_min = eta_min; };
}

[[maybe_unused]] auto WithAverageRating(const double average_user_rating) {
  return [average_user_rating](Place& place) {
    place.average_user_rating = average_user_rating;
  };
}

[[maybe_unused]] auto WithDeliveryType(std::string&& delivery_type) {
  return [delivery_type = std::move(delivery_type)](Place& place) {
    place.delivery_type = std::move(delivery_type);
  };
}

[[maybe_unused]] auto WithCourierType(std::string&& courier_type) {
  return [courier_type = std::move(courier_type)](Place& place) {
    place.courier_type = std::move(courier_type);
  };
}

[[maybe_unused]] auto WithBusiness(std::string&& business) {
  return [business = std::move(business)](Place& place) {
    place.business_type = std::move(business);
  };
}

#define BETTER(func, lhs, rhs)                      \
  EXPECT_EQ(func(lhs, rhs), CompareResult::kBetter) \
      << #func "(\n\t" #lhs ",\n\t" #rhs "\n) != Better";

#define WORST(func, lhs, rhs)                      \
  EXPECT_EQ(func(lhs, rhs), CompareResult::kWorst) \
      << #func "(\n\t" #lhs ",\n\t" #rhs "\n) != Worst";

#define EQUAL(func, lhs, rhs)                      \
  EXPECT_EQ(func(lhs, rhs), CompareResult::kEqual) \
      << #func "(\n\t" #lhs ",\n\t" #rhs "\n) != Equal";

}  // namespace

TEST(Compare, Available) {
  WORST(Available, MakePlace(WithAvailable(true)),
        MakePlace(WithAvailable(false)));
  BETTER(Available, MakePlace(WithAvailable(false)),
         MakePlace(WithAvailable(true)));
  EQUAL(Available, MakePlace(WithAvailable(false)),
        MakePlace(WithAvailable(false)));
  EQUAL(Available, MakePlace(WithAvailable(true)),
        MakePlace(WithAvailable(true)));
}

TEST(Compare, WithLessEta) {
  WORST(WithLessEta, MakePlace(WithEtaMin(10)), MakePlace(WithEtaMin(20)));
  BETTER(WithLessEta, MakePlace(WithEtaMin(30)), MakePlace(WithEtaMin(10)));
  EQUAL(WithLessEta, MakePlace(WithEtaMin(15)), MakePlace(WithEtaMin(15)));
}

TEST(Compare, WithGreaterRating) {
  WORST(WithGreaterRating, MakePlace(WithAverageRating(4.25)),
        MakePlace(WithAverageRating(4.24)));
  BETTER(WithGreaterRating, MakePlace(WithAverageRating(3.1)),
         MakePlace(WithAverageRating(5.0)));
  EQUAL(WithGreaterRating, MakePlace(WithAverageRating(1.0000001)),
        MakePlace(WithAverageRating(1.0000004)));
}

TEST(Compare, NativeNonAutoBetter) {
  const auto native = WithDeliveryType("native");

  WORST(NativeNonAutoBetter, MakePlace(native, WithCourierType("yandex_rover")),
        MakePlace(native, WithCourierType("yandex_taxi")));
  BETTER(NativeNonAutoBetter, MakePlace(native, WithCourierType("vehicle")),
         MakePlace(native, WithCourierType("pedestrian")));
  EQUAL(NativeNonAutoBetter, MakePlace(native, WithCourierType("vehicle")),
        MakePlace(native, WithCourierType("yandex_taxi")));
  EQUAL(NativeNonAutoBetter, MakePlace(native, WithCourierType("yandex_taxi")),
        MakePlace(native, WithCourierType("yandex_taxi")));
  EQUAL(NativeNonAutoBetter, MakePlace(native, WithCourierType("pedestrian")),
        MakePlace(native, WithCourierType("bicycle")));
  EQUAL(NativeNonAutoBetter,
        MakePlace(WithDeliveryType("market"), WithCourierType("pedestrian")),
        MakePlace(native, WithCourierType("vehicle")));
}

TEST(Compare, NativeWithLessDeliveryTimeComparator) {
  std::unordered_map<int, models::catalog::Route> id_to_route;
  {
    id_to_route[1].minutes = 10;
    id_to_route[2].minutes = 10;
    id_to_route[3].minutes = 5;
    id_to_route[4].minutes = 20;
  }

  auto native_with_less_delivery_time =
      NativeWithLessDeliveryTimeComparator(id_to_route);

  const auto native = WithDeliveryType("native");

  WORST(native_with_less_delivery_time, MakePlace(WithId(3), native),
        MakePlace(WithId(2), native));
  BETTER(native_with_less_delivery_time, MakePlace(WithId(4), native),
         MakePlace(WithId(2), native));
  EQUAL(native_with_less_delivery_time, MakePlace(WithDeliveryType("market")),
        MakePlace(WithDeliveryType("market")));
  EQUAL(native_with_less_delivery_time, MakePlace(WithId(1), native),
        MakePlace(WithId(2), native));
  EQUAL(native_with_less_delivery_time,
        MakePlace(WithId(1), WithCourierType("yandex_taxi"), native),
        MakePlace(WithId(2), WithCourierType("pedestrian"), native));
}

TEST(Compare, NativeNonAutoWithLessDeliveryTimeComparator) {
  std::unordered_map<int, models::catalog::Route> id_to_route;
  {
    id_to_route[1].minutes = 10;
    id_to_route[2].minutes = 10;
    id_to_route[3].minutes = 5;
    id_to_route[4].minutes = 20;
  }

  auto native_with_less_delivery_time =
      NativeNonAutoWithLessDeliveryTimeComparator(id_to_route);

  const auto native = WithDeliveryType("native");

  EQUAL(native_with_less_delivery_time, MakePlace(WithDeliveryType("market")),
        MakePlace(WithDeliveryType("market")));
  EQUAL(native_with_less_delivery_time,
        MakePlace(native, WithCourierType("pedestrian")),
        MakePlace(WithDeliveryType("market"), WithCourierType("yandex_taxi")));
  WORST(native_with_less_delivery_time, MakePlace(WithId(3), native),
        MakePlace(WithId(2), native));
  BETTER(native_with_less_delivery_time, MakePlace(WithId(4), native),
         MakePlace(WithId(2), native));
  EQUAL(native_with_less_delivery_time, MakePlace(WithId(1), native),
        MakePlace(WithId(2), native));
}

TEST(Compare, HasPriorityTagComparator) {
  std::unordered_map<int, std::unordered_set<std::string>> tags;
  {
    tags[1] = {"tag1"};
    tags[2] = {};
    tags[3] = {"tag2"};
    tags[4] = {"tag1"};
  }

  auto has_tag = HasPriorityTagComparator("tag1", tags);

  EQUAL(has_tag, MakePlace(WithId(1)), MakePlace(WithId(4)));
  EQUAL(has_tag, MakePlace(WithId(2)), MakePlace(WithId(3)));
  WORST(has_tag, MakePlace(WithId(1)), MakePlace(WithId(3)));
  BETTER(has_tag, MakePlace(WithId(2)), MakePlace(WithId(4)));
}

TEST(Compare, RetailComparator) {
  using models::catalog::SlotAvailability;

  std::unordered_map<int, SlotAvailability> id_to_slot;
  {
    id_to_slot[1] = SlotAvailability{
        true,   // is_asap_available
        false,  // is_slot_available
    };
    id_to_slot[2] = SlotAvailability{
        false,  // is_asap_available
        true,   // is_slot_available
    };
    id_to_slot[3] = SlotAvailability{
        true,  // is_asap_available
        true,  // is_slot_available
    };
    id_to_slot[4] = SlotAvailability{
        false,  // is_asap_available
        false,  // is_slot_available
    };
    id_to_slot[5] = SlotAvailability{
        false,  // is_asap_available
        false,  // is_slot_available
    };
  }

  std::unordered_map<int, models::catalog::Route> id_to_route;
  {
    id_to_route[1].distance = 8129;
    id_to_route[2].distance = 5021;
    id_to_route[3].distance = 5021;
    id_to_route[4].distance = 2311;
    id_to_route[5].distance = 7102;
  }

  const auto shop = WithBusiness("shop");

  auto retail_cmp = RetailComparator(7000, id_to_route, id_to_slot);

  // Одинаковое расстояние, оба до трешхолда, 3 доступен ASAP = лучше
  BETTER(retail_cmp, MakePlace(shop, WithId(2)), MakePlace(shop, WithId(3)));
  // Разное расстояние, 1 за трешхолдом, 3 лучше
  WORST(retail_cmp, MakePlace(shop, WithId(3)), MakePlace(shop, WithId(1)));
  // Разное расстояние, оба до трешхолда, у обоих недоступен ASAP, выбираем
  // ближайший - 4
  BETTER(retail_cmp, MakePlace(shop, WithId(2)), MakePlace(shop, WithId(4)));
  // Разное расстояние, оба после трешхолда, у 1 доступен ASAP, но 5 ближе и
  // поэтому лучше
  BETTER(retail_cmp, MakePlace(shop, WithId(1)), MakePlace(shop, WithId(5)));

  const auto restaurant = WithBusiness("restaurant");

  EQUAL(retail_cmp, MakePlace(restaurant, WithId(3)),
        MakePlace(restaurant, WithId(1)));
  EQUAL(retail_cmp, MakePlace(restaurant, WithId(2)),
        MakePlace(restaurant, WithId(4)));
}

TEST(Compare, DistanceComparator) {
  std::unordered_map<int, models::catalog::Route> id_to_route;
  {
    id_to_route[1].distance = 8129;
    id_to_route[2].distance = 5021;
    id_to_route[3].distance = 5021;
    id_to_route[4].distance = 2311;
    id_to_route[5].distance = 7102;
  }

  auto distance_cmp = DistanceComparator(id_to_route);

  EQUAL(distance_cmp, MakePlace(WithId(2)), MakePlace(WithId(3)));
  BETTER(distance_cmp, MakePlace(WithId(1)), MakePlace(WithId(5)));
  WORST(distance_cmp, MakePlace(WithId(4)), MakePlace(WithId(5)));
}

}  // namespace umlaas_eats::utils::catalog::impl
