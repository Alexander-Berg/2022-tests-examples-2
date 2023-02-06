#include "map_render.hpp"

#include <cmath>
#include <iterator>
#include <utility>

#include <gtest/gtest.h>

#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/formats/json.hpp>
#include <userver/logging/log.hpp>
#include <userver/utest/utest.hpp>

#include <geometry/position.hpp>

#include <defs/all_definitions.hpp>
#include <models/place.hpp>
#include <taxi_config/taxi_config.hpp>
#include <taxi_config/variables/EATS_CATALOG_MAP_RESPONSE_LIMITS.hpp>

namespace handlers::common_map {

namespace {

using eats_catalog::algo::PlacesCluster;
using eats_catalog::models::Place;
using eats_catalog::models::PlaceId;
using eats_catalog::models::PlaceInfo;
using ::geometry::BoundingBox;
using ::geometry::Position;
using MapConfig =
    taxi_config::eats_catalog_map_response_limits::EatsCatalogMapResponseLimits;

Position MakePosition(const double lon, const double lat) {
  return {lon * ::geometry::lon, lat * ::geometry::lat};
}

taxi_config::TaxiConfig PatchConfig(MapConfig map_config) {
  auto config =
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>();
  config.eats_catalog_map_response_limits = std::move(map_config);
  return config;
}

struct ScoreIdPosition {
  double score;
  int id;
  double lon, lat;
};

struct RelevantPinsTestCase {
  MapConfig map_config;
  std::vector<ScoreIdPosition> places;
  BoundingBox bounding_box;
  std::vector<int> expected_places;  // order of ids matters!
  std::vector<std::vector<int>> expected_clusters;
};

bool AreEqual(const std::vector<PlacesCluster>& clusters,
              std::vector<std::vector<int>>& ids) {
  if (clusters.size() != ids.size()) {
    return false;
  }

  std::vector<std::vector<int>> clustered_ids;
  for (const auto& cluster : clusters) {
    std::vector<int> raw_ids(cluster.place_ids.size());
    std::transform(cluster.place_ids.begin(), cluster.place_ids.end(),
                   raw_ids.begin(),
                   [](const auto id) { return id.GetUnderlying(); });
    std::sort(raw_ids.begin(), raw_ids.end());
    clustered_ids.emplace_back(std::move(raw_ids));
  }
  for (auto& entry : ids) {
    std::sort(entry.begin(), entry.end());
  }

  for (const auto& entry : ids) {
    if (std::find(clustered_ids.begin(), clustered_ids.end(), entry) ==
        clustered_ids.end()) {
      return false;
    }
  }
  return true;
}

void TestKeepRelevantMapPins(RelevantPinsTestCase& tc) {
  std::vector<PlaceInfo> place_infos;
  // reserve нужен, чтобы ссылки на PlaceInfo не инвалидировались
  place_infos.reserve(tc.places.size());
  std::vector<Place> places;
  for (const auto& entry : tc.places) {
    auto& place_info = place_infos.emplace_back();
    place_info.id = PlaceId{entry.id};
    place_info.location.position = MakePosition(entry.lon, entry.lat);
    Place place{place_info};
    places.push_back(std::move(place));
  }
  std::vector<PlaceWithScore> with_score;
  for (size_t i = 0; i < tc.places.size(); ++i) {
    with_score.push_back({tc.places[i].score, &places[i]});
  }
  const auto& config = PatchConfig(tc.map_config);

  auto result =
      KeepRelevantMapPins(std::move(with_score), config, tc.bounding_box);

  EXPECT_EQ(tc.expected_places.size(), result.places.size());
  for (size_t i = 0; i < tc.expected_places.size(); ++i) {
    EXPECT_EQ(tc.expected_places[i],
              result.places[i].place->id.GetUnderlying());
  }

  EXPECT_TRUE(AreEqual(result.clusters, tc.expected_clusters));
}

}  // namespace

// Not a single constraint is violated
UTEST(KeepRelevantMapPins, NoConstraintsApply) {
  RelevantPinsTestCase tc{
      {
          10,  // max_found_places
          10,  // max_map_pins
          10   // max_clustered_points
      },
      {{0.5, 1, 37.5, 55.7},
       {0.7, 2, 37.6, 55.8},
       {0.2, 3, 37.6, 55.80001}},                                // places
      {MakePosition(37.49, 55.69), MakePosition(37.61, 55.81)},  // bounding_box
      {2, 1, 3},  // expected_places
      {{2, 3}}    // expected_clusters
  };
  TestKeepRelevantMapPins(tc);
}

// Choose place with the highest score and all its neighbours
UTEST(KeepRelevantMapPins, OnePin) {
  RelevantPinsTestCase tc{
      {
          10,  // max_found_places
          1,   // max_map_pins
          10   // max_clustered_points
      },
      {{0.5, 1, 37.5, 55.7},
       {0.6, 4, 37.5, 55.7},
       {0.4, 5, 37.5, 55.7},
       {0.7, 2, 37.6, 55.8},
       {0.2, 3, 37.6, 55.80001},
       {0.4, 6, 37.6, 55.7}},                                    // places
      {MakePosition(37.49, 55.69), MakePosition(37.61, 55.81)},  // bounding_box
      {2, 3},   // expected_places
      {{2, 3}}  // expected_clusters
  };
  TestKeepRelevantMapPins(tc);
}

// Taking place #2 into response automatically adds place #3 -> max_found_places
// is violated
UTEST(KeepRelevantMapPins, MaxFoundPlacesViolated) {
  RelevantPinsTestCase tc{
      {
          2,   // max_found_places
          10,  // max_map_pins
          10   // max_clustered_points
      },
      {{0.5, 1, 37.5, 55.7},
       {0.6, 4, 37.5, 55.7},
       {0.4, 5, 37.5, 55.7},
       {0.7, 2, 37.6, 55.8},
       {0.2, 3, 37.6, 55.80001},
       {0.4, 6, 37.6, 55.7}},                                    // places
      {MakePosition(37.49, 55.69), MakePosition(37.61, 55.81)},  // bounding_box
      {2, 3},   // expected_places
      {{2, 3}}  // expected_clusters
  };
  TestKeepRelevantMapPins(tc);
}

// Take all places from the second cluster despite total number of places in
// response exceeds max_found_places
UTEST(KeepRelevantMapPins, AddAllPlacesFromCLuster) {
  RelevantPinsTestCase tc{
      {
          3,  // max_found_places
          2,  // max_map_pins
          10  // max_clustered_points
      },
      {{0.5, 1, 37.5, 55.7},
       {0.6, 4, 37.5, 55.7},
       {0.4, 5, 37.5, 55.7},
       {0.7, 2, 37.6, 55.8},
       {0.2, 3, 37.6, 55.80001},
       {0.4, 6, 37.6, 55.7}},                                    // places
      {MakePosition(37.49, 55.69), MakePosition(37.61, 55.81)},  // bounding_box
      {2, 4, 1, 5, 3},     // expected_places
      {{2, 3}, {1, 4, 5}}  // expected_clusters
  };
  TestKeepRelevantMapPins(tc);
}

// Take the most rated cluster into one pin and the second most rated place into
// another pin
UTEST(KeepRelevantMapPins, ClusterAndSinglePlace) {
  RelevantPinsTestCase tc{
      {
          3,  // max_found_places
          3,  // max_map_pins
          10  // max_clustered_points
      },
      {{0.5, 1, 37.5, 55.7},
       {0.6, 4, 37.5, 55.7},
       {0.4, 5, 37.5, 55.7},
       {0.7, 2, 37.6, 55.8},
       {0.2, 3, 37.6, 55.80001},
       {0.65, 6, 37.6, 55.7}},                                   // places
      {MakePosition(37.49, 55.69), MakePosition(37.61, 55.81)},  // bounding_box
      {2, 6, 3},  // expected_places
      {{2, 3}}    // expected_clusters
  };
  TestKeepRelevantMapPins(tc);
}

// Place #3 is pruned even before the clustering algorithm is executed
UTEST(KeepRelevantMapPins, MaxClusteredPointsViolated) {
  RelevantPinsTestCase tc{
      {
          10,  // max_found_places
          3,   // max_map_pins
          5    // max_clustered_points
      },
      {{0.5, 1, 37.5, 55.7},
       {0.6, 4, 37.5, 55.7},
       {0.4, 5, 37.5, 55.7},
       {0.7, 2, 37.6, 55.8},
       {0.2, 3, 37.6, 55.80001},
       {0.65, 6, 37.6, 55.7}},                                   // places
      {MakePosition(37.49, 55.69), MakePosition(37.61, 55.81)},  // bounding_box
      {2, 6, 4, 1, 5},  // expected_places
      {{4, 1, 5}}       // expected_clusters
  };
  TestKeepRelevantMapPins(tc);
}

namespace {

using eats_catalog::models::BrandId;
using eats_catalog::models::DeliveryType;

struct PlaceDuplicate {
  int place_id;
  int brand_id;
  std::string address;
  double lon, lat;
  double score;
  DeliveryType delivery;
};

struct DeduplicateTestCase {
  std::vector<PlaceDuplicate> input;
  std::vector<int> expected_place_ids;
};

void TestDeduplicatePlaces(const DeduplicateTestCase& tc) {
  std::vector<PlaceInfo> place_infos;
  // reserve нужен, чтобы ссылки на PlaceInfo не инвалидировались
  place_infos.reserve(tc.input.size());
  std::vector<Place> places;
  for (const auto& entry : tc.input) {
    auto& place_info = place_infos.emplace_back();
    place_info.id = PlaceId{entry.place_id};
    place_info.brand.id = BrandId{entry.brand_id};
    place_info.location.address = {"", entry.address};
    place_info.location.position = {entry.lon * ::geometry::lon,
                                    entry.lat * ::geometry::lat};
    place_info.delivery_type = entry.delivery;
    Place place{place_info};
    places.push_back(std::move(place));
  }

  std::vector<PlaceWithScore> with_score;
  with_score.reserve(places.size());
  for (size_t i = 0; i < places.size(); ++i) {
    with_score.push_back({tc.input[i].score, &places[i]});
  }

  DeduplicatePlaces(with_score);

  EXPECT_EQ(tc.expected_place_ids.size(), with_score.size());
  for (const auto place_id : tc.expected_place_ids) {
    auto iter = std::find_if(
        with_score.begin(), with_score.end(), [place_id](const auto& entry) {
          return entry.place->id.GetUnderlying() == place_id;
        });
    EXPECT_FALSE(iter == with_score.end());
  }
}

}  // namespace

UTEST(DeduplicatePlacesForMap, ByAddress) {
  DeduplicateTestCase tc{
      {
          // If both restaurants have equal rating keep the one with native
          // delivery
          {1, 1, "Moscow", 37.0, 55.0, 4.0, DeliveryType::kNative},
          {2, 1, "Moscow", 37.0, 55.0, 4.0, DeliveryType::kMarketplace},
          // Native place has the same brand as two above, but differs in
          // address and position
          {3, 1, "Moscow, Bolshaya Ordynka str.", 38.0, 55.0, 4.0,
           DeliveryType::kNative},
          // Both restaurants are not affected since they do not share the same
          // address and their positions don't match
          {4, 2, "Moscow", 37.0, 55.0, 4.0, DeliveryType::kNative},
          {5, 2, "Moscow, str.", 38.0, 56.0, 4.0, DeliveryType::kMarketplace},
          // Out of two restaurants with native delivery, keep the one with
          // higher rating
          {6, 3, "Havana", 37.0, 55.0, 4.0, DeliveryType::kNative},
          {7, 3, "Havana", 37.0, 55.0, 4.2, DeliveryType::kNative},
          // Out of two restaurants with marketplace delivery, keep the one with
          // higher rating
          {8, 3, "Havana, ave.", 38.0, 56.0, 4.0, DeliveryType::kMarketplace},
          {9, 3, "Havana, ave.", 38.0, 56.0, 4.2, DeliveryType::kMarketplace},
          // Marketplace has the same brand as two above, but differs in address
          // and position
          {10, 3, "Santa Clara", 4.2, 37.0, 56.0, DeliveryType::kMarketplace},
          // Choose restaurant with the higher rating, even if marketplace
          // dominates native delivery
          {11, 3, "Pinar del Rio", 39.0, 57.0, 4.4, DeliveryType::kNative},
          {12, 3, "Pinar del Rio", 39.0, 57.0, 4.5, DeliveryType::kMarketplace},
      },
      {1, 3, 4, 5, 7, 9, 10, 12}};
  TestDeduplicatePlaces(tc);
}

UTEST(DeduplicatePlacesForMap, ByAddressAndCoordinates) {
  DeduplicateTestCase tc{
      {
          // Out of two restaurants with equal coordinates, but different
          // addresses, keep the one with higher rating.
          // Coordinates are compared up to 5 digits after decimal point
          {1, 1, "St.Petersburg", 37.0, 55.0, 4.5, DeliveryType::kNative},
          {2, 1, "Moscow", 37.000004, 54.999996, 4.0, DeliveryType::kNative},
          // Three restaurants have either same address or same coordinates. The
          // one with native delivery wins.
          {3, 2, "Moscow", 37.0, 55.0, 4.0, DeliveryType::kNative},
          {4, 2, "Podolsk", 37.0, 55.0, 4.0, DeliveryType::kMarketplace},
          {5, 2, "Moscow", 38.0, 56.0, 4.0, DeliveryType::kMarketplace},
          // Similarity is NOT transitive -- if A and B share the same address
          // and B and C have equal coordinates, then A and C are NOT similar
          // unless their adresses match. Places are deduplicated by coordinates
          // at first and then -- by address. Voronezh with rating 4.2 is kept,
          // since Voronezh with 4.3 is dominated my Moscow with 4.4.
          {6, 3, "Moscow", 37.0, 55.0, 4.1, DeliveryType::kMarketplace},
          {7, 3, "Voronezh", 37.0, 55.0, 4.2, DeliveryType::kMarketplace},
          {8, 3, "Moscow", 38.0, 56.0, 4.4, DeliveryType::kMarketplace},
          {9, 3, "Voronezh", 38.0, 56.0, 4.3, DeliveryType::kMarketplace},
          // Restaurant has the same brand_id as the previous group, but neither
          // address nor coordinates match, so it is not affected.
          {10, 3, "Orel", 50.0, 50.0, 4.4, DeliveryType::kMarketplace},
          // Restaurants are divided into two groups by coordinates, but are
          // united by the same address. Marketplace has higher rating, than
          // native delivery.
          {11, 4, "Moscow", 38.0, 56.0, 4.1, DeliveryType::kMarketplace},
          {12, 4, "Moscow", 37.0, 55.0, 4.2, DeliveryType::kNative},
          {13, 4, "Moscow", 37.0, 55.0, 4.3, DeliveryType::kNative},
          {14, 4, "Moscow", 38.0, 56.0, 4.4, DeliveryType::kMarketplace},
      },
      {1, 3, 7, 8, 10, 14}};
  TestDeduplicatePlaces(tc);
}

namespace {

/*
 * Places are sorted in the following order:
 * by brand ID
 * by latitude if coordinates are not equal
 * if lat and lon are equal up to 5 decimal digits, then:
 *    by score
 *    native comes first, then - marketplace
 */
struct CompareInfo {
  int rank;
  int brand_id;
  double lon, lat;
  double score;
  DeliveryType delivery;
};

// Input vector is already correctly sorted.
// Test that predicate is consistent with sorting order.
void TestCompareForDeduplicate(const std::vector<CompareInfo>& input) {
  std::vector<PlaceInfo> place_infos;
  // reserve нужен, чтобы ссылки на PlaceInfo не инвалидировались
  place_infos.reserve(input.size());
  std::vector<Place> places;
  for (const auto& entry : input) {
    auto& place_info = place_infos.emplace_back();
    place_info.brand.id = BrandId{entry.brand_id};
    place_info.location.position = {entry.lon * ::geometry::lon,
                                    entry.lat * ::geometry::lat};
    place_info.delivery_type = entry.delivery;
    Place place{place_info};
    places.push_back(std::move(place));
  }

  std::vector<PlaceWithScore> with_score;
  with_score.reserve(places.size());
  for (size_t i = 0; i < places.size(); ++i) {
    with_score.push_back({input[i].score, &places[i]});
  }

  const auto& less = CompareForDeduplicate;

  for (size_t lhs_idx = 0; lhs_idx < with_score.size(); ++lhs_idx) {
    for (size_t rhs_idx = 0; rhs_idx < with_score.size(); ++rhs_idx) {
      EXPECT_EQ(less(with_score[lhs_idx], with_score[rhs_idx]),
                input[lhs_idx].rank < input[rhs_idx].rank);
    }
  }
}

}  // namespace

TEST(CompareForDeduplicate, Simple) {
  std::vector<CompareInfo> sorted{

      // Группа с Brand ID = 1
      {101, 1, 35.0, 55.0, 4.9, DeliveryType::kMarketplace},
      {101, 1, 35.0, 55.0, 4.9, DeliveryType::kMarketplace},
      {101, 1, 35.0, 55.0, 4.9, DeliveryType::kMarketplace},
      {102, 1, 34.999996, 55.0, 4.8, DeliveryType::kMarketplace},
      {103, 1, 34.999996, 55.000004, 4.79, DeliveryType::kNative},
      {103, 1, 35.0, 55.0, 4.79, DeliveryType::kNative},
      {103, 1, 35.0, 55.0, 4.79, DeliveryType::kNative},
      {103, 1, 35.0, 55.0, 4.79, DeliveryType::kNative},
      {104, 1, 35.0, 55.00001, 4.99, DeliveryType::kNative},

      // Группа с Brand ID = 2
      {201, 2, 35.0, 55.0, 4.9, DeliveryType::kNative},
      {202, 2, 35.0, 55.0, 4.9, DeliveryType::kMarketplace},
      {203, 2, 35.0, 55.0, 4.8, DeliveryType::kNative},
      {204, 2, 34.0, 57.0, 4.95, DeliveryType::kMarketplace},
      {205, 2, 34.0, 57.0, 4.9, DeliveryType::kMarketplace},

      // Группа с Brand ID = 3, порядок по longitude
      {301, 3, 24.0, 55.0, 3.9, DeliveryType::kNative},
      {302, 3, 25.0, 55.0, 4.1, DeliveryType::kNative},
      {303, 3, 35.0, 55.0, 4.0, DeliveryType::kNative},

      // Группа с Brand ID = 4 для EDACAT-1682
      {401, 4, 25.0, 55.0, 4.0, DeliveryType::kNative},
      {402, 4, 25.0, 55.0, 3.9, DeliveryType::kNative},
      {403, 4, 35.0, 55.0, 4.0, DeliveryType::kNative}};

  TestCompareForDeduplicate(sorted);
}

}  // namespace handlers::common_map
