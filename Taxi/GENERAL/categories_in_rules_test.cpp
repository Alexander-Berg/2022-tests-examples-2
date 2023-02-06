#include <gtest/gtest.h>

#include <utils/categories_in_rules.hpp>

namespace eats_menu_categories::categories_in_rules {

using CategoryId = eats_menu_categories::models::CategoryId;
using Category = eats_menu_categories::models::Category;

namespace {

struct CategoriesInRulesTestCase {
  std::string name{};
  std::vector<models::CategoryId> vector_categories{};
  std::vector<models::Category> mapping_categories{};
  std::vector<models::CategoryId> expected{};
};

}  // namespace

class CategoriesInRulesTest
    : public ::testing::TestWithParam<CategoriesInRulesTestCase> {};

TEST_P(CategoriesInRulesTest, DiffCategories) {
  auto param = GetParam();

  const auto actual =
      utils::DiffCategories(param.vector_categories, param.mapping_categories);

  ASSERT_EQ(param.expected, actual) << param.name;
}

std::vector<CategoriesInRulesTestCase> MakeCategoriesInRulesTestCases();

INSTANTIATE_TEST_SUITE_P(CategoriesInRules, CategoriesInRulesTest,
                         ::testing::ValuesIn(MakeCategoriesInRulesTestCases()),
                         [](const auto& test_case) {
                           return test_case.param.name;
                         });

std::vector<CategoriesInRulesTestCase> MakeCategoriesInRulesTestCases() {
  return {
      {"no_diff",  // name
       {CategoryId{"category-1"},
        CategoryId{"category-2"}},  // vector_categories
       {Category{CategoryId{"category-1"}},
        Category{CategoryId{"category-2"}}},  // mapping_categories
       {}},                                   // expected
      {"one_category_diff",                   // name
       {CategoryId{"category-1"},
        CategoryId{"category-2"}},            // vector_categories
       {Category{CategoryId{"category-1"}}},  // mapping_categories
       {CategoryId{"category-2"}}},           // expected
      {"one_else_diff",                       // name
       {CategoryId{"category-1"},
        CategoryId{"category-2"},   // vector_categories
        CategoryId{"category-3"}},  // mapping_categories
       {Category{CategoryId{"category-1"}}, Category{CategoryId{"category-3"}}},
       {CategoryId{"category-2"}}},  // expected
      {"empty_second_vector",        // name
       {CategoryId{"category-1"}, CategoryId{"category-2"},
        CategoryId{"category-3"}},  // vector_categories
       {},                          // mapping_categories
       {CategoryId{"category-1"}, CategoryId{"category-2"},
        CategoryId{"category-3"}}},  // name
  };
}

}  // namespace eats_menu_categories::categories_in_rules
