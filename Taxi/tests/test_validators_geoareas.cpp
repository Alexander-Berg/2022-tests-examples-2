#include <gmock/gmock.h>

#include <vector>

#include "smart_rules/types/base_types.hpp"
#include "smart_rules/validators/exceptions.hpp"
#include "smart_rules/validators/geoarea.hpp"

namespace vs = billing_subventions_x::smart_rules::validators;

using GeoArea = billing_subventions_x::types::GeoArea;

static const GeoArea kButovo{"butovo"};
static const GeoArea kChertanovo{"chertanovo"};

TEST(GeoAreasValidator, SilentlyPassesWhenOk) {
  auto geoareas = std::vector<GeoArea>{kButovo, kChertanovo};
  ASSERT_NO_THROW(vs::ValidateGeoAreas(geoareas));
}

namespace {

void AssertInvalid(const std::vector<GeoArea>& geoareas,
                   const std::string& expected) {
  try {
    vs::ValidateGeoAreas(geoareas);
    FAIL();
  } catch (const vs::ValidationError& exc) {
    ASSERT_THAT(std::string(exc.what()), ::testing::Eq(expected));
  }
}

}  // namespace

TEST(GeoAreasValidator, ThrowsExceptionWhenGeoAreaSetTwice) {
  auto geoareas = std::vector<GeoArea>{kButovo, kChertanovo, kButovo};
  AssertInvalid(geoareas, "butovo: geoareas must be unique.");
}
