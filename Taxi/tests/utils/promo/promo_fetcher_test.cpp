#include <userver/utest/utest.hpp>

#include <utils/promo/promo_fetcher.hpp>

namespace eats_restapp_promo::utils::promo::tests {

struct TestData {
  struct Data {
    models::PromoType promo_type;
  };
  std::string name;
  Data data;
  int64_t promo_id;
  bool check;
};

inline bool operator==(const TestData& lhs, const TestData& rhs) {
  return std::tie(lhs.name, lhs.data.promo_type, lhs.promo_id, lhs.check) ==
         std::tie(rhs.name, rhs.data.promo_type, rhs.promo_id, rhs.check);
}

struct ReplaceMarketingPromoData {
  std::vector<TestData> old_promos;
  std::unordered_map<int64_t, TestData> new_promos;
  std::unordered_set<std::string> enabled_promos;
  std::vector<TestData> result_promos;
};

class ReplaceMarketingPromoDataFull
    : public ::testing::TestWithParam<ReplaceMarketingPromoData> {};

const std::vector<ReplaceMarketingPromoData> kReplaceMarketingPromoData{
    {{{"name1", {models::PromoType::kGift}, 1, false},
      {"name2", {models::PromoType::kDiscount}, 2, true},
      {"name3", {models::PromoType::kGift}, 3, true}},
     {{2, {"name4", {models::PromoType::kOnePlusOne}, 2, false}},
      {3, {"name5", {models::PromoType::kDiscount}, 5, true}},
      {4, {"name6", {models::PromoType::kGift}, 4, false}},
      {5, {"name7", {models::PromoType::kOnePlusOne}, 5, false}}},
     {"gift"},
     {{"name1", {models::PromoType::kGift}, 1, false},
      {"name2", {models::PromoType::kDiscount}, 2, true},
      {"name5", {models::PromoType::kDiscount}, 5, true}}},
    {{},
     {{2, {"name4", {models::PromoType::kOnePlusOne}, 2, false}},
      {3, {"name5", {models::PromoType::kDiscount}, 5, true}},
      {4, {"name6", {models::PromoType::kGift}, 4, false}},
      {5, {"name7", {models::PromoType::kOnePlusOne}, 5, false}}},
     {"gift"},
     {}},
    {{{"name1", {models::PromoType::kGift}, 1, false},
      {"name2", {models::PromoType::kDiscount}, 2, true},
      {"name3", {models::PromoType::kGift}, 3, true}},
     {},
     {"gift"},
     {{"name1", {models::PromoType::kGift}, 1, false},
      {"name2", {models::PromoType::kDiscount}, 2, true},
      {"name3", {models::PromoType::kGift}, 3, true}}},
};

INSTANTIATE_TEST_SUITE_P(ReplaceMarketingPromoData,
                         ReplaceMarketingPromoDataFull,
                         ::testing::ValuesIn(kReplaceMarketingPromoData));

TEST_P(ReplaceMarketingPromoDataFull,
       function_should_update_old_promos_to_new_promos) {
  auto param = GetParam();
  ReplaceMarketingPromo(param.old_promos, param.new_promos,
                        param.enabled_promos);
  ASSERT_EQ(param.old_promos, param.result_promos);
}

}  // namespace eats_restapp_promo::utils::promo::tests
