#include <gmock/gmock.h>

#include <vector>

#include "smart_rules/types/base_types.hpp"
#include "smart_rules/validators/exceptions.hpp"
#include "smart_rules/validators/tariff_class.hpp"

namespace vs = billing_subventions_x::smart_rules::validators;

using TariffClass = billing_subventions_x::types::TariffClass;

static const TariffClass kEconom{"econom"};
static const TariffClass kBusiness{"business"};

TEST(TariffClassesValidator, SilentlyPassesWhenOk) {
  auto tariffs = std::vector<TariffClass>{kEconom, kBusiness};
  ASSERT_NO_THROW(vs::ValidateTariffClasses(tariffs));
}

namespace {

void AssertInvalid(const std::vector<TariffClass>& tariffs,
                   const std::string& expected) {
  try {
    vs::ValidateTariffClasses(tariffs);
    FAIL();
  } catch (const vs::ValidationError& exc) {
    ASSERT_THAT(std::string(exc.what()), ::testing::Eq(expected));
  }
}

}  // namespace

TEST(TariffClassesValidator, ThrowsExceptionWhenTariffClassSetTwice) {
  auto tariffs = std::vector<TariffClass>{kEconom, kBusiness, kEconom};
  AssertInvalid(tariffs, "econom: tariff classes must be unique.");
}
