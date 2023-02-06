#include <fmt/format.h>
#include <gtest/gtest.h>

#include <models/category_id.hpp>
#include <models/category_sort_order.hpp>
#include <models/nomenclature_response_mapper.hpp>
#include <models/scoring/scoring_defines.hpp>
#include <sorts/sort_categories.hpp>

namespace {

using eats_products::models::CategoriesScoringDataString;
using eats_products::models::CategoryId;
using eats_products::models::CategorySortOrder;
using eats_products::models::NomenclatureResponseMapper;

using clients::eats_nomenclature::CategoryResult;

// helper providing prettier output in the case of assertion failure
void AssertEqualCategoriesOrder(const std::vector<handlers::Category>& lhs,
                                const std::vector<handlers::Category>& rhs) {
  EXPECT_EQ(lhs.size(), rhs.size());
  for (size_t i = 0; i < lhs.size(); i++) {
    EXPECT_EQ(lhs.at(i).id, rhs.at(i).id) << "at position " << i;
  }
}

}  // namespace

namespace eats_products::tests {

class ResponseMapperForTestng {
 public:
  static void CategoriesSort(
      const std::unordered_map<CategoryId, CategorySortOrder>& sort_orders,
      std::vector<handlers::Category>& core_categories,
      const std::optional<CategoriesScoringDataString>&
          categories_scoring_data) {
    sorts::SortNomenclatureCategories(sort_orders, core_categories,
                                      categories_scoring_data);
  }
};

TEST(CategoriesSort, SortBySortOrder) {
  std::vector<handlers::Category> core_categories{{1, "1"}, {2, "2"}, {3, "3"}};
  std::unordered_map<CategoryId, CategorySortOrder> sort_orders{
      {CategoryId{"1"}, CategorySortOrder{3, false}},
      {CategoryId{"2"}, CategorySortOrder{2, false}},
      {CategoryId{"3"}, CategorySortOrder{1, false}}};

  ResponseMapperForTestng::CategoriesSort(sort_orders, core_categories,
                                          std::nullopt);

  std::vector<handlers::Category> expected_categories{{3}, {2}, {1}};
  AssertEqualCategoriesOrder(core_categories, expected_categories);
}

TEST(CategoriesSort, SortBySortOrderWithDepth) {
  // Category { id, parent_id }
  std::vector<handlers::Category> core_categories{
      {1, "1"}, {2, "2"}, {3, "3", 1, "1"}, {4, "4", 1, "1"}, {5, "5", 2, "2"}};
  std::unordered_map<CategoryId, CategorySortOrder> sort_orders{
      {CategoryId{"1"}, CategorySortOrder{2, false}},
      {CategoryId{"2"}, CategorySortOrder{1, false}},
      {CategoryId{"3"}, CategorySortOrder{2, false}},
      {CategoryId{"4"}, CategorySortOrder{1, false}},
      {CategoryId{"5"}, CategorySortOrder{3, false}}};

  ResponseMapperForTestng::CategoriesSort(sort_orders, core_categories,
                                          std::nullopt);

  std::vector<handlers::Category> expected_categories{{2}, {1}, {4}, {3}, {5}};
  AssertEqualCategoriesOrder(core_categories, expected_categories);
}

TEST(CategoriesSort, SortBySortOrderWithCustom) {
  std::vector<handlers::Category> core_categories{
      {1, "1"}, {2, "2"}, {3, "3"}, {4, "4"}};
  // custom categories have negative sort order
  std::unordered_map<CategoryId, CategorySortOrder> sort_orders{
      {CategoryId{"1"}, CategorySortOrder{3, true}},
      {CategoryId{"2"}, CategorySortOrder{2, false}},
      {CategoryId{"3"}, CategorySortOrder{1, false}},
      {CategoryId{"4"}, CategorySortOrder{-2, true}}};

  ResponseMapperForTestng::CategoriesSort(sort_orders, core_categories,
                                          std::nullopt);

  std::vector<handlers::Category> expected_categories{{4}, {1}, {3}, {2}};
  AssertEqualCategoriesOrder(core_categories, expected_categories);
}

TEST(CategoriesSort, SortBySortOrderEqualOrders) {
  std::vector<handlers::Category> core_categories{{1, "1"}, {2, "2"}, {3, "3"}};
  std::unordered_map<CategoryId, CategorySortOrder> sort_orders{
      {CategoryId{"1"}, CategorySortOrder{1, false}},
      {CategoryId{"2"}, CategorySortOrder{1, false}},
      {CategoryId{"3"}, CategorySortOrder{1, false}}};

  ResponseMapperForTestng::CategoriesSort(sort_orders, core_categories,
                                          std::nullopt);

  std::vector<handlers::Category> expected_categories{{1}, {2}, {3}};
  AssertEqualCategoriesOrder(core_categories, expected_categories);
}

TEST(CategoriesSort, SortByScoring) {
  std::vector<handlers::Category> core_categories{{1, "1"}, {2, "2"}, {3, "3"}};
  std::unordered_map<CategoryId, CategorySortOrder> sort_orders{
      {CategoryId{"1"}, CategorySortOrder{3, false}},
      {CategoryId{"2"}, CategorySortOrder{2, false}},
      {CategoryId{"3"}, CategorySortOrder{1, false}}};
  CategoriesScoringDataString scoring{{"1", 5.0f}, {"2", 7.0f}, {"3", 9.0f}};

  ResponseMapperForTestng::CategoriesSort(sort_orders, core_categories,
                                          scoring);

  std::vector<handlers::Category> expected_categories{{3}, {2}, {1}};
  AssertEqualCategoriesOrder(core_categories, expected_categories);
}

TEST(CategoriesSort, SortByScoringWithMissingScores) {
  std::vector<handlers::Category> core_categories{
      {1, "1"}, {2, "2"}, {3, "3"}, {4, "4"}};
  std::unordered_map<CategoryId, CategorySortOrder> sort_orders{
      {CategoryId{"1"}, CategorySortOrder{1, false}},
      {CategoryId{"2"}, CategorySortOrder{2, false}},
      {CategoryId{"3"}, CategorySortOrder{3, false}},
      {CategoryId{"4"}, CategorySortOrder{4, false}}};
  CategoriesScoringDataString scoring{{"3", 7.0f}, {"4", 9.0f}};

  ResponseMapperForTestng::CategoriesSort(sort_orders, core_categories,
                                          scoring);

  std::vector<handlers::Category> expected_categories{{4}, {3}, {1}, {2}};
  AssertEqualCategoriesOrder(core_categories, expected_categories);
}

TEST(CategoriesSort, SortByScoringWithDepth) {
  // Category { id, parent_id }
  std::vector<handlers::Category> core_categories{
      {1, "1"}, {2, "2"}, {3, "3", 1, "1"}, {4, "4", 1, "1"}};
  std::unordered_map<CategoryId, CategorySortOrder> sort_orders{
      {CategoryId{"1"}, CategorySortOrder{3, false}},
      {CategoryId{"2"}, CategorySortOrder{2, false}},
      {CategoryId{"3"}, CategorySortOrder{1, false}},
      {CategoryId{"4"}, CategorySortOrder{2, false}}};
  CategoriesScoringDataString scoring{
      {"1", 5.0f}, {"2", 7.0f}, {"3", 9.0f}, {"4", 11.0f}};

  ResponseMapperForTestng::CategoriesSort(sort_orders, core_categories,
                                          scoring);

  std::vector<handlers::Category> expected_categories{{2}, {1}, {4}, {3}};
  AssertEqualCategoriesOrder(core_categories, expected_categories);
}

TEST(CategoriesSort, SortByScoringWithCustom) {
  std::vector<handlers::Category> core_categories{{1, "1"}, {2, "2"}, {3, "3"}};
  // custom categories have negative sort order
  std::unordered_map<CategoryId, CategorySortOrder> sort_orders{
      {CategoryId{"1"}, CategorySortOrder{1, false}},
      {CategoryId{"2"}, CategorySortOrder{2, false}},
      {CategoryId{"3"}, CategorySortOrder{-1, true}}};
  CategoriesScoringDataString scoring{{"1", 5.0f}, {"2", 7.0f}, {"3", 0.0f}};

  ResponseMapperForTestng::CategoriesSort(sort_orders, core_categories,
                                          scoring);

  std::vector<handlers::Category> expected_categories{{3}, {2}, {1}};
  AssertEqualCategoriesOrder(core_categories, expected_categories);
}

TEST(CategoriesSort, SortByScoringEqualScores) {
  std::vector<handlers::Category> core_categories{{1, "1"}, {2, "2"}, {3, "3"}};
  std::unordered_map<CategoryId, CategorySortOrder> sort_orders{
      {CategoryId{"1"}, CategorySortOrder{3, false}},
      {CategoryId{"2"}, CategorySortOrder{2, false}},
      {CategoryId{"3"}, CategorySortOrder{1, false}}};
  CategoriesScoringDataString scoring{{"1", 10.0f}, {"2", 10.0f}, {"3", 10.0f}};

  ResponseMapperForTestng::CategoriesSort(sort_orders, core_categories,
                                          scoring);

  std::vector<handlers::Category> expected_categories{{3}, {2}, {1}};
  AssertEqualCategoriesOrder(core_categories, expected_categories);
}

TEST(CategoriesSort, SortByScoringMixed) {
  // Category { id, parent_id }
  std::vector<handlers::Category> core_categories{
      {1, "1"},         {2, "2"},         {3, "3"}, {4, "4", 1, "1"},
      {5, "5", 1, "1"}, {6, "6", 1, "1"}, {7, "7"}};
  // custom categories have negative sort order
  std::unordered_map<CategoryId, CategorySortOrder> sort_orders{
      {CategoryId{"1"}, CategorySortOrder{1, false}},
      {CategoryId{"2"}, CategorySortOrder{2, false}},
      {CategoryId{"3"}, CategorySortOrder{3, false}},
      {CategoryId{"4"}, CategorySortOrder{1, false}},
      {CategoryId{"5"}, CategorySortOrder{2, false}},
      {CategoryId{"6"}, CategorySortOrder{3, false}},
      {CategoryId{"7"}, CategorySortOrder{5, true}}};
  CategoriesScoringDataString scoring{{"1", 1.0f}, {"2", 2.0f}, {"3", 3.0f},
                                      {"4", 4.0f}, {"5", 5.0f}, {"6", 6.0f}};

  ResponseMapperForTestng::CategoriesSort(sort_orders, core_categories,
                                          scoring);

  std::vector<handlers::Category> expected_categories{{7}, {3}, {2}, {1},
                                                      {6}, {5}, {4}};
  AssertEqualCategoriesOrder(core_categories, expected_categories);
}

}  // namespace eats_products::tests
