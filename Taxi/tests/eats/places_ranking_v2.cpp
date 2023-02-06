#include <gtest/gtest.h>

#include <boost/any.hpp>
#include <unordered_map>

#include <common/stats.hpp>
#include "models/eats/places_ranking/v2/ranker.hpp"

namespace ml {
namespace eats {
namespace places_ranking {
namespace v2 {

using utils::GeoPoint;

namespace {

class RankerResourcesImpl : public RankerResources {
 public:
  double GetLocationRadius() const override { return 1000.; }
  int GetMinOrderRating() const override { return 4; }
  unsigned GetDefaultRankingWeight() const override { return 100; }
  unsigned GetMinRatingsCount() const override { return 40; }
  double GetUserRatingThreshold() const override { return 4.0; }
};

const std::string kNativeDelivery = "native";
const std::string kMarketplaceDelivery = "marketplace";

const std::string kDeliveredStatus = "delivered";
const std::string kCreatedStatus = "created";

Ranker GetRanker() { return Ranker(std::make_shared<RankerResourcesImpl>()); }

class PlacesRankingModelV2Fixture : public testing::Test {
 public:
  PlacesRankingModelV2Fixture() = default;

  int AddPlace(
      std::vector<Place>& places,
      const std::unordered_map<std::string, boost::any>& params) const {
    using ml::common::MapGetDef;
    auto place_id = static_cast<int>(places.size());
    Place place;
    place.id = place_id;
    place.ranking_weight =
        boost::any_cast<unsigned>(MapGetDef(params, "ranking_weight", 100u));
    place.eta_minutes_min =
        boost::any_cast<unsigned>(MapGetDef(params, "eta_minutes_min", 30u));
    place.eta_minutes_max = boost::any_cast<unsigned>(
        MapGetDef(params, "eta_minutes_max", place.eta_minutes_min));
    place.cancel_rate =
        boost::any_cast<double>(MapGetDef(params, "cancel_rate", 0.0));
    place.is_new = boost::any_cast<bool>(MapGetDef(params, "is_new", false));
    place.rating = boost::any_cast<double>(MapGetDef(params, "rating", 1.0));
    place.average_user_rating =
        boost::any_cast<double>(MapGetDef(params, "average_user_rating", 1.0));
    place.user_ratings_count = boost::any_cast<unsigned>(
        MapGetDef(params, "user_ratings_count", 100u));
    ;
    place.location = boost::any_cast<GeoPoint>(
        MapGetDef(params, "location", GeoPoint{0, 0}));
    place.delivery_type = boost::any_cast<std::string>(
        MapGetDef(params, "delivery_type", kNativeDelivery));
    place.is_available =
        boost::any_cast<bool>(MapGetDef(params, "is_available", true));
    places.push_back(std::move(place));
    return place_id;
  }

  int AddOrder(
      std::vector<Order>& orders,
      const std::unordered_map<std::string, boost::any>& params) const {
    auto order_id = static_cast<int>(orders.size());
    Order order;
    order.id = order_id;
    order.place_id = boost::any_cast<int>(params.at("place_id"));
    order.feedback = OrderFeedback();
    if (params.count("rating")) {
      order.feedback->rating = boost::any_cast<int>(params.at("rating"));
    }
    order.status = boost::any_cast<std::string>(params.at("status"));
    order.delivery_location =
        boost::any_cast<GeoPoint>(params.at("delivery_location"));
    if (params.count("hour")) {
      order.created_at =
          "2018-01-01T0" +
          std::to_string(boost::any_cast<int>(params.at("hour"))) + ":00:00";
    } else {
      order.created_at = boost::any_cast<std::string>(params.at("created_at"));
    }
    orders.push_back(std::move(order));
    return order_id;
  }
};

}  // namespace

TEST_F(PlacesRankingModelV2Fixture, LocationAwareSortPlaces) {
  std::vector<Place> places;

  int place1 = AddPlace(places, {{"eta_minutes_min", 20u},
                                 {"eta_minutes_max", 25u},
                                 {"average_user_rating", 4.9},
                                 {"user_ratings_count", 100u},
                                 {"cancel_rate", 0.01},
                                 {"delivery_type", kNativeDelivery},
                                 {"is_new", false}});

  int place2 = AddPlace(places, {{"eta_minutes_min", 20u},
                                 {"eta_minutes_max", 25u},
                                 {"average_user_rating", 4.8},
                                 {"user_ratings_count", 100u},
                                 {"cancel_rate", 0.05},
                                 {"delivery_type", kNativeDelivery},
                                 {"is_new", false}});

  int place3 = AddPlace(places, {{"eta_minutes_min", 20u},
                                 {"eta_minutes_max", 25u},
                                 {"average_user_rating", 4.8},
                                 {"user_ratings_count", 100u},
                                 {"cancel_rate", 0.08},
                                 {"delivery_type", kMarketplaceDelivery},
                                 {"is_new", false}});

  int place4 = AddPlace(places, {{"eta_minutes_min", 15u},
                                 {"eta_minutes_max", 20u},
                                 {"average_user_rating", 4.5},
                                 {"user_ratings_count", 100u},
                                 {"cancel_rate", 0.11},
                                 {"delivery_type", kNativeDelivery},
                                 {"is_new", false}});

  int place5 = AddPlace(places, {{"eta_minutes_min", 15u},
                                 {"eta_minutes_max", 20u},
                                 {"average_user_rating", 4.5},
                                 {"user_ratings_count", 100u},
                                 {"cancel_rate", 0.11},
                                 {"delivery_type", kMarketplaceDelivery},
                                 {"is_new", false}});

  int place6 = AddPlace(places, {{"eta_minutes_min", 15u},
                                 {"eta_minutes_max", 20u},
                                 {"average_user_rating", 3.8},
                                 {"user_ratings_count", 100u},
                                 {"cancel_rate", 0.05},
                                 {"delivery_type", kNativeDelivery},
                                 {"is_new", false}});

  int place7 = AddPlace(places, {{"eta_minutes_min", 15u},
                                 {"eta_minutes_max", 20u},
                                 {"average_user_rating", 3.6},
                                 {"user_ratings_count", 100u},
                                 {"cancel_rate", 0.20},
                                 {"delivery_type", kMarketplaceDelivery},
                                 {"is_new", false}});

  int place8 = AddPlace(places, {{"eta_minutes_min", 15u},
                                 {"eta_minutes_max", 20u},
                                 {"average_user_rating", 0.0},
                                 {"user_ratings_count", 100u},
                                 {"cancel_rate", 0.0},
                                 {"delivery_type", kNativeDelivery},
                                 {"is_new", true}});

  int place9 = AddPlace(places, {{"eta_minutes_min", 20u},
                                 {"eta_minutes_max", 25u},
                                 {"average_user_rating", 5.0},
                                 {"user_ratings_count", 10u},
                                 {"cancel_rate", 0.0},
                                 {"delivery_type", kNativeDelivery},
                                 {"is_new", false}});

  int place10 = AddPlace(places, {{"eta_minutes_min", 20u},
                                  {"eta_minutes_max", 25u},
                                  {"average_user_rating", 4.9},
                                  {"user_ratings_count", 100u},
                                  {"cancel_rate", 0.05},
                                  {"delivery_type", kMarketplaceDelivery},
                                  {"is_new", false}});

  int place11 = AddPlace(places, {{"eta_minutes_min", 15u},
                                  {"eta_minutes_max", 20u},
                                  {"average_user_rating", 4.9},
                                  {"user_ratings_count", 100u},
                                  {"cancel_rate", 0.07},
                                  {"delivery_type", kNativeDelivery},
                                  {"is_new", false}});

  int place12 = AddPlace(places, {{"eta_minutes_min", 20u},
                                  {"eta_minutes_max", 25u},
                                  {"average_user_rating", 4.6},
                                  {"user_ratings_count", 100u},
                                  {"cancel_rate", 0.05},
                                  {"delivery_type", kNativeDelivery},
                                  {"is_new", false}});

  int place13 = AddPlace(places, {{"eta_minutes_min", 20u},
                                  {"eta_minutes_max", 25u},
                                  {"average_user_rating", 4.6},
                                  {"user_ratings_count", 100u},
                                  {"cancel_rate", 0.05},
                                  {"delivery_type", kMarketplaceDelivery},
                                  {"is_new", false}});

  int place14 = AddPlace(places, {{"eta_minutes_min", 20u},
                                  {"eta_minutes_max", 25u},
                                  {"average_user_rating", 3.7},
                                  {"user_ratings_count", 100u},
                                  {"cancel_rate", 0.03},
                                  {"delivery_type", kMarketplaceDelivery},
                                  {"is_new", false}});

  int place15 = AddPlace(places, {{"eta_minutes_min", 20u},
                                  {"eta_minutes_max", 25u},
                                  {"average_user_rating", 3.7},
                                  {"user_ratings_count", 100u},
                                  {"cancel_rate", 0.11},
                                  {"delivery_type", kNativeDelivery},
                                  {"is_new", false}});

  int place16 = AddPlace(places, {{"eta_minutes_min", 15u},
                                  {"eta_minutes_max", 20u},
                                  {"average_user_rating", 0.0},
                                  {"user_ratings_count", 100u},
                                  {"cancel_rate", 0.02},
                                  {"delivery_type", kNativeDelivery},
                                  {"is_new", true}});

  int place17 = AddPlace(places, {{"eta_minutes_min", 30u},
                                  {"eta_minutes_max", 35u},
                                  {"average_user_rating", 4.9},
                                  {"user_ratings_count", 100u},
                                  {"cancel_rate", 0.05},
                                  {"delivery_type", kNativeDelivery},
                                  {"is_new", false}});

  int place18 = AddPlace(places, {{"eta_minutes_min", 35u},
                                  {"eta_minutes_max", 40u},
                                  {"average_user_rating", 4.9},
                                  {"user_ratings_count", 100u},
                                  {"cancel_rate", 0.05},
                                  {"delivery_type", kNativeDelivery},
                                  {"is_new", false}});

  int place19 = AddPlace(places, {{"eta_minutes_min", 35u},
                                  {"eta_minutes_max", 40u},
                                  {"average_user_rating", 4.8},
                                  {"user_ratings_count", 100u},
                                  {"cancel_rate", 0.11},
                                  {"delivery_type", kMarketplaceDelivery},
                                  {"is_new", false}});

  int place20 = AddPlace(places, {{"eta_minutes_min", 30u},
                                  {"eta_minutes_max", 40u},
                                  {"average_user_rating", 0.0},
                                  {"user_ratings_count", 100u},
                                  {"cancel_rate", 0.0},
                                  {"delivery_type", kNativeDelivery},
                                  {"is_new", true}});

  int place21 = AddPlace(places, {{"eta_minutes_min", 30u},
                                  {"eta_minutes_max", 40u},
                                  {"average_user_rating", 3.7},
                                  {"user_ratings_count", 100u},
                                  {"cancel_rate", 0.05},
                                  {"delivery_type", kNativeDelivery},
                                  {"is_new", false}});

  int place22 = AddPlace(places, {{"eta_minutes_min", 30u},
                                  {"eta_minutes_max", 40u},
                                  {"average_user_rating", 5.0},
                                  {"user_ratings_count", 10u},
                                  {"cancel_rate", 0.02},
                                  {"delivery_type", kNativeDelivery},
                                  {"is_new", false}});

  GetRanker().LocationAwareSortPlaces(places.begin(), places.end());

  ASSERT_EQ(places[0].id, place1);
  ASSERT_EQ(places[1].id, place10);
  ASSERT_EQ(places[2].id, place11);
  ASSERT_EQ(places[3].id, place2);
  ASSERT_EQ(places[4].id, place3);
  ASSERT_EQ(places[5].id, place12);
  ASSERT_EQ(places[6].id, place13);
  ASSERT_EQ(places[7].id, place4);
  ASSERT_EQ(places[8].id, place5);
  ASSERT_EQ(places[9].id, place8);
  ASSERT_EQ(places[10].id, place16);
  ASSERT_EQ(places[11].id, place9);
  ASSERT_EQ(places[12].id, place17);
  ASSERT_EQ(places[13].id, place18);
  ASSERT_EQ(places[14].id, place19);
  ASSERT_EQ(places[15].id, place20);
  ASSERT_EQ(places[16].id, place22);
  ASSERT_EQ(places[17].id, place6);
  ASSERT_EQ(places[18].id, place14);
  ASSERT_EQ(places[19].id, place15);
  ASSERT_EQ(places[20].id, place7);
  ASSERT_EQ(places[21].id, place21);
}

TEST_F(PlacesRankingModelV2Fixture, OneOrderPerPlace) {
  std::vector<Order> orders;
  std::vector<Place> places;

  int place1 = AddPlace(
      places, {{"eta_minutes_min", 10u}, {"average_user_rating", 0.0}});
  int place2 = AddPlace(
      places, {{"eta_minutes_min", 20u}, {"average_user_rating", 0.0}});
  int place3 = AddPlace(
      places, {{"eta_minutes_min", 30u}, {"average_user_rating", 0.0}});
  int place4 = AddPlace(
      places, {{"eta_minutes_min", 40u}, {"average_user_rating", 0.0}});
  int place5 = AddPlace(
      places, {{"eta_minutes_min", 10u}, {"average_user_rating", 1.0}});

  AddOrder(orders, {{"place_id", place1},
                    {"rating", 4},
                    {"hour", 0},
                    {"status", kDeliveredStatus},
                    {"delivery_location", GeoPoint{0, 0}}});
  AddOrder(orders, {{"place_id", place2},
                    {"rating", 4},
                    {"hour", 1},
                    {"status", kDeliveredStatus},
                    {"delivery_location", GeoPoint{0, 0}}});
  AddOrder(orders, {{"place_id", place3},
                    {"rating", 2},
                    {"hour", 2},
                    {"status", kDeliveredStatus},
                    {"delivery_location", GeoPoint{0, 0}}});
  AddOrder(orders, {{"place_id", place4},
                    {"rating", 5},
                    {"hour", 3},
                    {"status", kCreatedStatus},
                    {"delivery_location", GeoPoint{0, 0}}});
  AddOrder(orders, {{"place_id", place5},
                    {"rating", 5},
                    {"hour", 5},
                    {"status", kDeliveredStatus},
                    {"delivery_location", GeoPoint{10, 10}}});

  RankerRequest request;
  request.location = GeoPoint(0, 0);
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

}  // namespace v2
}  // namespace places_ranking
}  // namespace eats
}  // namespace ml
