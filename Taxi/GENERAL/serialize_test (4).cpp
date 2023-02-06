#include <gtest/gtest.h>

#include <models/geometry/serialize.hpp>

using formats::json::ValueBuilder;
using models::geometry::Point;
using models::geometry::SerializeJson;
using models::geometry::Viewport;

TEST(Point, Serialize) {
  ValueBuilder json = SerializeJson(Point{1.0, 2.0});

  Point p;
  ASSERT_NO_THROW(p = json.ExtractValue().As<Point>());
  EXPECT_EQ(p.lon, 1.0);
  EXPECT_EQ(p.lat, 2.0);
}

TEST(Point, SerializeError) {
  ValueBuilder json;
  EXPECT_ANY_THROW(ValueBuilder(json).ExtractValue().As<Point>());
  json.PushBack(1.0);
  EXPECT_ANY_THROW(ValueBuilder(json).ExtractValue().As<Point>());
  json.PushBack(2.0);
  EXPECT_NO_THROW(ValueBuilder(json).ExtractValue().As<Point>());
  json.PushBack(3.0);
  EXPECT_ANY_THROW(ValueBuilder(json).ExtractValue().As<Point>());
}

TEST(Viewport, Serialize) {
  ValueBuilder json(Viewport{{1.0, 4.0}, {2.0, 3.0}});
  Viewport viewport;
  ASSERT_NO_THROW(viewport = json.ExtractValue().As<Viewport>());
  EXPECT_EQ(viewport.top_left, (Point{1.0, 4.0}));
  EXPECT_EQ(viewport.bottom_right, (Point{2.0, 3.0}));
}
