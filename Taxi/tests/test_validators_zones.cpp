#include <gmock/gmock.h>

#include <vector>

#include "smart_rules/types/base_types.hpp"
#include "smart_rules/validators/exceptions.hpp"
#include "smart_rules/validators/zone.hpp"

namespace vs = billing_subventions_x::smart_rules::validators;

using TariffZone = billing_subventions_x::types::TariffZone;

static const TariffZone kMsk{"msk"};
static const TariffZone kMskCenter{"msk_center"};

TEST(TariffZonesValidator, SilentlyPassesWhenOk) {
  auto zones = std::vector<TariffZone>{kMsk, kMskCenter};
  ASSERT_NO_THROW(vs::ValidateTariffZones(zones));
}

namespace {

void AssertInvalid(const std::vector<TariffZone>& zones,
                   const std::string& expected) {
  try {
    vs::ValidateTariffZones(zones);
    FAIL();
  } catch (const vs::ValidationError& exc) {
    ASSERT_THAT(std::string(exc.what()), ::testing::Eq(expected));
  }
}

}  // namespace

TEST(TariffZonesValidator, ThrowsExceptionWhenTariffZoneSetTwice) {
  auto zones = std::vector<TariffZone>{kMsk, kMskCenter, kMsk};
  AssertInvalid(zones, "msk: tariff zones must be unique.");
}
