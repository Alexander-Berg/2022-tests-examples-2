#include <gtest/gtest.h>

#include <internal/pointwithin.hpp>

TEST(PointWithin, Naive) {
  std::vector<models::Zone> zones1 = {};

  GeoareaBase::point_t p1(100, 100), p2(0, 0);
  EXPECT_EQ(PointWithinNaive(PointWithinNaiveData(zones1)).GetZonesForPoint(p1),
            std::vector<models::Zone::id_t>());
  EXPECT_EQ(PointWithinNaive(PointWithinNaiveData(zones1)).GetZonesForPoint(p2),
            std::vector<models::Zone::id_t>());

  models::Zone::polygon_t poly;
  boost::geometry::read_wkt("POLYGON((1 1, 1 -1, -1 -1, -1 1)())", poly);
  std::vector<models::Zone> zones2 = {models::Zone("1", "name", poly)};

  EXPECT_EQ(PointWithinNaive(PointWithinNaiveData(zones2))
                .GetZonesForPoint(GeoareaBase::point_t(0, 0)),
            std::vector<models::Zone::id_t>({"1"}));
  EXPECT_EQ(PointWithinNaive(PointWithinNaiveData(zones2))
                .GetZonesForPoint(GeoareaBase::point_t(2, 2)),
            std::vector<models::Zone::id_t>({}));
}

TEST(PointWithin, Platov) {
  models::Zone::polygon_t poly1, poly2;
  boost::geometry::read_wkt(
      "POLYGON(( 39.891501534963588 47.464881234748198, 39.884322750454778 "
      "47.457882611882425, 39.886444673624709 47.457389534518008, "
      "39.892440899797101 47.463196743090684, 39.897235496330822 "
      "47.466442474996583, 39.927595716009591 47.480498123726406, "
      "39.940706353674372 47.486963695593474, 39.954954247961517 "
      "47.493973827071635, 39.967163663397308 47.500285048725956, "
      "39.964856963644479 47.501811842552065, 39.952288132200692 "
      "47.495275397248051, 39.954138856420997 47.508921750848003, "
      "39.891985525771211 47.482993188827876, 39.892114271803919 "
      "47.476563494560843, 39.903529753371316 47.4760688699021, "
      "39.904860129042653 47.472926439149219, 39.891501534963588 "
      "47.464881234748198)())",
      poly1);
  boost::geometry::read_wkt(
      "POLYGON(( 39.933789761239105 47.489855810544867, 39.927599222832775 "
      "47.486932382247204, 39.929712803536468 47.484866976029515, "
      "39.935999901467454 47.487943237907963, 39.933789761239105 "
      "47.489855810544867)())",
      poly2);
  std::vector<models::Zone> zones = {
      models::Zone("c91ed679659247649af6a1315801914e", "platov_airport", poly1),
      models::Zone("026647a462c240b3a17011945dec7a63", "platov_waiting",
                   poly2)};

  auto found = PointWithinNaive(PointWithinNaiveData(zones))
                   .GetZonesForPoint(GeoareaBase::point_t(39.9301, 47.4851));
  ASSERT_EQ(2u, found.size());
  EXPECT_LT(found[0], found[1]);
  EXPECT_EQ(found,
            std::vector<models::Zone::id_t>({zones[1].Id(), zones[0].Id()}));
}
