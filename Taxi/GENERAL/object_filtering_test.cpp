#include <iostream>
#include <random>
#include <set>

#include <boost/range/irange.hpp>

#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

#include <experiments3/priorities.hpp>
#include "utils/feature_compare/prioritizer.hpp"

#include "grid.hpp"
#include "object_filtering.hpp"

namespace layers::utils::filtering {

namespace {

using namespace ::geometry::literals;

const int kDefaultZoom = 15;

const models::CacheConfig kDefaultCacheConfig{
    {},    // bbox
    15.2,  // round to 15
    18.4, 5, 5, 100,
};

const handlers::ObjectFilteringForTypeConfig GetDefaultFilteringConfig() {
  handlers::ObjectFilteringForTypeConfig config;
  config.enabled = true;

  // grouping_distance = 0.1 when zoom = 15
  config.grouping_distance_factor = (1 << 15) * 0.1;
  // 5x5
  config.buckets_per_tile_side = 5;
  // lat_side = lon_side * 2
  config.lat_squeeze_factor = 0.5;

  return config;
}

using BasicFeature = std::tuple<std::string, geometry::Position>;

std::vector<BasicFeature> kBasicFeatures{
    // different tiles, adjacent buckets
    {"f000", {30.51_lon, 42.01_lat}},
    {"f001", {30.51_lon, 41.99_lat}},
    {"f010", {30.49_lon, 41.99_lat}},

    // single bucket, close distance
    {"f002", {30.55_lon, 41.30_lat}},
    {"f003", {30.58_lon, 41.30_lat}},
    // adjacent bucket, far positions
    {"f004", {30.55_lon, 41.59_lat}},
    // another adjacent bucket, close positions
    {"f005", {30.61_lon, 41.30_lat}},

    // diagonal adjacent buckets, close positions
    {"f006", {30.79_lon, 41.59_lat}},
    {"f007", {30.81_lon, 41.61_lat}},
};

std::unordered_map<std::string, int> kExpectedTiles{
    {"f000", 2}, {"f001", 1}, {"f010", 3}, {"f002", 1}, {"f003", 1},
    {"f004", 1}, {"f005", 1}, {"f006", 1}, {"f007", 1},
};

std::unordered_map<std::string, int> kExpectedBuckets{
    {"f000", 1}, {"f001", 2}, {"f010", 8}, {"f002", 3}, {"f003", 3},
    {"f004", 4}, {"f005", 5}, {"f006", 6}, {"f007", 7},
};

std::shared_ptr<models::PointFeature> MakeFeature(
    const BasicFeature& basic_feature) {
  const auto& [id, position] = basic_feature;
  models::PointFeature feature;
  feature.id = id;
  feature.position = position;
  return std::make_shared<models::PointFeature>(std::move(feature));
}

std::vector<std::shared_ptr<models::PointFeature>> MakeFeatures(
    const std::vector<BasicFeature>& basic_features) {
  std::vector<std::shared_ptr<models::PointFeature>> features;
  for (const auto& basic_feature : basic_features) {
    features.emplace_back(MakeFeature(basic_feature));
  }
  return features;
}

template <typename F, typename T>
auto MapVector(const std::vector<T>& items, const F& mapper) {
  std::vector<decltype(mapper(items[0]))> result;
  result.reserve(items.size());
  for (const auto& item : items) {
    result.emplace_back(mapper(item));
  }
  return result;
}

template <typename F>
void AssertFeaturesUnordered(
    const std::vector<std::shared_ptr<layers::models::PointFeature>>& features,
    const F& mapper, decltype(MapVector(features, mapper)) expected) {
  auto actual = MapVector(features, mapper);
  std::sort(actual.begin(), actual.end());
  std::sort(expected.begin(), expected.end());
  ASSERT_EQ(actual, expected);
}

// Checks if each slot contains features which should go in one slot
void CheckGrid1(
    const std::vector<std::shared_ptr<models::PointFeature>>& features,
    const std::unordered_map<std::string, int>& expected_slots,
    const Grid& grid,
    std::unordered_map<GridKey, int>& grid_key_to_test_slot_id) {
  for (const auto& [grid_key, slot_content_idxes] : grid) {
    bool first = true;
    for (size_t i : slot_content_idxes) {
      const auto& expected_slot = expected_slots.at(features[i]->id);
      if (first) {
        first = false;
        ASSERT_EQ(grid_key_to_test_slot_id.find(grid_key),
                  grid_key_to_test_slot_id.end());
        grid_key_to_test_slot_id[grid_key] = expected_slot;
      } else {
        ASSERT_EQ(grid_key_to_test_slot_id.at(grid_key), expected_slot);
      }
    }
  }
}

// Checks if different slots don't contain features which should go in one slot
void CheckGrid2(std::unordered_map<GridKey, int>& grid_key_to_test_slot_id) {
  std::unordered_set<int> discovered_slot_ids;
  for (const auto& [_, slot_id] : grid_key_to_test_slot_id) {
    auto [_2, inserted] = discovered_slot_ids.emplace(slot_id);
    // If not, these features must be in one slot
    ASSERT_TRUE(inserted);
  }
}

}  // namespace

TEST(ObjectFilteringTest, TilesAndBuckets) {
  const auto zoom = kDefaultZoom;
  const auto filtering_config = GetDefaultFilteringConfig();
  const auto tile_size = GetTileSize(zoom, filtering_config);
  const auto bucket_size = GetBucketSize(tile_size, filtering_config);

  const GridSlotSize expected_tile_size{0.5 * geometry::dlon,
                                        1.0 * geometry::dlat};
  ASSERT_DOUBLE_EQ(tile_size.lon_side.Value(),
                   expected_tile_size.lon_side.Value());
  ASSERT_DOUBLE_EQ(tile_size.lat_side.Value(),
                   expected_tile_size.lat_side.Value());

  const auto features = MakeFeatures(kBasicFeatures);
  const auto [tiles, _] =
      MakeGrid(features, tile_size, boost::irange(0ul, features.size()));

  std::unordered_map<GridKey, int> grid_check_map;
  CheckGrid1(features, kExpectedTiles, tiles, grid_check_map);
  CheckGrid2(grid_check_map);

  grid_check_map.clear();
  for (const auto& [_, tile_content_idxes] : tiles) {
    const auto [buckets, _2] =
        MakeGrid(features, bucket_size, tile_content_idxes);

    CheckGrid1(features, kExpectedBuckets, buckets, grid_check_map);
  }
  CheckGrid2(grid_check_map);
}

#define ASSERT_CLOSE_BBOXES(first, second)                    \
  ASSERT_TRUE(geometry::AreCloseBoundingBoxes(first, second)) \
      << "first: " << (first) << "\nsecond: " << (second);

TEST(ObjectFilteringTest, TestExtendBbox) {
  const geometry::BoundingBox orig_bbox{
      {37.554382_lon, 55.763275_lat},
      {37.696051_lon, 55.812698_lat},
  };
  const Zooms feature_zooms{1, 21};
  auto filtering_config = GetDefaultFilteringConfig();
  const auto extended_bbox = ExtendBbox(orig_bbox, kDefaultCacheConfig,
                                        feature_zooms, filtering_config);

  // Extends as expected
  ASSERT_CLOSE_BBOXES(extended_bbox, (geometry::BoundingBox{
                                         {37.5_lon, 55.0_lat},
                                         {38.0_lon, 56.0_lat},
                                     }));

  // Does not extend further
  ASSERT_CLOSE_BBOXES(extended_bbox,
                      ExtendBbox(extended_bbox, kDefaultCacheConfig,
                                 feature_zooms, filtering_config));

  // Another squeeze factor
  filtering_config.lat_squeeze_factor = 2;
  ASSERT_CLOSE_BBOXES(ExtendBbox(orig_bbox, kDefaultCacheConfig, feature_zooms,
                                 filtering_config),
                      (geometry::BoundingBox{
                          {37.5_lon, 55.75_lat},
                          {38.0_lon, 56.0_lat},
                      }));

  // Does not extend if filtering is disabled
  filtering_config.enabled = false;
  ASSERT_CLOSE_BBOXES(orig_bbox, ExtendBbox(orig_bbox, kDefaultCacheConfig,
                                            feature_zooms, filtering_config));
}

namespace {

void CheckCorrectFeaturesMarked(
    const Strategy& strategy, bool with_buckets,
    std::vector<std::string>& expected_visible_features) {
  RunInCoro([&] {
    const auto zoom = kDefaultZoom;
    const auto filtering_config = GetDefaultFilteringConfig();
    const auto tile_size = GetTileSize(zoom, filtering_config);
    const auto bucket_size = GetBucketSize(tile_size, filtering_config);

    auto features = MakeFeatures(kBasicFeatures);
    const layers::utils::feature_compare::Prioritizer p;
    std::vector<FeatureMeta> features_meta(features.size());

    const auto [tiles, _] =
        MakeGrid(features, tile_size, boost::irange(0ul, features.size()));
    ZoomHandleStats zoom_stats;
    for (const auto& [tile_key, tile_content_idxes] : tiles) {
      MarkVisibleFeatures(features, features_meta, tile_key, tile_content_idxes,
                          zoom, bucket_size, strategy, with_buckets, zoom_stats,
                          p);
    }
    std::vector<std::string> actual_visibile_features;
    for (size_t i = 0; i < features.size(); ++i) {
      if (features_meta[i].min_zoom) {
        actual_visibile_features.emplace_back(features[i]->id);
      }
    }

    std::sort(actual_visibile_features.begin(), actual_visibile_features.end());
    std::sort(expected_visible_features.begin(),
              expected_visible_features.end());

    ASSERT_EQ(actual_visibile_features, expected_visible_features);
  });
}

}  // namespace

TEST(ObjectFilteringTest, MarkVisibleFeaturesBasic) {
  std::vector<std::string> expected_visible_features{
      "f000", "f001", "f010",  // different tiles

      // f002 is skipped, because it's in the same bucket as f003 and 2 < 3

      "f003", "f005",  // these are close, but in different buckets, not joint
                       // by basic algo

      "f004",  // standalone

      "f006", "f007",  // close, but different buckets
  };

  CheckCorrectFeaturesMarked(Strategy::kPerBucket, true,
                             expected_visible_features);
}

TEST(ObjectFilteringTest, MarkVisibleFeaturesClustering) {
  std::vector<std::string> expected_visible_features{
      "f000",
      "f001",
      "f010",  // different tiles

      // f002 and f003 skipped, as they belong the same component as f005

      "f005",

      "f004",  // standalone

      // f006 skipped because of f007

      "f007",
  };

  CheckCorrectFeaturesMarked(Strategy::kMainInCluster, false,
                             expected_visible_features);

  CheckCorrectFeaturesMarked(Strategy::kMainInCluster, true,
                             expected_visible_features);
}

namespace {

std::vector<std::shared_ptr<models::PointFeature>> MakeRandomFeatures(
    size_t n_features, size_t seed) {
  const double lon_lo = 45;
  const double lon_hi = 46;
  const double lat_lo = 50;
  const double lat_hi = 51;

  std::uniform_real_distribution lon_dist(lon_lo, lon_hi);
  std::uniform_real_distribution lat_dist(lat_lo, lat_hi);

  std::mt19937 rng(seed);

  std::vector<std::shared_ptr<models::PointFeature>> features;
  features.reserve(n_features);
  for (size_t i = 0; i < n_features; ++i) {
    double lon = lon_dist(rng);
    double lat = lat_dist(rng);
    features.emplace_back(MakeFeature(
        {std::to_string(i), {lon * geometry::lon, lat * geometry::lat}}));
  }
  return features;
}

// XXX: test with different types
std::set<std::string> GetClosePairs(
    const std::vector<std::shared_ptr<models::PointFeature>>& features,
    const GridSlotSize& bucket_size, bool use_buckets) {
  std::vector<size_t> features_idxes(features.size());
  std::iota(features_idxes.begin(), features_idxes.end(), 0ul);

  // should be sorted
  std::set<std::string> result;

  ZoomHandleStats zoom_stats;
  FeaturePairsGen fpg(features, 1337, features_idxes, kDefaultZoom, bucket_size,
                      use_buckets, zoom_stats);
  for (size_t i = 0; i < features.size(); ++i) {
    const auto& position_i = features[i]->position;
    const auto filtering_radius = GetFilteringRadius(position_i, bucket_size);
    for (size_t j = i + 1; j < features.size(); ++j) {
      const auto& position_j = features[j]->position;
      if (geometry::GreatCircleDistance(position_i, position_j) <
          filtering_radius) {
        result.emplace(features[i]->id + "__" + features[j]->id);
      }
    }
  }

  return result;
}

}  // namespace

TEST(ObjectFilteringTest, ClosePairs) {
  const size_t n_features = 50;
  for (size_t seed = 322; seed <= 1337; ++seed) {
    const auto features = MakeRandomFeatures(n_features, seed);

    for (double squeeze : std::initializer_list<double>{1, 0.5, 1.5, 1.75}) {
      const GridSlotSize bucket_size{0.1 * geometry::dlon,
                                     0.1 * squeeze * geometry::dlat};

      const auto no_buckets = GetClosePairs(features, bucket_size, false);
      const auto with_buckets = GetClosePairs(features, bucket_size, true);

      std::vector<std::string> diff;

      std::set_symmetric_difference(no_buckets.begin(), no_buckets.end(),
                                    with_buckets.begin(), with_buckets.end(),
                                    std::back_inserter(diff));
      ASSERT_EQ(diff, std::vector<std::string>{})
          << "seed: " << seed << ", squeeze: " << squeeze;
    }
  }
}

namespace {

void StressTest(const Strategy& strategy, bool use_buckets, size_t seed) {
  RunInCoro([&] {
    std::mt19937 rng(seed);

    const size_t n_features = 5000;

    auto features = MakeRandomFeatures(n_features, seed);
    const layers::utils::feature_compare::Prioritizer p;

    const size_t kMaxZoom = 17;
    const size_t kMinZoom = 15;
    for (size_t zoom = kMaxZoom; zoom >= kMinZoom; --zoom) {
      const auto filtering_config = GetDefaultFilteringConfig();
      const auto tile_size = GetTileSize(zoom, filtering_config);
      const auto bucket_size = GetBucketSize(tile_size, filtering_config);

      std::vector<FeatureMeta> features_meta(features.size());

      const auto [tiles, _] =
          MakeGrid(features, tile_size, boost::irange(0ul, features.size()));
      ZoomHandleStats zoom_stats;
      for (const auto& [tile_key, tile_content_idxes] : tiles) {
        // Uncomment to view some debug info
        // std::cout << "tile " << tile_key << ", feats: " <<
        // tile_content_idxes.size() << "\n";
        MarkVisibleFeatures(features, features_meta, tile_key,
                            tile_content_idxes, zoom, bucket_size, strategy,
                            use_buckets, zoom_stats, p);
      }
      // std::cout << "zoom=" << zoom << ": " << Format(zoom_stats) << "\n";
    }
  });
}

}  // namespace

TEST(ObjectFilteringTest, StressBasic) {
  StressTest(Strategy::kPerBucket, true, 1337);
}

TEST(ObjectFilteringTest, StressQuadraticNoBuckets) {
  StressTest(Strategy::kNoHigherPriorityNearby, false, 1337);
}

TEST(ObjectFilteringTest, StressQuadraticWithBuckets) {
  StressTest(Strategy::kNoHigherPriorityNearby, true, 1337);
}

TEST(ObjectFilteringTest, StressClusteringNoBuckets) {
  StressTest(Strategy::kMainInCluster, false, 1337);
}

TEST(ObjectFilteringTest, StressClusteringWithBuckets) {
  StressTest(Strategy::kMainInCluster, true, 1337);
}

namespace {
const std::string kPrioritySettings = R"=({
  "priorities_tuple": [{
    "name": "g-first",
    "payload": {
      "type": "value",
      "by_provider": {
        "grouping": { "type": "const", "value": 9999 },
        "__default__": { "type": "const", "value": 1 }
      }
    }
  }, {
    "name": "hash_weights",
    "payload": {
      "type": "mult_hash",
      "by_provider": {
        "__default__": 1
      }
    }
  }]
})=";

std::vector<std::shared_ptr<layers::models::PointFeature>> FilterObjects(
    const handlers::ObjectFilteringForTypeConfig& config,
    const std::optional<std::string>& selected_object_id = std::nullopt) {
  auto cache_config = kDefaultCacheConfig;

  experiments3::layers_object_filtering::Value filtering_config;
  filtering_config.enabled = true;
  filtering_config.by_provider_name.extra["scooter"] = config;

  ObjectFilteringManager manager(
      filtering_config,                  //
      {handlers::ObjectType::kScooter},  // object_types
      {"scooter"},                       // provider_names
      cache_config, Zooms{0, 99});

  auto features = MakeFeatures(kBasicFeatures);
  features[6]->count = 0;  // f005
  const auto& priority_settings = Parse(
      formats::json::FromString(kPrioritySettings),
      formats::parse::To<experiments3::layers_priorities::PrioritySettings>{});
  const layers::utils::feature_compare::Prioritizer prioritizer(
      priority_settings, {{"scooter", features.size()}});
  manager.FilterObjects(features, cache_config, prioritizer,
                        selected_object_id);
  std::sort(features.begin(), features.end(),
            [](const auto& a, const auto& b) { return a->id < b->id; });
  return features;
}
}  // namespace

UTEST(ObjectFilteringTest, FilterObjects_Default) {
  const auto& features = FilterObjects(GetDefaultFilteringConfig());

  const auto& actual_features = MapVector(features, [](const auto& feature) {
    return std::tuple{feature->id,
                      feature->properties.display_settings.zooms.value_or(
                          std::vector<double>{})};
  });
  decltype(actual_features)& expected_features = {
      {"f000", {1, 21}},  {"f001", {1, 21}}, {"f002", {1, 21}},
      {"f003", {17, 21}}, {"f004", {1, 21}}, {"f005", {1, 21}},
      {"f006", {1, 21}},  {"f007", {1, 21}}, {"f010", {1, 21}},
  };
  ASSERT_EQ(actual_features, expected_features);
}

UTEST(ObjectFilteringTest, FilterObjects_Grouping) {
  // Arrange
  auto config = GetDefaultFilteringConfig();

  auto& groups_config = config.groups.emplace();
  groups_config.min_features_count_to_group = 2;
  groups_config.count_filter = 1;
  groups_config.debug_mode = true;
  groups_config.zoom_gap = 0.11;

  auto& template_ = groups_config.template_.emplace();
  template_.type = handlers::ObjectType::kGroup;

  handlers::ATTextProperties text;
  text.text = "{count}";
  groups_config.overlay.emplace().attributed_text.emplace().items.emplace_back(
      text);

  const auto& features = FilterObjects(config, "f006");

  AssertFeaturesUnordered(
      features,
      [](const auto& feature) {
        std::vector<std::string> overlay_texts;
        if (const auto& overlays = feature->properties.overlays) {
          for (const auto& overlay : *overlays) {
            if (const auto& attributed_text = overlay.attributed_text) {
              for (const auto& item : attributed_text->items) {
                if (const auto& text =
                        std::get_if<handlers::ATTextProperties>(&item)) {
                  overlay_texts.push_back(text->text);
                }
              }
            }
          }
        }
        const auto& feature_ids =
            Parse(feature->debug_info["feature_ids"],
                  formats::parse::To<std::optional<std::vector<std::string>>>{})
                .value_or(std::vector<std::string>{});
        return std::tuple{
            feature->id,
            feature->properties.display_settings.zooms.value_or(
                std::vector<double>{}),
            overlay_texts,
            feature_ids,
        };
      },
      {
          {"f000", {01, 21}, {}, {}},
          {"f001", {17, 21}, {}, {}},  // grouped
          {"f002", {18, 21}, {}, {}},  // grouped
          {"f003", {18, 21}, {}, {}},  // grouped
          {"f004", {17, 21}, {}, {}},  // grouped
          {"f005", {01, 21}, {}, {}},  // grouped, but count=0, so skipped
          {"f006", {01, 21}, {}, {}},  // we iterate 19..15 but it's selected
          // {"f007", {20, 21}, {}, {}},   // but we iterate 19..15
          {"f010", {1, 21}, {}, {}},
          {"g:15:f001",
           {15, 15.89},
           {"6"},  // f002.count = 0
           {"f001", "f002", "f003", "f004", "f005", "f006", "f007"}},
          {"g:16:f001", {16, 16.89}, {"2"}, {"f001", "f004"}},
          {"g:17:f002", {16, 17.89}, {"2"}, {"f002", "f003", "f005"}},
          {"g:19:f006", {16, 19.89}, {"2"}, {"f006", "f007"}},
      });
}

}  // namespace layers::utils::filtering
