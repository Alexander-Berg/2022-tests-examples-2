#include <client-geoareas-base/models/geoarea.hpp>

#include <userver/dump/test_helpers.hpp>

namespace client_geoareas_base::models {

namespace {

using namespace geometry::literals;

const std::vector<Geoarea> kTestGeoareas{
    {
        "id1",
        "some_type",
        "some_name",
        /*created*/ TimePoint::min(),
        {
            // inner
            {
                {1._lon, 2._lat},
                {3._lon, 4._lat},
                {13.37_lon, 3.22_lat},
                {1._lon, 2._lat},
            },
            // outer
            {
                {.1_lon, .2_lat},
                {.3_lon, .4_lat},
                {13.37_lon, 3.22_lat},
                {.1_lon, .2_lat},
            },
        },
        {Geoarea::ZoneType::SignificantTransfer},
        /*default_point*/ std::nullopt,
        /*area*/ 42.42,
    },
    {
        "id2",
        /*type*/ "",
        "some_name2",
        /*created*/ TimePoint::max(),
        {
            {
                {1._lon, 2._lat},
                {3._lon, 4._lat},
                {13.37_lon, 3.22_lat},
                {1._lon, 2._lat},
            },
        },
        {Geoarea::ZoneType::Airport},
        /*default_point*/ {{0.42_lon, 3.0_lat}},
        /*area*/ 4.04,
    },
};

}  // namespace

TEST(ClientGeoareasBase, Dumping) {
  for (size_t i = 0; i < kTestGeoareas.size(); ++i) {
    const auto binary = dump::ToBinary(kTestGeoareas[i]);
    const auto restored = dump::FromBinary<Geoarea>(binary);
    const auto original = kTestGeoareas[i];
    EXPECT_EQ(restored.id(), original.id());
    // type and name
    EXPECT_EQ(restored.identity(), original.identity());
    EXPECT_EQ(impl::PolygonToPointVectors(restored.geometry()),
              impl::PolygonToPointVectors(original.geometry()));
    EXPECT_EQ(restored.GetZoneTypes(), original.GetZoneTypes());
    EXPECT_EQ(restored.GetDefaultPoint(), original.GetDefaultPoint());
    EXPECT_EQ(restored.area(), original.area());
  }
}

}  // namespace client_geoareas_base::models
