#include <gtest/gtest.h>

#include "utils/geometry.hpp"

TEST(utils, geometry) {
  EXPECT_EQ(utils::geometry::СalcAzimuthRoughly(
                utils::geometry::Point{37.4468, 55.7568},
                utils::geometry::Point{37.4468, 56.7568}),
            0);
  EXPECT_EQ(utils::geometry::СalcAzimuthRoughly(
                utils::geometry::Point{37.4468, 55.7568},
                utils::geometry::Point{38.4468, 55.7568}),
            90);
  EXPECT_EQ(utils::geometry::СalcAzimuthRoughly(
                utils::geometry::Point{37.4468, 55.7568},
                utils::geometry::Point{37.4468, 54.7568}),
            180);
}

const double kDistanceEpsilon = 1e-4;

TEST(PickupModel, calc_distance_to_segment_common) {
  // https://static-maps.yandex.ru/1.x/?l=map&lang=ru_RU&ll=37.539819441192556%2C55.743370155419896&origin=jsapi-constructor&pl=c%3Aed4543e6%2Cw%3A5%2C37.53739472424317%2C55.74335805113156%2C37.54082795178223%2C55.74415692888691&pt=37.54003401791374%2C55.74276493426189%2Cpm2bll&size=500%2C400&z=16
  utils::geometry::Point a{37.53739472424317, 55.74335805113156};
  utils::geometry::Point b{37.54082795178223, 55.74415692888691};
  utils::geometry::Point p{37.54003401791374, 55.74276493426189};

  EXPECT_NEAR(128.4693, utils::geometry::CalcDistanceToSegment(p, a, b),
              kDistanceEpsilon);
  EXPECT_NEAR(128.4693, utils::geometry::CalcDistanceToSegment(p, b, a),
              kDistanceEpsilon);
}

TEST(PickupModel, calc_distance_to_segment_point_in_segment) {
  // https://static-maps.yandex.ru/1.x/?l=map&lang=ru_RU&ll=37.539819441192556%2C55.743370155419896&origin=jsapi-constructor&pl=c%3Aed4543e6%2Cw%3A5%2C37.53739472424317%2C55.74335805113156%2C37.54082795178223%2C55.74415692888691&pt=37.54003401791374%2C55.74276493426189%2Cpm2bll&size=500%2C400&z=16
  utils::geometry::Point a{37.53739472424317, 55.74335805113156};
  utils::geometry::Point b{37.54082795178223, 55.74415692888691};
  utils::geometry::Point p{37.53739472424317, 55.74335805113156};

  EXPECT_NEAR(0.0, utils::geometry::CalcDistanceToSegment(p, a, b),
              kDistanceEpsilon);
  EXPECT_NEAR(0.0, utils::geometry::CalcDistanceToSegment(p, b, a),
              kDistanceEpsilon);
}

TEST(PickupModel, calc_distance_to_segment_projection_out_of_segment) {
  // https://static-maps.yandex.ru/1.x/?l=map&lang=ru_RU&ll=37.5369655708007%2C55.74333384241571&origin=jsapi-constructor&pl=c%3Aed4543e6%2Cw%3A5%2C37.53739472424317%2C55.74335805113156%2C37.54082795178223%2C55.74415692888691&pt=37.53394003903043%2C55.74259546932306%2Cpm2bll&size=500%2C400&z=16
  // utils::geometry::Point a{37.53739472424317,55.74335805113156};
  utils::geometry::Point a{37.53739472424317, 55.74335805113156};
  utils::geometry::Point b{37.54082795178223, 55.74415692888691};
  utils::geometry::Point p{37.53394003903043, 55.74259546932306};

  EXPECT_NEAR(232.3337, utils::geometry::CalcDistanceToSegment(p, a, b),
              kDistanceEpsilon);
  EXPECT_NEAR(232.3337, utils::geometry::CalcDistanceToSegment(p, b, a),
              kDistanceEpsilon);
}

TEST(PickupModel, convex_polygon) {
  // https://static-maps.yandex.ru/1.x/?l=map&lang=ru_RU&ll=37.15175744091788%2C55.90198726133497&origin=jsapi-constructor&pl=c%3Aed4543e6%2Cf%3Aed454399%2Cw%3A5%2C37.038117609374986%2C55.93553344495757%2C37.20565911328124%2C55.937075097294915%2C37.20565911328124%2C55.863006264633%2C37.03537102734374%2C55.86377854710077%2C37.038117609374986%2C55.93553344495757&pt=37.26745720898437%2C55.897743713698766%2Cpm2bll~37.04910393749999%2C55.864550814117806%2Cpm2bll&size=500%2C400&z=11
  std::vector<utils::geometry::Point> polygon{
      {37.038117609374986, 55.93553344495757},
      {37.20565911328124, 55.937075097294915},
      {37.20565911328124, 55.863006264633},
      {37.03537102734374, 55.86377854710077}};

  ASSERT_FALSE(utils::geometry::PointInPolygon(
      {37.26745720898437, 55.897743713698766}, polygon));
  ASSERT_TRUE(utils::geometry::PointInPolygon(
      {37.04910393749999, 55.864550814117806}, polygon));
  // point from border
  ASSERT_TRUE(utils::geometry::PointInPolygon(
      {37.03537102734374, 55.86377854710077}, polygon));
}

TEST(PickupModel, non_convex_polygon) {
  // https://static-maps.yandex.ru/1.x/?l=map&lang=ru_RU&ll=37.250402367628084%2C55.7946750436679&origin=jsapi-constructor&pl=c%3Aed4543e6%2Cf%3Aed454399%2Cw%3A5%2C37.13562127148438%2C55.74931292653505%2C37.18917962109374%2C55.8506476480836%2C37.33886834179688%2C55.83905785958948%2C37.23999138867186%2C55.757057740108934%2C37.23724480664062%2C55.83364810401016%2C37.13562127148438%2C55.74931292653505&pt=37.255097589843736%2C55.789195947780705%2Cpm2bll~37.29160109809687%2C55.7702972887989%2Cpm2bll&size=600%2C450&z=11
  std::vector<utils::geometry::Point> polygon{
      {37.13562127148438, 55.74931292653505},
      {37.18917962109374, 55.8506476480836},
      {37.33886834179688, 55.83905785958948},
      {37.23999138867186, 55.757057740108934},
      {37.23724480664062, 55.83364810401016}};

  ASSERT_TRUE(utils::geometry::PointInPolygon(
      {37.255097589843736, 55.789195947780705}, polygon));
  ASSERT_FALSE(utils::geometry::PointInPolygon(
      {37.29160109809687, 55.7702972887989}, polygon));
  // point from border
  ASSERT_TRUE(utils::geometry::PointInPolygon(
      {37.23724480664062, 55.83364810401016}, polygon));
}
