#include "utils.hpp"

#include <userver/utest/utest.hpp>

namespace utils {

namespace {

const rules_match::RulesMatchBase::DataId kDiscountId(1);
const rules_match::RulesMatchBase::DataId kNewDiscountId(2);

discounts::models::LazyData<DiscountUsages> GetLazyData() {
  DiscountUsages kDiscountUsages{{kDiscountId.GetUnderlying(), 2}};
  discounts::models::LazyData<DiscountUsages> discount_usages(kDiscountUsages);
  return discount_usages;
}

}  // namespace

UTEST(IsRestrictedByUsages, NewDiscount) {
  handlers::DiscountUsageRestriction restriction;
  restriction.max_count = 1;
  EXPECT_FALSE(IsRestrictedByUsages(kNewDiscountId, GetLazyData(),
                                    std::vector{restriction}));
}

UTEST(IsRestrictedByUsages, NotRestricted) {
  handlers::DiscountUsageRestriction restriction;
  restriction.max_count = 3;
  EXPECT_FALSE(IsRestrictedByUsages(kDiscountId, GetLazyData(),
                                    std::vector{restriction}));
}

UTEST(IsRestrictedByUsages, Restricted) {
  handlers::DiscountUsageRestriction restriction;
  restriction.max_count = 1;
  EXPECT_TRUE(IsRestrictedByUsages(kDiscountId, GetLazyData(),
                                   std::vector{restriction}));
}

UTEST(IsRestrictedByUsages, DoesNotHaveRestriction) {
  EXPECT_FALSE(IsRestrictedByUsages(kDiscountId, GetLazyData(), std::nullopt));
}

UTEST(IsRestrictedByUsages, DoesNotHaveDiscountUsages) {
  handlers::DiscountUsageRestriction restriction;
  restriction.max_count = 1;
  discounts::models::LazyData<DiscountUsages> discount_usages(
      []() -> std::optional<DiscountUsages> { return std::nullopt; });
  EXPECT_TRUE(IsRestrictedByUsages(kDiscountId, discount_usages,
                                   std::vector{restriction}));
}

}  // namespace utils
