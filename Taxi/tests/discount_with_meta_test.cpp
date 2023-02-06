#include <gtest/gtest.h>

#include <applicators/cart.hpp>
#include <eats-discounts-applicator/delivery_applyer.hpp>
#include <tests/utils.hpp>

#include <experiments3.hpp>

namespace eats_discounts_applicator::tests {

namespace discount_with_meta {

namespace {

struct TestParams {
  discounts_client::V2MatchedMoneyProductDiscount discount;
  impl::DiscountWithMeta<discounts_client::V2MatchedMoneyProductDiscount>::Meta
      exp_meta;
  bool exp_valid;
  std::string test_name;
};

class TestDiscountWithMeta : public testing::TestWithParam<TestParams> {};

std::string PrintToString(const TestParams& params) { return params.test_name; }

inline const std::string kPromoType = "promo_type";
inline const std::string kHierarchyName = "hierarchy_name";

inline const std::unordered_map<
    std::string, experiments3::eats_discounts_promo_types_info::PromoTypeInfo>
    kTestPromoTypes{
        {kPromoType, {"default_name", "default_descr", "default_picture"}},
    };

const std::vector<TestParams> kBasicTestParams = {
    {
        MakeV2MenuDiscount(
            DiscountType::AbsoluteValue, "50", std::nullopt /*max_disc*/,
            std::nullopt /*promotype*/, std::nullopt /*promo_info*/),
        {},
        false,
        "bad_old_promo_info",
    },
    {
        MakeV2MenuDiscount(DiscountType::AbsoluteValue),
        {"name", "descr", "picture_uri", kHierarchyName, impl::kMoneyTypeId,
         impl::DiscountTypeForThreshold::kOther, impl::kMoneyTypeName,
         std::nullopt},
        true,
        "old_way_without_promo_type",
    },
    {
        MakeV2MenuDiscount(DiscountType::AbsoluteValue, "50",
                           std::nullopt /*max_disc*/,
                           "not_existing_promo" /*promotype*/),
        {"name", "descr", "picture_uri", "not_existing_promo",
         impl::kMoneyTypeId, impl::DiscountTypeForThreshold::kOther,
         impl::kMoneyTypeName, std::nullopt},
        true,
        "not_matched_promo_type_with_fallback",
    },
    {
        MakeV2MenuDiscount(
            DiscountType::AbsoluteValue, "50", std::nullopt /*max_disc*/,
            "not_existing_promo" /*promotype*/,
            CustomPromoInfo{std::nullopt /*name*/, "descr", "picture"}),
        {},
        false,
        "not_matched_promo_type_without_fallback",
    },
    {
        MakeV2MenuDiscount(DiscountType::AbsoluteValue, "50",
                           std::nullopt /*max_disc*/, kPromoType /*promotype*/),
        {"name", "descr", "picture_uri", kPromoType, impl::kMoneyTypeId,
         impl::DiscountTypeForThreshold::kOther, impl::kMoneyTypeName,
         std::nullopt},
        true,
        "rewrite_promo_info",
    },
    {
        MakeV2MenuDiscount(
            DiscountType::AbsoluteValue, "50", std::nullopt /*max_disc*/,
            kPromoType /*promotype*/,
            CustomPromoInfo{
                "custom_name", std::nullopt /*description*/,
                std::nullopt /*picture_uri*/} /*custom_promo_info*/),
        {"custom_name", "default_descr", "default_picture", kPromoType,
         impl::kMoneyTypeId, impl::DiscountTypeForThreshold::kOther,
         impl::kMoneyTypeName, std::nullopt},
        true,
        "part_rewrite_promo_info_name",
    },
    {
        MakeV2MenuDiscount(
            DiscountType::AbsoluteValue, "50", std::nullopt /*max_disc*/,
            kPromoType /*promotype*/,
            CustomPromoInfo{
                std::nullopt /*name*/, "custom_descr",
                std::nullopt /*picture_uri*/} /*custom_promo_info*/),
        {"default_name", "custom_descr", "default_picture", kPromoType,
         impl::kMoneyTypeId, impl::DiscountTypeForThreshold::kOther,
         impl::kMoneyTypeName, std::nullopt},
        true,
        "part_rewrite_promo_info_descr",
    },
    {
        MakeV2MenuDiscount(
            DiscountType::AbsoluteValue, "50", std::nullopt /*max_disc*/,
            kPromoType /*promotype*/,
            CustomPromoInfo{std::nullopt /*name*/, std::nullopt /*description*/,
                            "custom_picture"} /*custom_promo_info*/),
        {"default_name", "default_descr", "custom_picture", kPromoType,
         impl::kMoneyTypeId, impl::DiscountTypeForThreshold::kOther,
         impl::kMoneyTypeName, std::nullopt},
        true,
        "part_rewrite_promo_info_picture",
    },
    {
        MakeV2MenuDiscount(DiscountType::AbsoluteValue, "50",
                           std::nullopt /*max_disc*/, kPromoType /*promotype*/,
                           std::nullopt /*promo_info*/),
        {"default_name", "default_descr", "default_picture", kPromoType,
         impl::kMoneyTypeId, impl::DiscountTypeForThreshold::kOther,
         impl::kMoneyTypeName, std::nullopt},
        true,
        "promo_info_from_promo_type",
    },
};

}  // namespace

TEST_P(TestDiscountWithMeta, BasicTest) {
  const auto params = GetParam();
  impl::DiscountWithMeta discount_with_meta(params.discount, kTestPromoTypes,
                                            kHierarchyName);
  EXPECT_EQ(discount_with_meta.IsValid(), params.exp_valid);
  if (discount_with_meta.IsValid()) {
    const auto& meta = discount_with_meta.GetMeta();
    EXPECT_EQ(meta.name, params.exp_meta.name);
    EXPECT_EQ(meta.description, params.exp_meta.description);
    EXPECT_EQ(meta.picture_uri, params.exp_meta.picture_uri);
    EXPECT_EQ(meta.promo_type, params.exp_meta.promo_type);
  }
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestDiscountWithMeta,
                         testing::ValuesIn(kBasicTestParams),
                         testing::PrintToStringParamName());

}  // namespace discount_with_meta

}  // namespace eats_discounts_applicator::tests
