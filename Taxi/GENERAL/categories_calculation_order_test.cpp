#include <userver/utest/utest.hpp>

#include "categories_calculation_order.hpp"

namespace {

struct AppendDepsTestData {
  std::unordered_set<std::string> categories;
  std::vector<std::string> categories_calculation_order;
  std::unordered_set<std::string> expected_result;
};

class AppendDepsTest : public ::testing::TestWithParam<AppendDepsTestData> {};

}  // namespace

TEST_P(AppendDepsTest, AppendDependenciesToCategories) {
  using utils::prepare::AppendDependenciesToCategories;

  EXPECT_EQ(AppendDependenciesToCategories(
                GetParam().categories, GetParam().categories_calculation_order),
            GetParam().expected_result);
}

INSTANTIATE_TEST_SUITE_P(
    AppendDepsTest, AppendDepsTest,
    ::testing::Values(
        AppendDepsTestData{
            {"comfortplus"},
            {"econom", "business", "comfortplus", "vip", "ultima"},
            {"econom", "business", "comfortplus"}},
        AppendDepsTestData{
            {"econom", "comfortplus", "uberx"},
            {"econom", "business", "comfortplus", "vip", "ultima"},
            {"econom", "business", "comfortplus", "uberx"}},
        AppendDepsTestData{
            {}, {"econom", "business", "comfortplus", "vip", "ultima"}, {}},
        AppendDepsTestData{
            {"uberx"},
            {"econom", "business", "comfortplus", "vip", "ultima"},
            {"uberx"}},
        AppendDepsTestData{
            {"business", "ultima", "uberx"},
            {"econom", "business", "comfortplus", "vip", "ultima"},
            {"econom", "business", "comfortplus", "vip", "ultima", "uberx"}}));
