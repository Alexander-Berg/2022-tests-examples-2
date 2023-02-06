#include <gmock/gmock.h>

#include <vector>

#include "smart_rules/types/base_types.hpp"
#include "smart_rules/validators/exceptions.hpp"
#include "smart_rules/validators/geonode.hpp"

namespace vs = billing_subventions_x::smart_rules::validators;

using TariffZone = billing_subventions_x::types::TariffZone;

static const TariffZone kMsk{"br_root/br_russia/br_moscow"};
static const TariffZone kMskCenter{"br_root/br_russia/br_moscow/br_center"};
static const TariffZone kMskObl{"br_root/br_russia/br_moscow_obl"};

TEST(GeoNodesValidator, SilentlyPassesWhenOk) {
  auto zones = std::vector<TariffZone>{kMsk, kMskObl};
  ASSERT_NO_THROW(vs::ValidateGeoNodes(zones));
}
namespace {

void AssertInvalid(const std::vector<TariffZone>& nodes,
                   const std::string& expected) {
  try {
    vs::ValidateGeoNodes(nodes);
    FAIL();
  } catch (const vs::ValidationError& exc) {
    ASSERT_THAT(std::string(exc.what()), ::testing::Eq(expected));
  }
}

}  // namespace

TEST(GeoNodesValidator, ThrowsExceptionWhenGeoNodeSetTwice) {
  auto nodes = std::vector<TariffZone>{kMsk, kMskObl, kMsk};
  AssertInvalid(nodes, "br_root/br_russia/br_moscow: geonodes must be unique.");
}

TEST(GeoNodesValidator, ThrowsExceptionWhenThereIsSubNode) {
  auto nodes = std::vector<TariffZone>{kMsk, kMskObl, kMskCenter};
  AssertInvalid(nodes,
                "br_root/br_russia/br_moscow/br_center: subnodes forbidden "
                "when node (br_root/br_russia/br_moscow) is set.");
}

TEST(GeoNodesValidator, ThrowsExceptionWhenNodeHasSlashOnEdges) {
  auto nodes = std::vector<TariffZone>{TariffZone{"x/"}, TariffZone{"/y"}};
  AssertInvalid(nodes, "x/, /y: nodes must not start or end with slash.");
}
