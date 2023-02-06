#include <models/grocery/matching_features/path.hpp>
#include <models/grocery/reject_reason.hpp>

#include <fmt/format.h>

#include <gtest/gtest.h>

using namespace models::grocery::matching_features;
using namespace models::grocery;

const ::geometry::Position kDepotPosition{37.415 * ::geometry::lat,
                                          55.721 * geometry::lon};

const ::geometry::Position kPos0{37.46 * ::geometry::lat,
                                 55.721 * geometry::lon};

const ::geometry::Position kPos1{37.42 * ::geometry::lat,
                                 55.721 * geometry::lon};

const ::geometry::Position kPos2{37.43 * ::geometry::lat,
                                 55.721 * geometry::lon};

const ::geometry::Position kPos3{37.44 * ::geometry::lat,
                                 55.721 * geometry::lon};

const ::geometry::Position kPos4{37.45 * ::geometry::lat,
                                 55.721 * geometry::lon};

TEST(GroceryPathTest, OptimizeStraightGroceryPath) {
  Path::Container container{
      handlers::SegmentPoint{"point_id_3", "segment_id_3", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos3, std::nullopt},
      handlers::SegmentPoint{"point_id_2", "segment_id_2", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos2, std::nullopt},
      handlers::SegmentPoint{"point_id_4", "segment_id_4", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos4, std::nullopt},
      handlers::SegmentPoint{"point_id_1", "segment_id_1", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos1, std::nullopt},
  };

  Path::Container expected_container{
      handlers::SegmentPoint{"point_id_1", "segment_id_1", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos1, std::nullopt},
      handlers::SegmentPoint{"point_id_2", "segment_id_2", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos2, std::nullopt},
      handlers::SegmentPoint{"point_id_3", "segment_id_3", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos3, std::nullopt},

      handlers::SegmentPoint{"point_id_4", "segment_id_4", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos4, std::nullopt},
  };

  constexpr auto speed = 2.0;
  constexpr auto dropoff_time = std::chrono::seconds{10};
  Path path({}, container, {}, kDepotPosition, speed, dropoff_time,
            std::chrono::seconds::max(),
            ::geometry::Distance::from_value(1000000000.0), {});
  auto expected_distance_without_pull_back =
      ::geometry::SphericalProjectionDistance(kDepotPosition, kPos1) +
      ::geometry::SphericalProjectionDistance(kPos1, kPos2) +
      ::geometry::SphericalProjectionDistance(kPos2, kPos3) +
      ::geometry::SphericalProjectionDistance(kPos3, kPos4);

  auto expected_distance =
      expected_distance_without_pull_back +
      ::geometry::SphericalProjectionDistance(kPos4, kDepotPosition);

  auto expected_max_cte =
      std::chrono::seconds{static_cast<std::size_t>(
          expected_distance_without_pull_back.value() / speed)} +
      dropoff_time * 3;

  auto expected_roundtrip_eta = std::chrono::seconds{static_cast<std::size_t>(
                                    expected_distance.value() / speed)} +
                                dropoff_time * 4;

  ASSERT_NEAR(expected_distance.value(), path.GetDistance().value(), 1e-5);
  ASSERT_EQ(expected_max_cte, path.GetMaxCte());
  ASSERT_EQ(expected_roundtrip_eta, path.GetRoundtripEta());
  ASSERT_EQ(expected_container, path.GetInner());
}

TEST(GroceryPathTest, OptimizeStraightMarketPath) {
  Path::Container container{
      handlers::SegmentPoint{"point_id_3", "segment_id_3", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos3, std::nullopt},
      handlers::SegmentPoint{"point_id_2", "segment_id_2", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos2, std::nullopt},
      handlers::SegmentPoint{"point_id_4", "segment_id_4", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos4, std::nullopt},
      handlers::SegmentPoint{"point_id_1", "segment_id_1", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos1, std::nullopt},
  };

  Path::Container expected_container{
      handlers::SegmentPoint{"point_id_1", "segment_id_1", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos1, std::nullopt},
      handlers::SegmentPoint{"point_id_2", "segment_id_2", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos2, std::nullopt},
      handlers::SegmentPoint{"point_id_4", "segment_id_4", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos4, std::nullopt},
      handlers::SegmentPoint{"point_id_3", "segment_id_3", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos3, std::nullopt},
  };

  constexpr auto speed = 2.0;
  constexpr auto dropoff_time = std::chrono::seconds{10};
  Path path({}, {}, container, kDepotPosition, speed, dropoff_time,
            std::chrono::seconds::max(),
            ::geometry::Distance::from_value(1000000000.0), {});
  auto expected_distance_without_pull_back =
      ::geometry::SphericalProjectionDistance(kDepotPosition, kPos1) +
      ::geometry::SphericalProjectionDistance(kPos1, kPos2) +
      ::geometry::SphericalProjectionDistance(kPos2, kPos3) +
      ::geometry::SphericalProjectionDistance(kPos3, kPos4);

  auto expected_distance =
      expected_distance_without_pull_back +
      ::geometry::SphericalProjectionDistance(kPos4, kDepotPosition);

  // у маркетных заказов нет cte
  auto expected_max_cte = std::chrono::seconds{0};

  auto expected_roundtrip_eta = std::chrono::seconds{static_cast<std::size_t>(
                                    expected_distance.value() / speed)} +
                                dropoff_time * 4;

  ASSERT_NEAR(expected_distance.value(), path.GetDistance().value(), 1e-5);
  ASSERT_EQ(expected_max_cte, path.GetMaxCte());
  ASSERT_EQ(expected_roundtrip_eta, path.GetRoundtripEta());
  ASSERT_EQ(expected_container, path.GetInner());
}

TEST(GroceryPathTest, OptimizeStraightPath) {
  Path::Container prefix_container{{"point_id_0", "segment_id_0", 2,
                                    ::handlers::SegmentPointType::kDropoff,
                                    std::nullopt, kPos0, std::nullopt}};

  Path::Container grocery_container{
      handlers::SegmentPoint{"point_id_3", "segment_id_3", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos3, std::nullopt},
      handlers::SegmentPoint{"point_id_2", "segment_id_2", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos2, std::nullopt}};

  Path::Container market_container{
      handlers::SegmentPoint{"point_id_4", "segment_id_4", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos4, std::nullopt},
      handlers::SegmentPoint{"point_id_1", "segment_id_1", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos1, std::nullopt},
  };

  Path::Container expected_container{
      handlers::SegmentPoint{"point_id_0", "segment_id_0", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos0, std::nullopt},
      handlers::SegmentPoint{"point_id_3", "segment_id_3", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos3, std::nullopt},
      handlers::SegmentPoint{"point_id_2", "segment_id_2", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos2, std::nullopt},
      handlers::SegmentPoint{"point_id_4", "segment_id_4", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos4, std::nullopt},
      handlers::SegmentPoint{"point_id_1", "segment_id_1", 2,
                             ::handlers::SegmentPointType::kDropoff,
                             std::nullopt, kPos1, std::nullopt},
  };

  constexpr auto speed = 2.0;
  constexpr auto dropoff_time = std::chrono::seconds{10};
  Path path(prefix_container, grocery_container, market_container,
            kDepotPosition, speed, dropoff_time, std::chrono::seconds::max(),
            ::geometry::Distance::from_value(1000000000.0), {});

  auto expected_grocery_distance =
      ::geometry::SphericalProjectionDistance(kDepotPosition, kPos0) +
      ::geometry::SphericalProjectionDistance(kPos0, kPos3) +
      ::geometry::SphericalProjectionDistance(kPos3, kPos2);

  auto expected_distance =
      expected_grocery_distance +
      ::geometry::SphericalProjectionDistance(kPos2, kPos4) +
      ::geometry::SphericalProjectionDistance(kPos4, kPos1) +
      ::geometry::SphericalProjectionDistance(kPos1, kDepotPosition);

  auto expected_max_cte = std::chrono::seconds{static_cast<std::size_t>(
                              expected_grocery_distance.value() / speed)} +
                          dropoff_time * 2;

  auto expected_roundtrip_eta = std::chrono::seconds{static_cast<std::size_t>(
                                    expected_distance.value() / speed)} +
                                dropoff_time * 5;

  ASSERT_NEAR(expected_distance.value(), path.GetDistance().value(), 1e-5);
  ASSERT_EQ(expected_max_cte.count(), path.GetMaxCte().count());
  ASSERT_EQ(expected_roundtrip_eta, path.GetRoundtripEta());
  ASSERT_EQ(expected_container, path.GetInner());
}

TEST(GroceryPathTest, DistanceLimitFilter) {
  Path path(Path::Container{}, ::geometry::Distance::from_value(1000.0),
            ::geometry::Distance::from_value(2000.0),
            ::geometry::Distance::from_value(500.0), std::chrono::seconds{1200},
            std::chrono::seconds{2400});

  ASSERT_EQ(std::nullopt,
            path.Filter(filters::WeightVolumeDistanceLimits{
                1000.0, 1000.0, ::geometry::Distance::from_value(1001.0)}));
  ASSERT_EQ(reject::kDistanceLimitExceeded,
            path.Filter(filters::WeightVolumeDistanceLimits{
                1000.0, 1000.0, ::geometry::Distance::from_value(999.0)}));
}

TEST(GroceryPathTest, CteLimitFilter) {
  Path path(Path::Container{}, ::geometry::Distance::from_value(1000.0),
            ::geometry::Distance::from_value(2000.0),
            ::geometry::Distance::from_value(500.0), std::chrono::seconds{1200},
            std::chrono::seconds{2400});

  ASSERT_EQ(std::nullopt,
            path.Filter(filters::CteLimit{std::chrono::seconds{1201}}));
  ASSERT_EQ(reject::kCteLimitExceeded,
            path.Filter(filters::CteLimit{std::chrono::seconds{1199}}));
}

TEST(GroceryPathTest, DistanceDiffFilter) {
  Path path(Path::Container{}, ::geometry::Distance::from_value(1000.0),
            ::geometry::Distance::from_value(2000.0),
            ::geometry::Distance::from_value(500.0), std::chrono::seconds{1200},
            std::chrono::seconds{2400});

  ASSERT_EQ(std::nullopt, path.Filter(filters::DistanceDiffLimit{
                              ::geometry::Distance::from_value(501.0)}));

  ASSERT_EQ(reject::kDistanceDiffLimitExceeded,
            path.Filter(filters::DistanceDiffLimit{
                ::geometry::Distance::from_value(499.0)}));
}
