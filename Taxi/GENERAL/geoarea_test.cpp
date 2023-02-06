#include <gtest/gtest.h>

#include <client-geoareas-base/models/geoarea.hpp>

using namespace ::geometry::literals;
using Position = ::geometry::Position;
using Geoarea = client_geoareas_base::models::Geoarea;

TEST(PolygonDistance, Point) {
  const std::vector<Position> vko_polygon = {
      {37.2324_lon, 55.5772_lat},       {37.2299_lon, 55.5917_lat},
      {37.2299_lon, 55.5917000001_lat}, {37.2461_lon, 55.6057_lat},
      {37.2796999999_lon, 55.6257_lat}, {37.2797000001_lon, 55.6257_lat},
      {37.3188_lon, 55.5969_lat},       {37.2324_lon, 55.5772_lat},
  };
  const Geoarea geoarea("id", "type", "name", std::chrono::system_clock::now(),
                        {vko_polygon}, {}, {});

  const Geoarea::point_t inside{37.27339925829745, 55.60198676141709};
  EXPECT_TRUE(geoarea.IntersectsCircle(inside, 0));

  const Geoarea::point_t border(37.2299, 55.5917);
  EXPECT_TRUE(geoarea.IntersectsCircle(border, 0.5));

  // svo - vko distance is about 46km
  const Geoarea::point_t svo_point{37.41392866129457, 55.98194383103484};
  EXPECT_TRUE(geoarea.IntersectsCircle(svo_point, 50000));
  EXPECT_FALSE(geoarea.IntersectsCircle(svo_point, 40000));
}
