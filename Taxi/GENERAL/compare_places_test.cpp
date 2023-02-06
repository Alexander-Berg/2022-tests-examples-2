#include <gtest/gtest.h>

#include <geometry/distance.hpp>

#include "compare_places.hpp"

namespace eats_places::utils::dedup {

namespace {

using eats_places::models::DeliverySlotAvailability;
using eats_places::models::DeliverySlotInfo;
using eats_places::models::DeliverySlots;
using eats_places::models::DeliveryType;
using eats_places::models::Place;
using eats_places::models::PlaceInfo;
using eats_places::resolve::CouriersType;
using eats_shared::Business;

template <typename... Apply>
PlaceInfo& Info(std::vector<PlaceInfo>& state, Apply... apply) {
  auto& info = state.emplace_back();
  (apply(info), ...);

  return info;
}

template <typename... Apply>
Place MakePlace(const PlaceInfo& info, Apply... apply) {
  Place result{info};
  (apply(result), ...);

  return result;
}

[[maybe_unused]] auto WithId(const int64_t id) {
  return
      [id](PlaceInfo& place) { place.id = eats_places::models::PlaceId(id); };
}

[[maybe_unused]] auto WithAvailable(const bool available) {
  return [available](Place& place) {
    place.delivery.info.is_available = available;
  };
}

[[maybe_unused]] auto WithPreparation(const unsigned int preparation) {
  return [preparation](Place& place) {
    place.timings.preparation = std::chrono::minutes(preparation);
  };
}

[[maybe_unused]] auto WithDeliveryDuration(const unsigned int duration) {
  return [duration](Place& place) {
    place.timings.delivery = std::chrono::minutes(duration);
  };
}

[[maybe_unused]] auto WithAverageRating(const double average_user_rating) {
  return [average_user_rating](PlaceInfo& place) {
    place.rating.value = average_user_rating;
  };
}

[[maybe_unused]] auto WithDeliveryType(DeliveryType delivery_type) {
  return [delivery_type](PlaceInfo& place) {
    place.delivery_type = delivery_type;
  };
}

[[maybe_unused]] auto WithCourierType(CouriersType courier_type) {
  return [courier_type](Place& place) { place.couriers_type = courier_type; };
}

[[maybe_unused]] auto WithBusiness(Business business) {
  return [business](PlaceInfo& place) { place.business = business; };
}

[[maybe_unused]] auto WithDistance(const double distance) {
  return [distance](Place& place) {
    place.distance = geometry::Distance::from_value(distance);
  };
}

[[maybe_unused]] auto WithTag(std::string&& tag) {
  return [place_tag = std::move(tag)](PlaceInfo& info) {
    info.tags.emplace(std::move(place_tag));
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
  std::vector<PlaceInfo> state;
  state.reserve(20);

  WORST(Available, MakePlace(Info(state), WithAvailable(true)),
        MakePlace(Info(state), WithAvailable(false)));
  BETTER(Available, MakePlace(Info(state), WithAvailable(false)),
         MakePlace(Info(state), WithAvailable(true)));
  EQUAL(Available, MakePlace(Info(state), WithAvailable(false)),
        MakePlace(Info(state), WithAvailable(false)));
  EQUAL(Available, MakePlace(Info(state), WithAvailable(true)),
        MakePlace(Info(state), WithAvailable(true)));
}

TEST(Compare, WithLessEta) {
  std::vector<PlaceInfo> state;
  state.reserve(20);

  WORST(WithLessEta, MakePlace(Info(state), WithDeliveryDuration(10)),
        MakePlace(Info(state), WithDeliveryDuration(20)));
  BETTER(WithLessEta, MakePlace(Info(state), WithDeliveryDuration(30)),
         MakePlace(Info(state), WithDeliveryDuration(10)));
  EQUAL(WithLessEta, MakePlace(Info(state), WithDeliveryDuration(15)),
        MakePlace(Info(state), WithDeliveryDuration(15)));
}

TEST(Compare, WithGreaterRating) {
  std::vector<PlaceInfo> state;
  state.reserve(20);

  WORST(WithGreaterRating, MakePlace(Info(state, WithAverageRating(4.25))),
        MakePlace(Info(state, WithAverageRating(4.24))));
  BETTER(WithGreaterRating, MakePlace(Info(state, WithAverageRating(3.1))),
         MakePlace(Info(state, WithAverageRating(5.0))));
  EQUAL(WithGreaterRating, MakePlace(Info(state, WithAverageRating(1.0000001))),
        MakePlace(Info(state, WithAverageRating(1.0000004))));
}

TEST(Compare, NativeNonAutoBetter) {
  std::vector<PlaceInfo> state;
  state.reserve(20);

  const auto native = WithDeliveryType(DeliveryType::kNative);
  const auto marketplace = WithDeliveryType(DeliveryType::kMarketplace);

  WORST(NativeNonAutoBetter,
        MakePlace(Info(state, native),
                  WithCourierType(CouriersType::kYandexRover)),
        MakePlace(Info(state, native),
                  WithCourierType(CouriersType::kYandexTaxi)));
  BETTER(
      NativeNonAutoBetter,
      MakePlace(Info(state, native), WithCourierType(CouriersType::kVehicle)),
      MakePlace(Info(state, native),
                WithCourierType(CouriersType::kPedestrian)));
  EQUAL(NativeNonAutoBetter,
        MakePlace(Info(state, native), WithCourierType(CouriersType::kVehicle)),
        MakePlace(Info(state, native),
                  WithCourierType(CouriersType::kYandexTaxi)));
  EQUAL(NativeNonAutoBetter,
        MakePlace(Info(state, native),
                  WithCourierType(CouriersType::kYandexTaxi)),
        MakePlace(Info(state, native),
                  WithCourierType(CouriersType::kYandexTaxi)));
  EQUAL(
      NativeNonAutoBetter,
      MakePlace(Info(state, native),
                WithCourierType(CouriersType::kPedestrian)),
      MakePlace(Info(state, native), WithCourierType(CouriersType::kBicycle)));
  EQUAL(
      NativeNonAutoBetter,
      MakePlace(Info(state, marketplace),
                WithCourierType(CouriersType::kPedestrian)),
      MakePlace(Info(state, native), WithCourierType(CouriersType::kVehicle)));
}

TEST(Compare, NativeWithLessDeliveryTimeComparator) {
  std::vector<PlaceInfo> state;
  state.reserve(20);

  const auto native = WithDeliveryType(DeliveryType::kNative);
  const auto marketplace = WithDeliveryType(DeliveryType::kMarketplace);

  WORST(NativeWithLessDeliveryTime,
        MakePlace(Info(state, native), WithDeliveryDuration(5)),
        MakePlace(Info(state, native), WithDeliveryDuration(10)));
  BETTER(NativeWithLessDeliveryTime,
         MakePlace(Info(state, native), WithDeliveryDuration(20)),
         MakePlace(Info(state, native), WithDeliveryDuration(2)));
  EQUAL(NativeWithLessDeliveryTime, MakePlace(Info(state, marketplace)),
        MakePlace(Info(state, marketplace)));
  EQUAL(NativeWithLessDeliveryTime,
        MakePlace(Info(state, native), WithDeliveryDuration(10)),
        MakePlace(Info(state, native), WithDeliveryDuration(10)));
  EQUAL(NativeWithLessDeliveryTime,
        MakePlace(Info(state, native), WithDeliveryDuration(10),
                  WithCourierType(CouriersType::kYandexTaxi)),
        MakePlace(Info(state, native), WithDeliveryDuration(10),
                  WithCourierType(CouriersType::kPedestrian)));
}

TEST(Compare, HasPriorityTagComparator) {
  std::vector<PlaceInfo> state;
  state.reserve(20);

  auto has_tag = HasPriorityTagComparator("better");

  EQUAL(has_tag,                                                   //
        MakePlace(Info(state, WithTag("better"))),                 // with_tag
        MakePlace(Info(state, WithTag("tag"), WithTag("better")))  // with_tag
  );

  EQUAL(has_tag,                                 //
        MakePlace(Info(state)),                  // no_tag
        MakePlace(Info(state, WithTag("tag2")))  // wrong_tag
  );
  WORST(has_tag,                                    //
        MakePlace(Info(state, WithTag("better"))),  // with_tag
        MakePlace(Info(state, WithTag("tag2")))     // wrong_tag
  );
  BETTER(has_tag,                                   //
         MakePlace(Info(state)),                    // no_tag
         MakePlace(Info(state, WithTag("better")))  // with_tag
  );
}

TEST(Compare, RetailComparator) {
  std::vector<PlaceInfo> state;
  state.reserve(20);

  const auto id_to_slot = std::make_optional(DeliverySlots{
      {
          eats_places::models::PlaceId(1),
          DeliverySlotInfo{
              DeliverySlotAvailability{
                  false,  // is_slot_available
                  true,   // is_asap_available
              },
              {},  // description
          },
      },
      {
          eats_places::models::PlaceId(2),
          DeliverySlotInfo{
              DeliverySlotAvailability{
                  true,   // is_slot_available
                  false,  // is_asap_available
              },
              {},  // description
          },
      },
      {
          eats_places::models::PlaceId(3),
          DeliverySlotInfo{
              DeliverySlotAvailability{
                  true,  // is_slot_available
                  true,  // is_asap_available
              },
              {},  // description
          },
      },
      {
          eats_places::models::PlaceId(4),
          DeliverySlotInfo{
              DeliverySlotAvailability{
                  false,  // is_slot_available
                  false,  // is_asap_available
              },
              {},  // description
          },
      },
      {
          eats_places::models::PlaceId(5),
          DeliverySlotInfo{
              DeliverySlotAvailability{
                  false,  // is_slot_available
                  false,  // is_asap_available
              },
              {},  // description
          },
      },
  });

  const auto shop = WithBusiness(Business::kShop);
  const auto restaurant = WithBusiness(Business::kRestaurant);

  const auto retail_cmp = RetailComparator(7000, id_to_slot);

  // Одинаковое расстояние, оба до трешхолда, 3 доступен ASAP = лучше
  BETTER(retail_cmp,  //
         MakePlace(Info(state, WithId(2), shop), WithDistance(5021)),
         MakePlace(Info(state, WithId(3), shop), WithDistance(5021)));
  // Разное расстояние, 1 за трешхолдом, 3 лучше
  WORST(retail_cmp,  //
        MakePlace(Info(state, WithId(3), shop), WithDistance(5021)),
        MakePlace(Info(state, WithId(1), shop), WithDistance(8129)));
  // Разное расстояние, оба до трешхолда, у обоих недоступен ASAP, выбираем
  // ближайший - 4
  BETTER(retail_cmp,  //
         MakePlace(Info(state, WithId(2), shop), WithDistance(5021)),
         MakePlace(Info(state, WithId(4), shop), WithDistance(2311)));
  // Разное расстояние, оба после трешхолда, у 1 доступен ASAP, но 5 ближе и
  // поэтому лучше
  BETTER(retail_cmp,  //
         MakePlace(Info(state, WithId(1), shop), WithDistance(8129)),
         MakePlace(Info(state, WithId(5), shop), WithDistance(7102)));

  EQUAL(retail_cmp,  //
        MakePlace(Info(state, WithId(3), restaurant), WithDistance(5021)),
        MakePlace(Info(state, WithId(1), restaurant), WithDistance(8129)));
  EQUAL(retail_cmp,  //
        MakePlace(Info(state, WithId(2), restaurant), WithDistance(5021)),
        MakePlace(Info(state, WithId(4), restaurant), WithDistance(2311)));
}

TEST(Compare, LessDistance) {
  std::vector<PlaceInfo> state;
  state.reserve(20);

  EQUAL(LessDistance,                                           //
        MakePlace(Info(state, WithId(2)), WithDistance(20.0)),  //
        MakePlace(Info(state, WithId(3)), WithDistance(20.0)));
  BETTER(LessDistance,                                           //
         MakePlace(Info(state, WithId(1)), WithDistance(12.2)),  //
         MakePlace(Info(state, WithId(5)), WithDistance(3.14)));
  WORST(LessDistance,                                           //
        MakePlace(Info(state, WithId(4)), WithDistance(80.5)),  //
        MakePlace(Info(state, WithId(5)), WithDistance(123.4)));
}

}  // namespace eats_places::utils::dedup
