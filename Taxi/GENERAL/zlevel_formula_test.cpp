#include "zlevel_formula.hpp"

#include <cmath>
#include <iterator>
#include <limits>
#include <utility>

#include <fmt/format.h>
#include <gtest/gtest.h>

#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/utest/utest.hpp>

#include <defs/all_definitions.hpp>
#include <models/place.hpp>
#include <taxi_config/taxi_config.hpp>
#include <taxi_config/variables/EATS_CATALOG_FAVORITES_FORMULA.hpp>
#include <taxi_config/variables/EATS_CATALOG_PIN_SIZE_RANGES.hpp>
#include <taxi_config/variables/EATS_CATALOG_PLACE_FORMULA_BY_REGION.hpp>
#include "test_utils.hpp"

namespace eats_catalog::algo {

namespace {

using ::taxi_config::eats_catalog_pin_size_ranges::ZoomRange;

constexpr std::string_view kPlaceScoreFormula = R"({
  "__default__": {
    "rating_min": 3.7844,
    "rating_max": 5,
    "count_min": 1,
    "count_max": 200,
    "count_threshold": 201,
    "left_formula": {
      "rating_mean": 4.668,
      "rating_std": 0.2408,
      "count_mean": 146.8327,
      "count_std": 60.5249,
      "intercept": 0.3908,
      "r1": 0.2668,
      "c1": 0.0695,
      "r2": 0.0519,
      "rc": 0.0602,
      "c2": -0.0147,
      "r3": 0.0022,
      "r2c": 0.0142,
      "rc2": -0.0145,
      "c3": 0.009,
      "r4": 0,
      "r3c": 0,
      "r2c2": 0,
      "rc3": 0,
      "c4": 0
    },
    "right_formula": {
      "mean": 0,
      "std": 1,
      "intercept": 0,
      "x1": 0,
      "x2": 0,
      "x3": 0,
      "x4": 0
    }
  },
  "1": {
    "rating_min": 3.1839,
    "rating_max": 5,
    "count_min": 1,
    "count_max": 200,
    "count_threshold": 200,
    "left_formula": {
      "rating_mean": 4.6621,
      "rating_std": 0.3563,
      "count_mean": 49.4074,
      "count_std": 54.2363,
      "intercept": 0.24275,
      "r1": 0.16238,
      "c1": 0.19748,
      "r2": 0.07737,
      "rc": 0.11888,
      "c2": -0.09358,
      "r3": 0.02372,
      "r2c": 0.02834,
      "rc2": -0.04083,
      "c3": 0.01534,
      "r4": 0.00269769,
      "r3c": 0.00269161,
      "r2c2": -0.00415742,
      "rc3": 0.004427948,
      "c4": -0.00017866
    },
    "right_formula": {
      "mean": 4.7672,
      "std": 0.1861,
      "intercept": 0.5464278,
      "x1": 0.2930459,
      "x2": 0.0882626,
      "x3": 0.0117345,
      "x4": 0.0005628
    }
  }
})";

constexpr std::string_view kFavoritesFormula = R"({
  "favorites_scale": 2.0,
  "favorites_bias": 0.0
})";

constexpr std::string_view kPinSizeRanges = R"({
  "hidden": {
    "min": 0,
    "max": 13
  },
  "small": {
    "min": 8,
    "max": 15
  },
  "medium": {
    "min": 12,
    "max": 17
  },
  "large": {
    "min": 14,
    "max": 19
  },
  "adjacent_min_gap": 1.0
})";

auto PatchConfig(const std::string_view formula = kPlaceScoreFormula,
                 const std::string_view favorites = kFavoritesFormula,
                 const std::string_view ranges = kPinSizeRanges) {
  return dynamic_config::MakeDefaultStorage(
      {{taxi_config::EATS_CATALOG_PLACE_FORMULA_BY_REGION,
        formats::json::FromString(formula)},
       {taxi_config::EATS_CATALOG_PIN_SIZE_RANGES,
        formats::json::FromString(ranges)},
       {taxi_config::EATS_CATALOG_FAVORITES_FORMULA,
        formats::json::FromString(favorites)}});
}

struct ScoreTestCase {
  std::string_view formula;
  double rating, count;
  double expected;
  bool is_favorite{false};
  std::string_view favorites = kFavoritesFormula;
  std::string region = "__default__";
};

void TestPlaceScore(const ScoreTestCase& tc) {
  const auto storage = PatchConfig(tc.formula, tc.favorites);
  const auto config = storage.GetSnapshot();
  eats_catalog::models::RatingInfo info;
  info.value = tc.rating;
  info.feedback_count = tc.count;

  PlaceScoreFormula formula{
      config[taxi_config::EATS_CATALOG_PLACE_FORMULA_BY_REGION][tc.region],
      config[taxi_config::EATS_CATALOG_FAVORITES_FORMULA]};
  const auto score = CalculatePlaceScore(formula, info, tc.is_favorite);
  ExpectDoubleEqual(score, tc.expected);
}

struct LevelsTestCase {
  std::string_view ranges;
  double score;
  handlers::MapPinTypesminzoomlevels expected;
};

void TestZoomLevels(const LevelsTestCase& tc) {
  const auto storage =
      PatchConfig(kPlaceScoreFormula, kFavoritesFormula, tc.ranges);
  const auto config = storage.GetSnapshot();

  const auto& levels = CalculateZoomLevels(
      tc.score, config[taxi_config::EATS_CATALOG_PIN_SIZE_RANGES]);

  ExpectOptionalEqual(tc.expected.small, levels.small);
  ExpectOptionalEqual(tc.expected.medium, levels.medium);
  ExpectOptionalEqual(tc.expected.large, levels.large);
}

}  // namespace

UTEST(CalculatePlaceScore, MaximumScore) {
  ScoreTestCase tc{
      kPlaceScoreFormula,  // formula
      5.0,                 // rating
      200,                 // count
      1.0                  // expected
  };
  TestPlaceScore(tc);
}

// Rating below rating_min results in 0 score regardless of number of reviews
UTEST(CalculatePlaceScore, MinimumScore) {
  ScoreTestCase tc{
      kPlaceScoreFormula,  // formula
      3.5,                 // rating
      200,                 // count
      0.0                  // expected
  };
  TestPlaceScore(tc);
}

// Test for division by zero and logarithm of negative number: rating ==
// rating_min, count == count_min.
UTEST(CalculatePlaceScore, CornerCase) {
  ScoreTestCase tc{
      kPlaceScoreFormula,  // formula
      3.7844,              // rating
      1,                   // count
      0.004                // expected
  };
  TestPlaceScore(tc);
}

// Test for correctness of coefficients in formula
UTEST(CalculatePlaceScore, RealData) {
  std::vector<ScoreTestCase> cases{{
                                       kPlaceScoreFormula,  // formula
                                       5,                   // rating
                                       100,                 // count
                                       0.699                // expected
                                   },
                                   {
                                       kPlaceScoreFormula,  // formula
                                       5,                   // rating
                                       50,                  // count
                                       0.450                // expected
                                   },
                                   {
                                       kPlaceScoreFormula,  // formula
                                       4,                   // rating
                                       20,                  // count
                                       0.008                // expected
                                   },
                                   {
                                       kPlaceScoreFormula,  // formula
                                       4.1,                 // rating
                                       135,                 // count
                                       0.021                // expected
                                   }};
  for (const auto& tc : cases) {
    TestPlaceScore(tc);
  }
}

// Test for correctness of calculations depending on region
UTEST(CalculatePlaceScore, RegionalLeftAndRight) {
  std::vector<ScoreTestCase> cases{
      // Left tail
      {
          kPlaceScoreFormula,  // formula
          5,                   // rating
          100,                 // count
          0.701,               // expected
          false,               // is_favorite
          kFavoritesFormula,   // favorites
          "1"                  // region_id
      },
      {
          kPlaceScoreFormula,  // formula
          5,                   // rating
          50,                  // count
          0.492,               // expected
          false,               // is_favorite
          kFavoritesFormula,   // favorites
          "1"                  // region_id
      },
      {
          kPlaceScoreFormula,  // formula
          4,                   // rating
          100,                 // count
          0.119,               // expected
          false,               // is_favorite
          kFavoritesFormula,   // favorites
          "1"                  // region_id
      },
      {
          kPlaceScoreFormula,  // formula
          3.9,                 // rating
          11,                  // count
          0.026,               // expected
          false,               // is_favorite
          kFavoritesFormula,   // favorites
          "1"                  // region_id
      },
      // Right tail
      {
          kPlaceScoreFormula,  // formula
          4.95,                // rating
          200,                 // count
          0.931,               // expected
          false,               // is_favorite
          kFavoritesFormula,   // favorites
          "1"                  // region_id
      },
      {
          kPlaceScoreFormula,  // formula
          3.9,                 // rating
          200,                 // count
          0.175,               // expected
          false,               // is_favorite
          kFavoritesFormula,   // favorites
          "1"                  // region_id
      },
      // Regionality does not interfere with favorites. Favorites' score is
      // multiplied by 2.
      {
          kPlaceScoreFormula,  // formula
          3.9,                 // rating
          200,                 // count
          0.175 * 2,           // expected
          true,                // is_favorite
          kFavoritesFormula,   // favorites
          "1"                  // region_id
      },
  };
  for (const auto& tc : cases) {
    TestPlaceScore(tc);
  }
}

// Test for corner cases when default formula is used
UTEST(CalculatePlaceScore, RegionalDefault) {
  // By default a single formula is used for the entire distribution, so
  // count_max should be less than count_threshold. Two cases below must produce
  // the same answer despite having different count, since min(count, count_max)
  // is used in calculations.
  std::vector<ScoreTestCase> cases{{
                                       kPlaceScoreFormula,  // formula
                                       5,                   // rating
                                       200,                 // count
                                       1.000,               // expected
                                       false,               // is_favorite
                                       kFavoritesFormula,   // favorites
                                       "__default__"        // region_id
                                   },
                                   {
                                       kPlaceScoreFormula,  // formula
                                       5,                   // rating
                                       220,                 // count
                                       1.000,               // expected
                                       false,               // is_favorite
                                       kFavoritesFormula,   // favorites
                                       "__default__"        // region_id
                                   }};
  for (const auto& tc : cases) {
    TestPlaceScore(tc);
  }
}

UTEST(CalculatePlaceScore, MonotonicityOnCount) {
  const auto storage = PatchConfig();
  const auto config = storage.GetSnapshot();
  PlaceScoreFormula formula{
      config[taxi_config::EATS_CATALOG_PLACE_FORMULA_BY_REGION]
          .GetDefaultValue(),
      config[taxi_config::EATS_CATALOG_FAVORITES_FORMULA]};

  eats_catalog::models::RatingInfo info;
  info.value = 4.5;

  double prev_score = -1 * std::numeric_limits<double>::epsilon();
  for (auto count = 10; count <= 200; count++) {
    info.feedback_count = count;
    const auto score = CalculatePlaceScore(formula, info);
    EXPECT_TRUE(score > prev_score);
    prev_score = score;
  }
}

UTEST(CalculatePlaceScore, MonotonicityOnRating) {
  const auto storage = PatchConfig();
  const auto config = storage.GetSnapshot();
  PlaceScoreFormula formula{
      config[taxi_config::EATS_CATALOG_PLACE_FORMULA_BY_REGION]
          .GetDefaultValue(),
      config[taxi_config::EATS_CATALOG_FAVORITES_FORMULA]};

  eats_catalog::models::RatingInfo info;
  info.feedback_count = 100;

  double prev_score = -1 * std::numeric_limits<double>::epsilon();
  for (auto rating = 3.95; rating <= 5.0; rating += 0.05) {
    info.value = rating;
    const auto score = CalculatePlaceScore(formula, info);
    EXPECT_TRUE(score > prev_score);
    prev_score = score;
  }
}

// Apply affine transformation to favourites score
UTEST(CalculatePlaceScore, FavouritesScore) {
  const double favorites_scale = 2.0;
  const double favorites_bias = 0.1;
  std::string favorites = "{" +
                          fmt::format(R"(
  "favorites_scale": {},
  "favorites_bias": {}
)",
                                      favorites_scale, favorites_bias) +
                          "}";

  eats_catalog::models::RatingInfo info;
  info.value = 4.5;
  info.feedback_count = 50;

  const auto storage = PatchConfig(kPlaceScoreFormula, favorites);
  const auto config = storage.GetSnapshot();
  PlaceScoreFormula formula{
      config[taxi_config::EATS_CATALOG_PLACE_FORMULA_BY_REGION]
          .GetDefaultValue(),
      config[taxi_config::EATS_CATALOG_FAVORITES_FORMULA]};

  const auto score = CalculatePlaceScore(formula, info, false);
  const auto favorites_score = CalculatePlaceScore(formula, info, true);

  ExpectDoubleEqual(favorites_score, score * favorites_scale + favorites_bias);
}

// Favorites score does not exceed 1.0
UTEST(CalculatePlaceScore, MaximumFavouritesScore) {
  ScoreTestCase tc{
      kPlaceScoreFormula,  // formula
      5.0,                 // rating
      200,                 // count
      1.0,                 // expected
      true,                // is_favorite
      kFavoritesFormula    // favorites
  };
  TestPlaceScore(tc);
}

// Maximum score sets each threshold at the left endpoint of the respective
// segment
UTEST(CalculateZoomLevels, LeftEndpoint) {
  LevelsTestCase tc{
      kPinSizeRanges,    // ranges
      1.0,               // score
      {8.0, 12.0, 14.0}  // expected
  };
  TestZoomLevels(tc);
}

// Minimum score sets each threshold at the right endpoint of the respective
// segment
UTEST(CalculateZoomLevels, RightEndpoint) {
  LevelsTestCase tc{
      kPinSizeRanges,     // ranges
      0.0,                // score
      {13.0, 15.0, 17.0}  // expected
  };
  TestZoomLevels(tc);
}

UTEST(CalculateZoomLevels, MiddlePoint) {
  LevelsTestCase tc{
      kPinSizeRanges,     // ranges
      0.5,                // score
      {10.5, 13.5, 15.5}  // expected
  };
  TestZoomLevels(tc);
}

// Opt for the larger size if two thresholds are equal
UTEST(CalculateZoomLevels, SmallEqualsMedium) {
  LevelsTestCase tc{
      R"({
  "hidden": {
    "min": 0,
    "max": 15
  },
  "small": {
    "min": 1,
    "max": 15
  },
  "medium": {
    "min": 1,
    "max": 17
  },
  "large": {
    "min": 14,
    "max": 19
  },
  "adjacent_min_gap": 1.0
})",                             // ranges
      0.5,                       // score
      {std::nullopt, 8.0, 15.5}  // expected
  };
  TestZoomLevels(tc);
}

// Keep only large if all thresholds are equal
UTEST(CalculateZoomLevels, AllThresholdsEqual) {
  LevelsTestCase tc{
      R"({
  "hidden": {
    "min": 0,
    "max": 15
  },
  "small": {
    "min": 1,
    "max": 15
  },
  "medium": {
    "min": 1,
    "max": 15
  },
  "large": {
    "min": 1,
    "max": 19
  },
  "adjacent_min_gap": 1.0
})",                                     // ranges
      0.5,                               // score
      {std::nullopt, std::nullopt, 8.0}  // expected
  };
  TestZoomLevels(tc);
}

}  // namespace eats_catalog::algo
