#include <eats-places/sort/sort_places.hpp>

#include <cassert>

#include <gtest/gtest.h>

#include <userver/utils/datetime.hpp>
#include <userver/utils/strong_typedef.hpp>

namespace eats_places::sort {
namespace {

using PlacesCache = std::vector<std::shared_ptr<models::PlaceInfo>>;

namespace place_maker {

using models::Business;
using models::DeliveryType;
using models::Money;
using models::PlaceId;
using models::PriceCategory;
using resolve::CouriersType;

using Available = utils::StrongTypedef<class AvailableTag, bool>;
using WillBeAvailableFrom =
    utils::StrongTypedef<class WillBeAvailableFromTag,
                         std::chrono::system_clock::time_point>;
using Rating = utils::StrongTypedef<class RatingTag, double>;
using RatingCount = utils::StrongTypedef<class RatingCountTag, int>;
using New = utils::StrongTypedef<class NewTag, bool>;

namespace impl {

void SetPlaceField(models::Place&, models::PlaceInfo& place_info,
                   const DeliveryType val) {
  place_info.delivery_type = val;
}

void SetPlaceField(models::Place&, models::PlaceInfo& place_info,
                   const PriceCategory val) {
  place_info.price_category = val;
}

void SetPlaceField(models::Place& place, models::PlaceInfo&,
                   const CouriersType val) {
  place.couriers_type = val;
}

void SetPlaceField(models::Place& place, models::PlaceInfo&,
                   const Available val) {
  place.delivery.info.is_available = val.GetUnderlying();
  place.pickup.info.is_available = val.GetUnderlying();
}

void SetPlaceField(models::Place& place, models::PlaceInfo&,
                   const WillBeAvailableFrom val) {
  place.delivery.info.from = val.GetUnderlying();
  place.pickup.info.from = val.GetUnderlying();
}

void SetPlaceField(models::Place&, models::PlaceInfo& place_info,
                   const Rating val) {
  place_info.rating.should_show = true;
  place_info.rating.value = val.GetUnderlying();
}

void SetPlaceField(models::Place&, models::PlaceInfo& place_info,
                   const RatingCount val) {
  place_info.rating.feedback_count = val.GetUnderlying();
}

void SetPlaceField(models::Place&, models::PlaceInfo& place_info,
                   const New val) {
  if (val.GetUnderlying()) {
    place_info.launched_at = utils::datetime::Now();
  }
}

void SetPlaceField(models::Place& place, models::PlaceInfo&,
                   const models::Timings& val) {
  place.timings = val;
  place.timings.estimated = models::CreateEstimatedTime(
      std::chrono::duration_cast<std::chrono::minutes>(val.delivery),
      val.offset);
}

void SetPlaceField(models::Place& place, models::PlaceInfo&,
                   const geometry::Distance distance) {
  place.distance = distance;
}

void SetPlaceField(models::Place&, models::PlaceInfo& place_info,
                   const Business business) {
  place_info.business = business;
}

void SetPlaceField(models::Place& place, models::PlaceInfo&,
                   const models::Place::OrderStats& order_stats) {
  place.order_stats = order_stats;
}

}  // namespace impl

models::Timings MakeStrictDeliveryTime(int delivery_time_minutes,
                                       int offset_minutes = 0) {
  models::Timings timings;
  timings.delivery = std::chrono::minutes{delivery_time_minutes};
  timings.offset = std::chrono::minutes{offset_minutes};
  return timings;
}

models::Timings MakeRestaurantDeliveryTime(int delivery_time_minutes,
                                           int offset_minutes = 0) {
  assert(delivery_time_minutes % 5 == 0);
  assert(std::min(delivery_time_minutes,
                  delivery_time_minutes + offset_minutes) >= 5);
  return MakeStrictDeliveryTime(delivery_time_minutes, offset_minutes);
}

template <typename T>
geometry::Distance MakeDistanceInMeters(T value) {
  return static_cast<double>(value) * ::boost::units::si::meters;
}

std::shared_ptr<PlacesCache> current_places_cache;

auto SetPlacesCacheInScope(const std::shared_ptr<PlacesCache>& places_cache) {
  current_places_cache = places_cache;

  struct PlacesCacheClearer {
    ~PlacesCacheClearer() { current_places_cache = nullptr; }
  };
  return PlacesCacheClearer{};
}

models::PlaceInfo& MakePlaceInfoInCurrentCache(const models::PlaceId id) {
  auto& place_info = *current_places_cache->emplace_back(
      std::make_shared<models::PlaceInfo>());
  place_info.id = id;
  return place_info;
}

template <typename... T>
models::Place MakePlace(const PlaceId id, T... args) {
  auto& place_info = MakePlaceInfoInCurrentCache(id);

  models::Place place{place_info};
  (impl::SetPlaceField(place, place_info, args), ...);
  return place;
}

models::Place MakeMarketplace(
    const PlaceId id,
    const std::optional<models::Money>& delivery_cost_opt = std::nullopt) {
  auto& place_info = MakePlaceInfoInCurrentCache(id);
  place_info.delivery_type = DeliveryType::kMarketplace;

  models::Place place{place_info};
  impl::SetPlaceField(place, place_info, Available{true});

  if (delivery_cost_opt.has_value()) {
    const auto& delivery_cost = delivery_cost_opt.value();
    auto& delivery_condition = place.delivery_conditions.emplace_back();
    delivery_condition.delivery_cost = delivery_cost;
    delivery_condition.order_price = delivery_cost;
  }

  return place;
}

std::vector<const models::Place*> Ptrs(
    const std::vector<models::Place>& places) {
  std::vector<const models::Place*> ptrs{};
  ptrs.reserve(places.size());

  for (const auto& place : places) {
    ptrs.push_back(&place);
  }

  return ptrs;
}

}  // namespace place_maker

struct PlacesSortTestCase {
  std::string name;
  std::shared_ptr<PlacesCache> places_cache;
  std::vector<models::Place> places;
  std::vector<size_t> expected;
  PlaceSortStrategy strategy = PlaceSortStrategy::kDefault;
  models::ShippingType shipping_type = models::ShippingType::kDelivery;
  bool shop_first = false;
  std::unordered_map<models::PlaceId, models::Money> delivery_price = {};

  std::string GetTestName() const {
    auto res = name;
    for (char& ch : res) {
      if (ch == ' ' || ch == ',') {
        ch = '_';
      }
    }
    return res;
  }
};

class GetSortedByContentPlacesIndexByIdMapTest
    : public testing::TestWithParam<PlacesSortTestCase> {};

TEST_P(GetSortedByContentPlacesIndexByIdMapTest, Test) {
  const auto& test_case = GetParam();

  const auto idx_by_id = GetSortedByContentPlacesIndexByIdMap(
      place_maker::Ptrs(test_case.places), test_case.strategy,
      test_case.shipping_type, test_case.shop_first, test_case.delivery_price);
  ASSERT_EQ(idx_by_id.size(), test_case.places.size());

  for (size_t sorted_place_idx = 0;
       sorted_place_idx < test_case.expected.size(); ++sorted_place_idx) {
    const auto& expected_place =
        test_case.places[test_case.expected[sorted_place_idx]];
    ASSERT_EQ(idx_by_id.at(expected_place.id), sorted_place_idx)
        << "expected place " << expected_place.id << " on position "
        << sorted_place_idx << ", actual position is "
        << idx_by_id.at(expected_place.id);
  }
}

std::vector<PlacesSortTestCase> MakeTestCases();

INSTANTIATE_TEST_SUITE_P(SortPlaces, GetSortedByContentPlacesIndexByIdMapTest,
                         testing::ValuesIn(MakeTestCases()),
                         [](const auto& param_info) {
                           return param_info.param.GetTestName();
                         });

std::vector<PlacesSortTestCase> MakeTestCases() {
  using namespace place_maker;
  using Places = std::vector<models::Place>;
  using Expected = std::vector<size_t>;

  const auto now = utils::datetime::Now();
  const auto in_sixty_minutes = now + std::chrono::hours{1};

  auto places_cache = std::make_shared<PlacesCache>();
  const auto scope_places_cache = SetPlacesCacheInScope(places_cache);

  return {
      {
          "empty",
          places_cache,
          Places{},
          Expected{},
      },
      {
          "available and unavailable",
          // В Go тут повторялись PlaceId
          places_cache,
          Places{MakePlace(PlaceId{1}, Available{false}),
                 MakePlace(PlaceId{2}, Available{true}),
                 MakePlace(PlaceId{3}, Available{true}),
                 MakePlace(PlaceId{4}, Available{false})},
          Expected{2, 1, 3, 0},
      },
      {
          "available and unavailable with shop first",
          places_cache,
          Places{
              MakePlace(PlaceId{1}, Available{false}, Business::kShop),
              MakePlace(PlaceId{2}, Available{true}, Business::kZapravki),
              MakePlace(PlaceId{3}, Available{true}, Business::kShop),
              MakePlace(PlaceId{4}, Available{false}, Business::kRestaurant)},
          Expected{2, 0, 1, 3},
          PlaceSortStrategy::kDefault,
          models::ShippingType::kDelivery,
          true,
      },
      // В Go тут был тест "sort" с разным Place.Order
      {
          "different group_dependent_section with shop first",
          places_cache,
          Places{
              MakePlace(PlaceId{5}, Available{true}, RatingCount{41}, Rating{3},
                        Business::kShop),
              MakePlace(PlaceId{1}, Available{true}, RatingCount{10}, Rating{3},
                        Business::kRestaurant),
          },
          Expected{0, 1},
          PlaceSortStrategy::kDefault,
          models::ShippingType::kDelivery,
          true,
      },
      {
          "different delivery_time",
          places_cache,
          Places{
              MakePlace(PlaceId{5}, Available{true}, RatingCount{41}, Rating{5},
                        MakeStrictDeliveryTime(30)),
              MakePlace(PlaceId{1}, Available{true}, RatingCount{41}, Rating{5},
                        MakeStrictDeliveryTime(20)),
              MakePlace(PlaceId{3}, Available{true}, RatingCount{41}, Rating{5},
                        MakeStrictDeliveryTime(40), Business::kShop),
          },
          Expected{1, 0, 2},
      },
      {
          "different delivery_time with shop first",
          places_cache,
          Places{
              MakePlace(PlaceId{5}, Available{true}, RatingCount{41}, Rating{5},
                        MakeStrictDeliveryTime(30)),
              MakePlace(PlaceId{1}, Available{true}, RatingCount{41}, Rating{5},
                        MakeStrictDeliveryTime(20)),
              MakePlace(PlaceId{3}, Available{true}, RatingCount{41}, Rating{5},
                        MakeStrictDeliveryTime(40), Business::kShop),
          },
          Expected{2, 1, 0},
          PlaceSortStrategy::kDefault,
          models::ShippingType::kDelivery,
          true,
      },
      {
          "different rating_dependent_group with shop first",
          places_cache,
          Places{
              MakePlace(PlaceId{5}, Available{true}, New{true},
                        MakeStrictDeliveryTime(30)),
              MakePlace(PlaceId{1}, Available{true}, RatingCount{10}, Rating{5},
                        MakeStrictDeliveryTime(30), Business::kShop),
              MakePlace(PlaceId{3}, Available{true}, RatingCount{41}, Rating{5},
                        MakeStrictDeliveryTime(30)),
          },
          Expected{1, 2, 0},
          PlaceSortStrategy::kDefault,
          models::ShippingType::kDelivery,
          true,
      },
      {
          "different group_dependent_rating",
          places_cache,
          Places{
              MakePlace(PlaceId{3}, Available{true}, Rating{4.33},
                        RatingCount{41}, MakeStrictDeliveryTime(30)),
              MakePlace(PlaceId{1}, Available{true}, Rating{4.78},
                        RatingCount{41}, MakeStrictDeliveryTime(30)),
          },
          Expected{1, 0},
      },
      {
          "different real_time",
          places_cache,
          Places{
              MakePlace(PlaceId{3}, Available{true}, Rating{4.33},
                        RatingCount{10}, MakeStrictDeliveryTime(29, 1)),
              MakePlace(PlaceId{1}, Available{true}, Rating{4.78},
                        RatingCount{10}, MakeStrictDeliveryTime(28, 2)),
          },
          Expected{1, 0},
      },
      // В Go тут был тест "different cancel_rate" с разным Place.CancelRate
      {
          "different place_id",
          places_cache,
          Places{
              MakePlace(PlaceId{2}, Available{true}, DeliveryType::kNative,
                        New{true}, MakeStrictDeliveryTime(29, 1)),
              MakePlace(PlaceId{5}, Available{true}, DeliveryType::kNative,
                        New{true}, MakeStrictDeliveryTime(29, 1)),
          },
          Expected{1, 0},
      },
      // В Go тут был тест "unavailable by sort desc" с разным Place.Order
      {
          "unavailable available_from asc, different from",
          places_cache,
          Places{
              MakePlace(PlaceId{2}, WillBeAvailableFrom(in_sixty_minutes)),
              MakePlace(PlaceId{3}, WillBeAvailableFrom(now)),
              MakePlace(PlaceId{1}, WillBeAvailableFrom(now)),
          },
          Expected{1, 2, 0},
      },
      {
          "unavailable available_from asc, different from, different "
          "delivery_time",
          places_cache,
          Places{
              MakePlace(PlaceId{2}, WillBeAvailableFrom(now),
                        MakeStrictDeliveryTime(90)),
              MakePlace(PlaceId{3}, WillBeAvailableFrom(in_sixty_minutes)),
          },
          Expected{1, 0},
      },
      {
          "unavailable available_from asc, eq from, different delivery_time",
          places_cache,
          Places{
              MakePlace(PlaceId{2}, WillBeAvailableFrom(now),
                        MakeStrictDeliveryTime(40)),
              MakePlace(PlaceId{3}, WillBeAvailableFrom(now)),
          },
          Expected{1, 0},
      },
      {
          "unavailable avg_rating desc",
          places_cache,
          Places{
              MakePlace(PlaceId{2}, Available{false}, Rating{4.5}),
              MakePlace(PlaceId{3}, Available{false}, Rating{5}),
          },
          Expected{1, 0},
      },
      {
          "unavailable new desc",
          places_cache,
          Places{
              MakePlace(PlaceId{2}, Available{false}, New{false}),
              MakePlace(PlaceId{3}, Available{false}, New{true}),
          },
          Expected{1, 0},
      },
      // В Go тут был тест "unavailable cancel_rate asc" с разным
      // Place.CancelRate
      {
          "unavailable type desc",
          places_cache,
          Places{
              MakePlace(PlaceId{2}, Available{false},
                        DeliveryType::kMarketplace),
              MakePlace(PlaceId{3}, Available{false}, DeliveryType::kNative),
          },
          Expected{1, 0},
      },
      {
          "unavailable place_id desc",
          places_cache,
          Places{
              MakePlace(PlaceId{2}, Available{false}),
              MakePlace(PlaceId{3}, Available{false}),
              MakePlace(PlaceId{1}, Available{false}),
          },
          Expected{1, 0, 2},
      },
      {
          "as fallback by order stat",
          places_cache,
          Places{
              MakePlace(PlaceId{2}, models::Place::OrderStats{20}),
              MakePlace(PlaceId{1}),
              MakePlace(PlaceId{3},
                        models::Place::OrderStats{20, utils::datetime::Now(),
                                                  utils::datetime::Now()}),
          },
          Expected{2, 0, 1},
          PlaceSortStrategy::kDefault,
          models::ShippingType::kDelivery,
          false,
          {},
      },
      {
          "as fallback by rating stat",
          places_cache,
          Places{
              MakePlace(PlaceId{2}, Rating{1.3}),
              MakePlace(PlaceId{1}, Rating{2.3}),
              MakePlace(PlaceId{3}, Rating{5.2}),
          },
          Expected{2, 1, 0},
          PlaceSortStrategy::kDefault,
          models::ShippingType::kDelivery,
          false,
          {},
      },
      {
          "fast delivery sort by ID",
          // В Go тут был Order = 10 и CancelRate = 10
          places_cache,
          Places{MakePlace(PlaceId{1}, Rating{4.8}, DeliveryType::kNative,
                           MakeRestaurantDeliveryTime(20)),
                 MakePlace(PlaceId{2}, Rating{4.8}, DeliveryType::kNative,
                           MakeRestaurantDeliveryTime(20)),
                 MakePlace(PlaceId{3}, Rating{4.8}, DeliveryType::kNative,
                           MakeRestaurantDeliveryTime(20)),
                 MakePlace(PlaceId{4}, Rating{4.8}, DeliveryType::kNative,
                           MakeRestaurantDeliveryTime(20))},
          Expected{3, 2, 1, 0},
          PlaceSortStrategy::kFastDelivery,
      },
      {
          "fast delivery sort by min time",
          places_cache,
          Places{
              MakePlace(PlaceId{3}, MakeRestaurantDeliveryTime(20),
                        Business::kShop),
              MakePlace(PlaceId{1}, MakeRestaurantDeliveryTime(10)),
              MakePlace(PlaceId{2}, MakeRestaurantDeliveryTime(15),
                        Business::kShop),
              MakePlace(PlaceId{4}, MakeRestaurantDeliveryTime(25)),
          },
          Expected{1, 2, 0, 3},
          PlaceSortStrategy::kFastDelivery,
      },
      {
          "fast delivery sort by min time with shop first",
          places_cache,
          Places{
              MakePlace(PlaceId{3}, MakeRestaurantDeliveryTime(20),
                        Business::kShop),
              MakePlace(PlaceId{1}, MakeRestaurantDeliveryTime(10)),
              MakePlace(PlaceId{2}, MakeRestaurantDeliveryTime(15),
                        Business::kShop),
              MakePlace(PlaceId{4}, MakeRestaurantDeliveryTime(25)),
          },
          Expected{2, 0, 1, 3},
          PlaceSortStrategy::kFastDelivery,
          models::ShippingType::kDelivery,
          true,
      },
      {
          "fast delivery sort by min time with offset",
          places_cache,
          Places{
              MakePlace(PlaceId{3}, MakeRestaurantDeliveryTime(20, 5)),
              MakePlace(PlaceId{1}, MakeRestaurantDeliveryTime(10, 5)),
              MakePlace(PlaceId{2}, MakeRestaurantDeliveryTime(15, 5)),
              MakePlace(PlaceId{4}, MakeRestaurantDeliveryTime(25, 5)),
          },
          Expected{1, 2, 0, 3},
          PlaceSortStrategy::kFastDelivery,
      },
      {
          "high rating sort by rating and delivery type",
          // В Go тест назывался "high rating sort by rating and order" и было 4
          // Place с одним Rating разными Order
          places_cache,
          Places{
              MakePlace(PlaceId{1}, Rating{10}),
              MakePlace(PlaceId{2}, Rating{9}),
              MakePlace(PlaceId{3}, Rating{8}),
              MakePlace(PlaceId{4}, Rating{11}),
              MakePlace(PlaceId{5}, Rating{5}, DeliveryType::kMarketplace),
              MakePlace(PlaceId{6}, Rating{5}, DeliveryType::kNative),
          },
          Expected{3, 0, 1, 2, 5, 4},
          PlaceSortStrategy::kHighRating,
      },
      {
          "high rating sort by time",
          places_cache,
          Places{
              MakePlace(PlaceId{1}, Rating{10}, MakeRestaurantDeliveryTime(25)),
              MakePlace(PlaceId{2}, Rating{10}, MakeRestaurantDeliveryTime(20)),
          },
          Expected{1, 0},
          PlaceSortStrategy::kHighRating,
      },
      // В Go тут был тест "high rating sort by deliveryType and cancelrate" с
      // разным Place.CancelRate
      {
          "cheap first sort by price category",
          // В Go тут был Order вместо Rating
          places_cache,
          Places{
              MakePlace(PlaceId{1}, PriceCategory{17, "", 1}, Rating{15}),
              MakePlace(PlaceId{2}, PriceCategory{64, "", 2}, Rating{10}),
              MakePlace(PlaceId{3}, PriceCategory{88, "", 3}, Rating{10},
                        Business ::kShop),
              MakePlace(PlaceId{4}, PriceCategory{12, "", 2}, Rating{5}),
              MakePlace(PlaceId{5}, PriceCategory{30, "", 3}, Rating{5},
                        Business::kShop),
          },
          Expected{0, 1, 3, 2, 4},
          PlaceSortStrategy::kCheapFirst,
      },
      {
          "cheap first sort by price category with shop first",
          // В Go тут был Order вместо Rating
          places_cache,
          Places{
              MakePlace(PlaceId{1}, PriceCategory{17, "", 1}, Rating{15}),
              MakePlace(PlaceId{2}, PriceCategory{64, "", 2}, Rating{10}),
              MakePlace(PlaceId{3}, PriceCategory{88, "", 3}, Rating{10},
                        Business::kShop),
              MakePlace(PlaceId{4}, PriceCategory{12, "", 2}, Rating{5}),
              MakePlace(PlaceId{5}, PriceCategory{30, "", 3}, Rating{5},
                        Business::kShop),
          },
          Expected{2, 4, 0, 1, 3},
          PlaceSortStrategy::kCheapFirst,
          models::ShippingType::kDelivery,
          true,
      },
      {
          "expensive first sort by price category",
          // В Go тут был Order вместо Rating
          places_cache,
          Places{
              MakePlace(PlaceId{1}, PriceCategory{21, "", 1}, Rating{10},
                        Business::kShop),
              MakePlace(PlaceId{2}, PriceCategory{42, "", 2}, Rating{10}),
              MakePlace(PlaceId{3}, PriceCategory{49, "", 3}, Rating{10}),
              MakePlace(PlaceId{4}, PriceCategory{19, "", 2}, Rating{5}),
              MakePlace(PlaceId{6}, PriceCategory{74, "", 1}, Rating{5},
                        Business::kShop),
              MakePlace(PlaceId{5}, PriceCategory{55, "", 3}, Rating{5}),
              MakePlace(PlaceId{7}, PriceCategory{13, "", 1}, Rating{15}),
          },
          Expected{2, 5, 1, 3, 6, 0, 4},
          PlaceSortStrategy::kExpensiveFirst,
      },
      {
          "expensive first sort by price category with shop first",
          places_cache,
          Places{
              MakePlace(PlaceId{1}, PriceCategory{21, "", 1}, Rating{10},
                        Business::kShop),
              MakePlace(PlaceId{2}, PriceCategory{42, "", 2}, Rating{10}),
              MakePlace(PlaceId{3}, PriceCategory{49, "", 3}, Rating{10}),
              MakePlace(PlaceId{4}, PriceCategory{19, "", 2}, Rating{5}),
              MakePlace(PlaceId{6}, PriceCategory{74, "", 1}, Rating{5},
                        Business::kShop),
              MakePlace(PlaceId{5}, PriceCategory{55, "", 3}, Rating{5}),
              MakePlace(PlaceId{7}, PriceCategory{13, "", 1}, Rating{15}),
          },
          Expected{0, 4, 2, 5, 1, 3, 6},
          PlaceSortStrategy::kExpensiveFirst,
          models::ShippingType::kDelivery,
          true,
      },
      {
          "expensive first sort by availability",
          places_cache,
          Places{
              MakePlace(PlaceId{1}, Available{true}, PriceCategory{2}),
              MakePlace(PlaceId{2}, PriceCategory{1}),
          },
          Expected{0, 1},
          PlaceSortStrategy::kExpensiveFirst,
      },
      {
          "courier type taxi vs marketplace vs native pedstrian",
          places_cache,
          Places{
              MakePlace(PlaceId{2}, DeliveryType::kMarketplace,
                        CouriersType::kPedestrian, Business::kShop),
              MakePlace(PlaceId{3}, DeliveryType::kNative,
                        CouriersType::kPedestrian, Business::kRestaurant),
              MakePlace(PlaceId{1}, DeliveryType::kNative,
                        CouriersType::kYandexTaxi, Business::kShop),
          },
          Expected{1, 2, 0},
          PlaceSortStrategy::kDefault,
      },
      {
          "courier type taxi vs marketplace vs native pedstrian with shop "
          "first",
          places_cache,
          Places{
              MakePlace(PlaceId{2}, DeliveryType::kMarketplace,
                        CouriersType::kPedestrian, Business::kShop),
              MakePlace(PlaceId{3}, DeliveryType::kNative,
                        CouriersType::kPedestrian, Business::kRestaurant),
              MakePlace(PlaceId{1}, DeliveryType::kNative,
                        CouriersType::kYandexTaxi, Business::kShop),
          },
          Expected{2, 0, 1},
          PlaceSortStrategy::kDefault,
          models::ShippingType::kDelivery,
          true,
      },
      {
          "courier type taxi vs marketplace",
          places_cache,
          Places{
              MakePlace(PlaceId{2}, DeliveryType::kMarketplace,
                        CouriersType::kPedestrian, MakeStrictDeliveryTime(20)),
              MakePlace(PlaceId{1}, DeliveryType::kNative,
                        CouriersType::kYandexTaxi, MakeStrictDeliveryTime(20)),
          },
          Expected{1, 0},
          PlaceSortStrategy::kDefault,
          models::ShippingType::kDelivery,
      },
      {
          "pickup sort available",
          places_cache,
          Places{
              MakePlace(PlaceId{1}, Available{true},
                        MakeDistanceInMeters(1000)),
              MakePlace(PlaceId{2}, Available{true}, MakeDistanceInMeters(500)),
              MakePlace(PlaceId{3}, Available{true}, MakeDistanceInMeters(300)),
          },
          Expected{2, 1, 0},
          PlaceSortStrategy::kDefault,
          models::ShippingType::kPickup,
      },
      {
          "pickup sort unavailable",
          places_cache,
          Places{
              MakePlace(PlaceId{1}, Available{false},
                        MakeDistanceInMeters(1000)),
              MakePlace(PlaceId{2}, Available{false},
                        MakeDistanceInMeters(500)),
              MakePlace(PlaceId{3}, Available{false},
                        MakeDistanceInMeters(300)),
          },
          Expected{2, 1, 0},
          PlaceSortStrategy::kDefault,
          models::ShippingType::kPickup,
      },
      {
          "pickup sort available vs unavailble",
          places_cache,
          Places{
              MakePlace(PlaceId{1}, Available{true},
                        MakeDistanceInMeters(1000)),
              MakePlace(PlaceId{2}, Available{true}, MakeDistanceInMeters(500)),
              MakePlace(PlaceId{3}, Available{false},
                        MakeDistanceInMeters(300)),
          },
          Expected{1, 0, 2},
          PlaceSortStrategy::kDefault,
          models::ShippingType::kPickup,
      },
      {
          "pickup sort available vs unavailble vs place id",
          places_cache,
          Places{
              MakePlace(PlaceId{1}, Available{true},
                        MakeDistanceInMeters(1000)),
              MakePlace(PlaceId{2}, Available{true}, MakeDistanceInMeters(500)),
              MakePlace(PlaceId{3}, Available{true}, MakeDistanceInMeters(500)),
              MakePlace(PlaceId{4}, Available{false}, MakeDistanceInMeters(50)),
              MakePlace(PlaceId{5}, Available{false},
                        MakeDistanceInMeters(300)),
          },
          Expected{2, 1, 0, 3, 4},
          PlaceSortStrategy::kDefault,
          models::ShippingType::kPickup,
      },
      {
          "pickup sort available vs unavailble vs place id with shop first",
          places_cache,
          Places{
              MakePlace(PlaceId{1}, Available{true},
                        MakeDistanceInMeters(1000)),
              MakePlace(PlaceId{2}, Available{true}, MakeDistanceInMeters(500)),
              MakePlace(PlaceId{3}, Available{true}, MakeDistanceInMeters(500)),
              MakePlace(PlaceId{4}, Available{false}, MakeDistanceInMeters(50)),
              MakePlace(PlaceId{5}, Available{false},
                        MakeDistanceInMeters(300)),
          },
          Expected{2, 1, 0, 3, 4},
          PlaceSortStrategy::kDefault,
          models::ShippingType::kPickup,
          true,
      },
      {"sort by dellivery price",
       places_cache,
       Places{
           MakePlace(PlaceId{1}, Available{true}),
           MakePlace(PlaceId{2}, Available{true}),
           MakePlace(PlaceId{3}, Available{true}),
           MakePlace(PlaceId{4}, Available{true}),
           MakePlace(PlaceId{5}, Available{true}),
       },
       Expected{4, 3, 2, 1, 0},
       PlaceSortStrategy::kCheapDelivery,
       models::ShippingType::kDelivery,
       true,
       {
           {PlaceId{1}, models::Money{500}},
           {PlaceId{2}, models::Money{400}},
           {PlaceId{3}, models::Money{300}},
           {PlaceId{4}, models::Money{200}},
           {PlaceId{5}, models::Money{100}},
       }},
      {"sort by dellivery price, unavailable down",
       places_cache,
       Places{
           MakePlace(PlaceId{1}, Available{true}),
           MakePlace(PlaceId{2}, Available{true}),
           MakePlace(PlaceId{3}, Available{false}),
       },
       Expected{1, 0, 2},
       PlaceSortStrategy::kCheapDelivery,
       models::ShippingType::kDelivery,
       true,
       {
           {PlaceId{1}, models::Money{500}},
           {PlaceId{2}, models::Money{400}},
           {PlaceId{3}, models::Money{300}},
       }},
      {"sort by dellivery price, unknow price down",
       places_cache,
       Places{
           MakePlace(PlaceId{1}, Available{true}),
           MakePlace(PlaceId{2}, Available{true}),
           MakePlace(PlaceId{3}, Available{true}),
       },
       Expected{1, 0, 2},
       PlaceSortStrategy::kCheapDelivery,
       models::ShippingType::kDelivery,
       true,
       {
           {PlaceId{1}, models::Money{500}},
           {PlaceId{2}, models::Money{400}},
       }},
      {"sort by dellivery price, with marketplace",
       places_cache,
       Places{
           MakePlace(PlaceId{1}, Available{true}),
           MakeMarketplace(PlaceId{2}, models::Money{400}),
           MakePlace(PlaceId{3}, Available{true}),
       },
       Expected{2, 1, 0},
       PlaceSortStrategy::kCheapDelivery,
       models::ShippingType::kDelivery,
       true,
       {
           {PlaceId{1}, models::Money{500}},
           {PlaceId{3}, models::Money{300}},
       }},
      {"sort by dellivery price, free marketplace delivery",
       places_cache,
       Places{
           MakePlace(PlaceId{1}, Available{true}),
           MakeMarketplace(PlaceId{2}),
           MakePlace(PlaceId{3}, Available{true}),
       },
       Expected{1, 2, 0},
       PlaceSortStrategy::kCheapDelivery,
       models::ShippingType::kDelivery,
       true,
       {
           {PlaceId{1}, models::Money{500}},
           {PlaceId{3}, models::Money{300}},
       }},
  };
}

TEST(SortPlacesUsingIndexByIdMap, Test) {
  using models::Place;
  using models::PlaceId;
  using models::PlaceInfo;

  const std::vector<size_t> permutation = {4, 2, 0, 1, 3};

  const size_t n_places = permutation.size();
  std::vector<PlaceInfo> place_infos;
  // reserve нужен, чтобы ссылки на PlaceInfo не инвалидировались
  place_infos.reserve(n_places);
  std::vector<Place> places;
  std::vector<const Place*> place_ptrs;
  places.reserve(n_places);
  for (size_t place_idx = 0; place_idx < n_places; ++place_idx) {
    auto& place_info = place_infos.emplace_back();
    place_info.id = PlaceId(place_idx + 1);
    auto& place = places.emplace_back(place_info);

    place_ptrs.push_back(&place);
  }

  Index idx_by_id;
  for (size_t sorted_place_idx = 0; sorted_place_idx < n_places;
       ++sorted_place_idx) {
    idx_by_id[places[permutation[sorted_place_idx]].id] = sorted_place_idx;
  }

  SortPlacesByIndex(place_ptrs.begin(), place_ptrs.end(), idx_by_id);
  for (size_t sorted_place_idx = 0; sorted_place_idx < n_places;
       ++sorted_place_idx) {
    ASSERT_EQ(place_ptrs[sorted_place_idx],
              &places[permutation[sorted_place_idx]]);
  }
}

}  // namespace
}  // namespace eats_places::sort
