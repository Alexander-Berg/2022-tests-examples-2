#include <gtest/gtest.h>

#include "models/eats/places_ranking/v1/ranker.hpp"

namespace ml {
namespace eats {
namespace places_ranking {
namespace v1 {

namespace {

class RankerResourcesImpl : public RankerResources {
 public:
  double GetLocationRadius() const override { return 1000.; }
  int GetMinOrderRating() const override { return 4; }
};

Ranker GetRanker() { return Ranker(std::make_shared<RankerResourcesImpl>()); }

class PlacesRankingModelV1Fixture : public testing::Test {
 public:
  PlacesRankingModelV1Fixture() = default;

  class PlacesManager {
   public:
    void RegisterPlace(Place& place) { place.id = ++generator_; }

   private:
    int generator_{0};
  };

  int AddPlace(PlacesManager& manager, std::vector<Place>& places, double eta,
               const utils::GeoPoint& point, double average_rating = 0.0,
               double rating = 0.0, bool is_available = true,
               const std::string& delivery_type = "native") const {
    Place place;
    place.eta_minutes = eta;
    place.average_user_rating = average_rating;
    place.location = point;
    place.rating = rating;
    place.delivery_type = delivery_type;
    place.is_available = is_available;
    manager.RegisterPlace(place);
    places.push_back(place);
    return place.id;
  }

  Order CreateOrder(int place_id, int rating, int hour,
                    const std::string& status,
                    const utils::GeoPoint& location) {
    Order order;

    order.place_id = place_id;
    order.feedback = OrderFeedback();
    order.feedback->rating = rating;
    order.status = status;
    order.delivery_location = location;
    order.created_at = "2018-01-01T0" + std::to_string(hour) + ":00:00";

    return order;
  }
};

}  // namespace

TEST_F(PlacesRankingModelV1Fixture, LocationAwareSortPlaces) {
  std::vector<Place> places;
  PlacesManager manager;

  int place1 = AddPlace(manager, places, 0, {0, 0}, 10);
  int place2 = AddPlace(manager, places, 0.999999, {0, 0}, 9);
  int place3 = AddPlace(manager, places, 1.000001, {0, 0}, 8.99999);
  int place4 = AddPlace(manager, places, 1.0, {0, 0}, 10);
  int place5 = AddPlace(manager, places, 1, {0, 0}, 11);
  int place6 = AddPlace(manager, places, 2, {0, 0}, 10);
  int place7 = AddPlace(manager, places, 2, {0, 0}, 10, 0, true, "marketplace");

  LocationAwareSortPlaces(places.begin(), places.end());

  ASSERT_EQ(places[0].id, place1);
  ASSERT_EQ(places[1].id, place5);
  ASSERT_EQ(places[2].id, place4);
  ASSERT_EQ(places[3].id, place3);
  ASSERT_EQ(places[4].id, place2);
  ASSERT_EQ(places[5].id, place6);
  ASSERT_EQ(places[6].id, place7);
}

TEST_F(PlacesRankingModelV1Fixture, OneOrderPerPlace) {
  std::vector<Order> orders;
  std::vector<Place> places;
  PlacesManager manager;

  int place1 = AddPlace(manager, places, 1, {0, 0}, 0);
  int place2 = AddPlace(manager, places, 2, {0, 0}, 0);
  int place3 = AddPlace(manager, places, 3, {0, 0}, 0);
  int place4 = AddPlace(manager, places, 4, {0, 0}, 0);
  int place5 = AddPlace(manager, places, 1, {0, 0}, 1);

  orders.push_back(
      CreateOrder(place1, 4, 0, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place2, 4, 1, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place3, 2, 2, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(CreateOrder(place4, 5, 3, "created", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place5, 5, 5, "delivered", utils::GeoPoint(10, 10)));

  RankerRequest request;
  request.location = utils::geometry::Point(0, 0);
  request.orders = orders;
  request.places = places;
  TimeStorage ts("");
  RankerResponse response = GetRanker().Apply(request, LogExtra(), ts);

  ASSERT_EQ(response.result.size(), places.size());
  ASSERT_EQ(response.result[0].id, place2);
  ASSERT_EQ(response.result[1].id, place1);
  ASSERT_EQ(response.result[2].id, place5);
  ASSERT_EQ(response.result[3].id, place3);
  ASSERT_EQ(response.result[4].id, place4);
}

TEST_F(PlacesRankingModelV1Fixture, MultipleOrdersPerPlace) {
  std::vector<Order> orders;
  std::vector<Place> places;
  PlacesManager manager;

  int place1 = AddPlace(manager, places, 3, {0, 0}, 1);
  int place2 = AddPlace(manager, places, 0, {0, 0}, 0);
  int place3 = AddPlace(manager, places, 0, {0, 0}, 0);
  int place4 = AddPlace(manager, places, 1, {0, 0}, 1);
  int place5 = AddPlace(manager, places, 1, {0, 0}, 1, 0, true, "marketplace");

  orders.push_back(
      CreateOrder(place1, 4, 0, "delivered", utils::GeoPoint(0, 0)));

  orders.push_back(
      CreateOrder(place2, 4, 1, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place2, 4, 2, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place2, 4, 5, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place2, 4, 6, "delivered", utils::GeoPoint(0, 0)));

  orders.push_back(
      CreateOrder(place3, 4, 3, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place3, 4, 4, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place3, 4, 5, "delivered", utils::GeoPoint(0, 0)));

  orders.push_back(CreateOrder(place4, 5, 3, "created", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place4, 5, 4, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place4, 5, 5, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(CreateOrder(place4, 5, 6, "created", utils::GeoPoint(0, 0)));

  orders.push_back(
      CreateOrder(place5, 5, 3, "delivered", utils::GeoPoint(10, 10)));
  orders.push_back(
      CreateOrder(place5, 5, 4, "delivered", utils::GeoPoint(10, 10)));
  orders.push_back(
      CreateOrder(place5, 5, 5, "delivered", utils::GeoPoint(10, 10)));
  orders.push_back(
      CreateOrder(place5, 5, 6, "delivered", utils::GeoPoint(10, 10)));

  RankerRequest request;
  request.location = utils::geometry::Point(0, 0);
  request.orders = orders;
  request.places = places;
  TimeStorage ts("");
  RankerResponse response = GetRanker().Apply(request, LogExtra(), ts);

  ASSERT_EQ(response.result.size(), places.size());
  ASSERT_EQ(response.result[0].id, place2);
  ASSERT_EQ(response.result[1].id, place3);
  ASSERT_EQ(response.result[2].id, place4);
  ASSERT_EQ(response.result[3].id, place5);
  ASSERT_EQ(response.result[4].id, place1);
}

TEST_F(PlacesRankingModelV1Fixture, RatingCheck) {
  std::vector<Order> orders;
  std::vector<Place> places;
  PlacesManager manager;

  int place1 = AddPlace(manager, places, 1, {0, 0}, 0);
  int place2 = AddPlace(manager, places, 10, {0, 0}, 1);
  int place3 = AddPlace(manager, places, 0, {0, 0}, 0);
  int place4 = AddPlace(manager, places, 11, {0, 0}, 1);
  int place5 = AddPlace(manager, places, 0, {0, 0}, 0);

  orders.push_back(
      CreateOrder(place2, 4, 1, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place2, 4, 2, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place2, 4, 5, "delivered", utils::GeoPoint(0, 0)));

  orders.push_back(
      CreateOrder(place3, 4, 3, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place3, 4, 4, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place3, 4, 6, "delivered", utils::GeoPoint(0, 0)));

  orders.push_back(
      CreateOrder(place4, 4, 3, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place4, 4, 4, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place4, 2, 7, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place4, 2, 5, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place4, 2, 8, "delivered", utils::GeoPoint(0, 0)));

  orders.push_back(
      CreateOrder(place5, 4, 1, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place5, 4, 1, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place5, 4, 1, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place5, 4, 7, "delivered", utils::GeoPoint(0, 0)));

  RankerRequest request;
  request.location = utils::geometry::Point(0, 0);
  request.orders = orders;
  request.places = places;
  TimeStorage ts("");
  RankerResponse response = GetRanker().Apply(request, LogExtra(), ts);

  ASSERT_EQ(response.result.size(), places.size());
  ASSERT_EQ(response.result[0].id, place5);
  ASSERT_EQ(response.result[1].id, place3);
  ASSERT_EQ(response.result[2].id, place1);
  ASSERT_EQ(response.result[3].id, place2);
  ASSERT_EQ(response.result[4].id, place4);
}

TEST_F(PlacesRankingModelV1Fixture, AvailabilityCheck) {
  std::vector<Order> orders;
  std::vector<Place> places;
  PlacesManager manager;

  int place1 = AddPlace(manager, places, 1, {0, 0}, 0);
  int place2 = AddPlace(manager, places, 10, {0, 0}, 1);
  int place3 = AddPlace(manager, places, 1000, {0, 0}, 0, 0, false);
  int place4 = AddPlace(manager, places, 11, {0, 0}, 1);
  int place5 = AddPlace(manager, places, 1001, {0, 0}, 0, 0, false);

  orders.push_back(
      CreateOrder(place2, 4, 1, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place2, 4, 2, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place2, 4, 5, "delivered", utils::GeoPoint(0, 0)));

  orders.push_back(
      CreateOrder(place3, 4, 3, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place3, 4, 4, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place3, 4, 6, "delivered", utils::GeoPoint(0, 0)));

  orders.push_back(
      CreateOrder(place4, 4, 3, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place4, 4, 4, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place4, 2, 7, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place4, 2, 5, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place4, 2, 8, "delivered", utils::GeoPoint(0, 0)));

  orders.push_back(
      CreateOrder(place5, 4, 1, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place5, 4, 1, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place5, 4, 1, "delivered", utils::GeoPoint(0, 0)));
  orders.push_back(
      CreateOrder(place5, 4, 7, "delivered", utils::GeoPoint(0, 0)));

  RankerRequest request;
  request.location = utils::geometry::Point(0, 0);
  request.orders = orders;
  request.places = places;
  TimeStorage ts("");
  RankerResponse response = GetRanker().Apply(request, LogExtra(), ts);

  ASSERT_EQ(response.result.size(), places.size());
  ASSERT_EQ(response.result[0].id, place1);
  ASSERT_EQ(response.result[1].id, place2);
  ASSERT_EQ(response.result[2].id, place4);
  ASSERT_EQ(response.result[3].id, place3);
  ASSERT_EQ(response.result[4].id, place5);
}

}  // namespace v1
}  // namespace places_ranking
}  // namespace eats
}  // namespace ml
