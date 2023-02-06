#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>

#include <models/geometry/polygon.hpp>

using models::geometry::Point;
using models::geometry::Polygon;
using models::geometry::SerializeJson;

TEST(Polygon, Empty) {
  {
    Polygon polygon;
    EXPECT_TRUE(polygon.empty());
    EXPECT_TRUE(polygon.envelope().empty());
  }
  {
    Polygon polygon(std::vector<Point>{});
    EXPECT_TRUE(polygon.empty());
    EXPECT_TRUE(polygon.envelope().empty());
  }
  {
    Polygon polygon({{1, 1}});
    EXPECT_FALSE(polygon.empty());
    const auto& envelope = polygon.envelope();
    EXPECT_EQ(envelope.top_left, envelope.bottom_right);
  }
}

TEST(Polygon, Envelope) {
  Polygon polygon({
      {37.309394, 55.914744},
      {37.884803, 55.911659},
      {37.942481, 55.520175},
      {37.242102, 55.499913},
      {37.309394, 55.914744},
  });
  const auto& envelope = polygon.envelope();
  EXPECT_EQ(envelope.top_left, (Point{37.242102, 55.914744}));
  EXPECT_EQ(envelope.bottom_right, (Point{37.942481, 55.499913}));
}

TEST(Polygon, Contains) {
  Polygon polygon({
      {37.309394, 55.914744},
      {37.884803, 55.911659},
      {37.942481, 55.520175},
      {37.242102, 55.499913},
      {37.309394, 55.914744},
  });
  EXPECT_TRUE(polygon.Contains({37.6247406, 55.7503036}));
  EXPECT_FALSE(polygon.Contains({55.7503036, 37.6247406}));
  EXPECT_FALSE(polygon.Contains({37.8925323, 55.901111}));
  EXPECT_TRUE(polygon.Contains({37.8801727, 55.906115}));
}

TEST(Polygon, Parse) {
  const auto& value = formats::json::FromString(
      "[[37.309394, 55.914744], [37.884803, 55.911659], [37.942481, "
      "55.520175], [37.242102, 55.499913], [37.309394, 55.914744]]");
  const auto& polygon = value.As<Polygon>();
  const auto& envelope = polygon.envelope();
  EXPECT_EQ(envelope.top_left, (Point{37.242102, 55.914744}));
  EXPECT_EQ(envelope.bottom_right, (Point{37.942481, 55.499913}));
}

TEST(Polygon, Serialize) {
  Polygon polygon({
      {37.309394, 55.914744},
      {37.884803, 55.911659},
      {37.942481, 55.520175},
      {37.242102, 55.499913},
      {37.309394, 55.914744},
  });
  auto json = SerializeJson(polygon);
  EXPECT_EQ(formats::json::ToString(json.ExtractValue()),
            "[[37.309394,55.914744],[37.884803,55.911659],[37.942481,55.520175]"
            ",[37.242102,55.499913],[37.309394,55.914744]]");
}
