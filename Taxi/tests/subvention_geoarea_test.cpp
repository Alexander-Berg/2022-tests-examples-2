#include <userver/utest/utest.hpp>

#include <userver/utils/datetime.hpp>

#include <client-geoareas/models/subvention_geoarea.hpp>

namespace {

namespace cgm = client_geoareas::models;
using TimePoint = std::chrono::system_clock::time_point;

cgm::SubventionGeoarea CreateSubventionGeoarea() {
  const std::vector<std::vector<double>> polygon_as_double = {
      {60.59601292079099, 56.83302456339234},
      {60.61043247645505, 56.842621740653506},
      {60.622448772841814, 56.83048372064773},
      {60.59601292079099, 56.83302456339234}};
  std::vector<cgm::Position> polygon;
  for (const auto& pair : polygon_as_double) {
    polygon.push_back(
        cgm::Position{pair[0] * geometry::lon, pair[1] * geometry::lat});
  }
  std::vector<std::vector<cgm::Position>> polygon_set = {polygon};
  TimePoint created = utils::datetime::Stringtime("2020-08-10T12:55:00+0000");
  return cgm::SubventionGeoarea{"658a069caa4f4b2eb3206903dd7b6d73",
                                /*type=*/"",
                                "test_polygon",
                                created,
                                polygon_set,
                                {},
                                {}};
}

}  // namespace

TEST(SubventionGeoarea, GeoareaModel) {
  const cgm::SubventionGeoarea geoarea = CreateSubventionGeoarea();
  const auto& min_corner = geoarea.GetEnvelope().min_corner();
  EXPECT_NEAR(min_corner.get<0>(), 60.59601292079099, 0.001);
  EXPECT_NEAR(min_corner.get<1>(), 56.83048372064773, 0.001);
  const auto& max_corner = geoarea.GetEnvelope().max_corner();
  EXPECT_NEAR(max_corner.get<0>(), 60.622448772841814, 0.001);
  EXPECT_NEAR(max_corner.get<1>(), 56.842621740653506, 0.001);
  EXPECT_EQ(geoarea.name(), std::string("test_polygon"));
}
