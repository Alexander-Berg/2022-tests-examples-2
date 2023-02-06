#include <userver/utest/utest.hpp>

#include <geometry/distance.hpp>

#include "route_prediction.hpp"
#include "route_prediction_impl.hpp"

namespace masstransit::route_prediction {

using namespace geometry::literals;

TEST(RoutePrediction, AdvanceFraction) {
  geometry::Position a0{0._lon, 0._lat};
  geometry::Position a1{1._lon, 1._lat};
  EXPECT_TRUE(
      geometry::AreClosePositions(impl::AdvanceFraction(a0, a1, 0), a0));
  EXPECT_TRUE(
      geometry::AreClosePositions(impl::AdvanceFraction(a0, a1, 1), a1));
  EXPECT_TRUE(geometry::AreClosePositions(impl::AdvanceFraction(a0, a1, 0.5),
                                          {.5_lon, .5_lat}));
}

TEST(RoutePrediction, AdvanceDistance) {
  geometry::Position a0{0._lon, 0._lat};
  geometry::Position a1{1._lon, 1._lat};
  EXPECT_TRUE(geometry::AreClosePositions(
      impl::AdvanceDistance(a0, a1,
                            geometry::GreatCircleDistance(a0, a1) * 0.5),
      {.5_lon, .5_lat}));
}

TEST(RoutePrediction, Project) {
  geometry::Position a0{0._lon, 0._lat};
  geometry::Position a1{1._lon, 1._lat};
  {
    const auto dist = impl::Project(a0, a1, 1337, {0._lon, 1._lat});
    EXPECT_TRUE(
        geometry::AreClosePositions(dist.proj, {.5_lon, .5_lat}, /*eps*/ 0.001))
        << dist.proj << " " << a1;
    EXPECT_EQ(dist.segment_idx, 1337);
    EXPECT_NEAR(dist.t, 0.5, 0.01);
  }
  {
    const auto dist = impl::Project(a0, a1, 1337, {0._lon, 2._lat});
    EXPECT_TRUE(geometry::AreClosePositions(dist.proj, a1, /*eps*/ 0.001))
        << dist.proj << " " << a1;
    EXPECT_EQ(dist.segment_idx, 1337);
    EXPECT_NEAR(dist.t, 1, 0.01);
  }
}

TEST(RoutePrediction, Advancer) {
  std::vector<geometry::Position> polyline{
      {0._lon, 0._lat},
      {0._lon, 1._lat},
      {1._lon, 1._lat},
  };
  impl::Advancer adv{polyline, /*is_cyclic*/ false, /*i*/ 0, /*adv_dist*/ 0};
  {
    const auto pos_azi = adv.Get();
    EXPECT_TRUE(geometry::AreClosePositions(pos_azi.position, polyline[0]));
    EXPECT_EQ(pos_azi.azimuth, 0);
  }

  geometry::Position stop1{0._lon, 0.5_lat};
  const auto dist_0_stop1 = geometry::GreatCircleDistance(polyline[0], stop1);
  const auto dist_0_1 = geometry::GreatCircleDistance(polyline[0], polyline[1]);
  const auto dist_1_2 = geometry::GreatCircleDistance(polyline[1], polyline[2]);
  const auto dist_2_0 = geometry::GreatCircleDistance(polyline[2], polyline[0]);

  adv.adv_dist += dist_0_stop1;
  adv.Normalize();
  ASSERT_EQ(adv.i, 0);
  EXPECT_EQ(adv.adv_dist, dist_0_stop1);
  {
    const auto pos_azi = adv.Get();
    EXPECT_TRUE(geometry::AreClosePositions(pos_azi.position, stop1));
    EXPECT_EQ(pos_azi.azimuth, 0);
  }

  adv.adv_dist += dist_0_1 - dist_0_stop1;
  adv.Normalize();
  ASSERT_TRUE(adv.i == 0 || adv.i == 1);
  if (adv.i == 0) {
    EXPECT_EQ(adv.adv_dist, dist_0_1);
  } else {
    EXPECT_EQ(adv.adv_dist, geometry::Distance{0});
  }
  {
    const auto pos_azi = adv.Get();
    EXPECT_TRUE(geometry::AreClosePositions(pos_azi.position, polyline[1]));
  }

  adv.adv_dist += geometry::Distance::from_value(200500);
  adv.Normalize();
  ASSERT_EQ(adv.i, 1);
  EXPECT_EQ(adv.adv_dist, dist_1_2);
  {
    const auto pos_azi = adv.Get();
    EXPECT_TRUE(geometry::AreClosePositions(pos_azi.position, polyline[2]));
    EXPECT_TRUE(pos_azi.azimuth == 89 || pos_azi.azimuth == 90 ||
                pos_azi.azimuth == 91)
        << pos_azi.azimuth;
  }

  adv.is_cyclic = true;
  adv.adv_dist += dist_2_0 + dist_0_stop1;
  adv.Normalize();
  ASSERT_EQ(adv.i, 0);
  EXPECT_EQ(adv.adv_dist, dist_0_stop1);
  {
    const auto pos_azi = adv.Get();
    EXPECT_TRUE(geometry::AreClosePositions(pos_azi.position, stop1));
    EXPECT_EQ(pos_azi.azimuth, 0);
  }
}

}  // namespace masstransit::route_prediction
