#include <gtest/gtest.h>

#include <boost/geometry/algorithms/distance.hpp>
#include <internal/carstates.hpp>
#include <models/zone.hpp>
#include <mongo/names/geofence_zones.hpp>

using namespace models;

TEST(Zone, Ctr) {
  Zone z("1", "name", Zone::polygon_t());

  EXPECT_EQ(z.Id(), "1");
  EXPECT_EQ(z.Name(), "name");
  EXPECT_EQ(z.Areas(), std::vector<GeoareaBase>({Zone::polygon_t()}));
}

TEST(Zone, FromJsonStringThrow1) {
  Zone z = Zone::FromJsonStringThrow(
      "{\"geometry\": {\"type\": \"MultiPolygon\", \"coordinates\": [[[]]]}, "
      "\"name\": \"123\"}");

  EXPECT_EQ(z.Name(), "123");
  EXPECT_EQ(z.Type(), "");
  EXPECT_EQ(z.Areas(), std::vector<GeoareaBase>({Zone::polygon_t()}));
}

TEST(Zone, FromJsonStringType) {
  Zone z = Zone::FromJsonStringThrow(
      "{\"geometry\": {\"type\": \"MultiPolygon\", \"coordinates\": [[[]]]}, "
      "\"name\": \"123\", \"type\": \"airport\"}");

  EXPECT_EQ(z.Name(), "123");
  EXPECT_EQ(z.Type(), "airport");
  EXPECT_EQ(z.Areas(), std::vector<GeoareaBase>({Zone::polygon_t()}));
}

TEST(Zone, FromJsonStringThrow2) {
  Zone z = Zone::FromJsonStringThrow(
      "{\"geometry\": {\"type\": \"MultiPolygon\", \"coordinates\": [[[[0.0, "
      "1.2], [1.3, 2.4]]]]}, "
      "\"name\": \"name\"}");

  Zone::polygon_t polygon;
  boost::geometry::append(polygon, Geoarea::point_t(0.0, 1.2));
  boost::geometry::append(polygon, Geoarea::point_t(1.3, 2.4));

  EXPECT_EQ(z.Name(), "name");
  EXPECT_EQ(z.Areas(), std::vector<GeoareaBase>({polygon}));
}

TEST(Zone, FromJsonStringThrow3) {
  Zone z = Zone::FromJsonStringThrow(
      "{\"geometry\": {\"type\":\"MultiPolygon\", \"coordinates\": [[[[0.0, "
      "1.2], [1.3, 2.4]]], "
      "[[[4.4, 5.5], [6.6, 7.7]]]]}, "
      "\"name\": \"name\"}");

  Zone::polygon_t polygon1, polygon2;
  boost::geometry::append(polygon1, Geoarea::point_t(0.0, 1.2));
  boost::geometry::append(polygon1, Geoarea::point_t(1.3, 2.4));

  boost::geometry::append(polygon2, Geoarea::point_t(4.4, 5.5));
  boost::geometry::append(polygon2, Geoarea::point_t(6.6, 7.7));

  EXPECT_EQ(z.Name(), "name");
  EXPECT_EQ(z.Areas(), std::vector<GeoareaBase>({polygon1, polygon2}));
}

using namespace utils::mongo::db::geofence::geozones;
using mongo::BSONArrayBuilder;

TEST(Zone, toBSON1) {
  Zone z("1", "name", Zone::polygon_t());
  z.SetType("type1");

  EXPECT_EQ(
      BSON(kName << "name" << kAreas
                 << BSON_ARRAY(BSON(kShell << BSONArrayBuilder().arr() << kHoles
                                           << BSONArrayBuilder().arr()))
                 << "removed" << false << "zone_type"
                 << "type1"),
      z.toBSON());
}

TEST(Zone, toBSON2) {
  Zone::polygon_t polygon;
  boost::geometry::append(polygon, Geoarea::point_t(0.0, 1.2));
  boost::geometry::append(polygon, Geoarea::point_t(1.3, 2.4));
  Zone z("1", "name", polygon);

  auto shell = BSON_ARRAY(BSON_ARRAY(0.0 << 1.2) << BSON_ARRAY(1.3 << 2.4));
  EXPECT_EQ(BSON(kName << "name" << kAreas
                       << BSON_ARRAY(BSON(kShell << shell << kHoles
                                                 << BSONArrayBuilder().arr()))
                       << "removed" << false << "zone_type"
                       << ""),
            z.toBSON());
}

TEST(Zone, toBSON3) {
  Zone::polygon_t polygon1, polygon2;
  boost::geometry::append(polygon1, Geoarea::point_t(0.0, 1.2));
  boost::geometry::append(polygon1, Geoarea::point_t(1.3, 2.4));

  boost::geometry::append(polygon2, Geoarea::point_t(2.2, 3.3));
  boost::geometry::append(polygon2, Geoarea::point_t(567.22, 456.22));
  Zone z("1", "name", std::vector<Zone::polygon_t>({polygon1, polygon2}));

  auto shell1 = BSON_ARRAY(BSON_ARRAY(0.0 << 1.2) << BSON_ARRAY(1.3 << 2.4));
  auto shell2 =
      BSON_ARRAY(BSON_ARRAY(2.2 << 3.3) << BSON_ARRAY(567.22 << 456.22));
  EXPECT_EQ(
      BSON(kName << "name" << kAreas
                 << BSON_ARRAY(BSON(kShell << shell1 << kHoles
                                           << BSONArrayBuilder().arr())
                               << BSON(kShell << shell2 << kHoles
                                              << BSONArrayBuilder().arr()))
                 << "removed" << false << "zone_type"
                 << ""),
      z.toBSON());
}

TEST(Zone, toBsonFromBson) {
  Zone::polygon_t polygon;
  boost::geometry::append(polygon, Geoarea::point_t(0.0, 1.2));
  boost::geometry::append(polygon, Geoarea::point_t(1.3, 2.4));
  Zone z("", "name", polygon);
  z.SetType("type_x");

  auto parsed = ParseZone(z.toBSON());
  EXPECT_EQ(z, parsed);
}

TEST(Zone, toBsonFromBson2) {
  Zone::polygon_t polygon1, polygon2;
  boost::geometry::append(polygon1, Geoarea::point_t(0.0, 1.2));
  boost::geometry::append(polygon1, Geoarea::point_t(1.3, 2.4));

  boost::geometry::append(polygon2, Geoarea::point_t(2.2, 3.3));
  boost::geometry::append(polygon2, Geoarea::point_t(567.22, 456.22));
  Zone z("", "name", std::vector<Zone::polygon_t>({polygon1, polygon2}));

  EXPECT_EQ(ParseZone(z.toBSON()), z);
}
