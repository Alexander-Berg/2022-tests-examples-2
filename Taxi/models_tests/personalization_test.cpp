#include <gtest/gtest.h>

#include <models/brand.hpp>
#include <models/nomenclature.hpp>
#include <models/personalization.hpp>

#include <tests/models_tests/personalization_delegate_for_testing.hpp>

namespace eats_products::tests {

namespace {

using models::PersonalizationType;
using models::PersonalizationTypes;

const PersonalizationTypes kCarouselsProducts = {
    PersonalizationType::kCarouselsProductsSort};
const PersonalizationTypes kMenuProducts = {
    PersonalizationType::kMenuProductsSort};
const PersonalizationTypes kAllProducts = {
    PersonalizationType::kCarouselsProductsSort,
    PersonalizationType::kMenuProductsSort};
const PersonalizationTypes kCarouselsOnly = {
    PersonalizationType::kCarouselsSort};
const PersonalizationTypes kProductsAndCarousels = {
    PersonalizationType::kCarouselsProductsSort,
    PersonalizationType::kMenuProductsSort,
    PersonalizationType::kCarouselsSort};

constexpr models::BrandId kBrandForTesting{0};

const models::Personalization::Delegate::CategoryInfo kCategory1Info{
    {models::NomenclatureProductId{"product1"},
     models::NomenclatureProductId{"product2"}},
    10};
const models::Personalization::Delegate::CategoryInfo kCategory2Info{
    {models::NomenclatureProductId{"product4"},
     models::NomenclatureProductId{"product3"}},
    20};

const models::Personalization::Delegate::CategoriesInfo kCategoriesInfo{
    {models::CategoryId{"category1"}, kCategory1Info},
    {models::CategoryId{"category2"}, kCategory2Info}};

struct TableNameTestParams {
  PersonalizationTypes personalization_types;
  std::string user_income_level;
  std::string income_level_by_brand;
  std::string default_table_name;
  std::string table_name_template;
};

struct GetOrderedProductsTestParams {
  PersonalizationTypes personalization_types;
  std::string category;
  models::NomenclatureProductIds expected_result;
};

struct GetNumberOfOrderedProductsTestParams {
  PersonalizationTypes personalization_types;
  std::string category;
  size_t expected_result;
};

struct DefaultTableNameTestParams : TableNameTestParams {
  std::string expected_default_table_name;
};

struct PersonalizedTableNameTestParams : TableNameTestParams {
  std::string expected_personalized_table_name;
};

struct DefaultTablNameTest
    : public ::testing::TestWithParam<DefaultTableNameTestParams> {};
struct PersonalizedCarouselsProductsTableNameTest
    : public ::testing::TestWithParam<PersonalizedTableNameTestParams> {};
struct PersonalizedMenuProductsTableNameTest
    : public ::testing::TestWithParam<PersonalizedTableNameTestParams> {};
struct PersonalizedCategoriesTableNameTest
    : public ::testing::TestWithParam<PersonalizedTableNameTestParams> {};
struct GetOrderedProductsTest
    : public ::testing::TestWithParam<GetOrderedProductsTestParams> {};
struct GetNumberOfOrderedProductsTest
    : public ::testing::TestWithParam<GetNumberOfOrderedProductsTestParams> {};

const std::vector<DefaultTableNameTestParams> kDefaultTableNameParams = {
    {{{}, "", "", "default", ""}, "default"},
    {{{}, "", "B2", "default", ""}, "default"},
    {{{}, "A", "C2", "default", ""}, "default"},
    {{kCarouselsProducts, "", "", "default", ""}, "default"},
    {{kCarouselsProducts, "", "B2", "default", ""}, "default"},
    {{kCarouselsProducts, "A", "C2", "default", ""}, "default"},
    {{kMenuProducts, "", "", "default", ""}, "default"},
    {{kMenuProducts, "", "B2", "default", ""}, "default"},
    {{kMenuProducts, "A", "C2", "default", ""}, "default"},
    {{kAllProducts, "", "", "default", ""}, "default"},
    {{kAllProducts, "", "B2", "default", ""}, "default"},
    {{kAllProducts, "A", "C2", "default", ""}, "default"},
    {{kCarouselsOnly, "", "", "default", ""}, "default"},
    {{kCarouselsOnly, "", "B2", "default", ""}, "default"},
    {{kCarouselsOnly, "A", "C2", "default", ""}, "default"},
    {{kProductsAndCarousels, "", "", "default", ""}, "default"},
    {{kProductsAndCarousels, "", "B2", "default", ""}, "default"},
    {{kProductsAndCarousels, "A", "C2", "default", ""}, "default"},
};

const std::vector<PersonalizedTableNameTestParams> kCarouselsProductsParams = {
    {{{}, "", "", "default", ""}, "default"},
    {{{}, "", "", "default", "template_"}, "default"},
    {{{}, "", "C1", "default", ""}, "default"},
    {{{}, "", "C1", "default", "template_"}, "default"},
    {{{}, "B2", "", "default", ""}, "default"},
    {{{}, "B2", "", "default", "template_"}, "default"},
    {{{}, "B2", "A", "default", "template_"}, "default"},
    {{{}, "B2", "C1", "default", "template_"}, "default"},
    {{kCarouselsProducts, "", "", "default", ""}, "default"},
    {{kCarouselsProducts, "", "", "default", "template_"}, "default"},
    {{kCarouselsProducts, "", "C1", "default", ""}, "C1"},
    {{kCarouselsProducts, "", "C1", "default", "template_"}, "template_C1"},
    {{kCarouselsProducts, "B2", "", "default", ""}, "B2"},
    {{kCarouselsProducts, "B2", "", "default", "template_"}, "template_B2"},
    {{kCarouselsProducts, "B2", "A", "default", "template_"}, "template_B2"},
    {{kCarouselsProducts, "B2", "C1", "default", "template_"}, "template_B2"},
    {{kMenuProducts, "", "", "default", ""}, "default"},
    {{kMenuProducts, "", "", "default", "template_"}, "default"},
    {{kMenuProducts, "", "C1", "default", ""}, "default"},
    {{kMenuProducts, "", "C1", "default", "template_"}, "default"},
    {{kMenuProducts, "B2", "", "default", ""}, "default"},
    {{kMenuProducts, "B2", "", "default", "template_"}, "default"},
    {{kMenuProducts, "B2", "A", "default", "template_"}, "default"},
    {{kMenuProducts, "B2", "C1", "default", "template_"}, "default"},
    {{kAllProducts, "", "", "default", ""}, "default"},
    {{kAllProducts, "", "", "default", "template_"}, "default"},
    {{kAllProducts, "", "C1", "default", ""}, "C1"},
    {{kAllProducts, "", "C1", "default", "template_"}, "template_C1"},
    {{kAllProducts, "B2", "", "default", ""}, "B2"},
    {{kAllProducts, "B2", "", "default", "template_"}, "template_B2"},
    {{kAllProducts, "B2", "A", "default", "template_"}, "template_B2"},
    {{kAllProducts, "B2", "C1", "default", "template_"}, "template_B2"},
    {{kCarouselsOnly, "", "", "default", ""}, "default"},
    {{kCarouselsOnly, "", "", "default", "template_"}, "default"},
    {{kCarouselsOnly, "", "C1", "default", ""}, "default"},
    {{kCarouselsOnly, "", "C1", "default", "template_"}, "default"},
    {{kCarouselsOnly, "B2", "", "default", ""}, "default"},
    {{kCarouselsOnly, "B2", "", "default", "template_"}, "default"},
    {{kCarouselsOnly, "B2", "A", "default", "template_"}, "default"},
    {{kCarouselsOnly, "B2", "C1", "default", "template_"}, "default"},
    {{kProductsAndCarousels, "", "", "default", ""}, "default"},
    {{kProductsAndCarousels, "", "", "default", "template_"}, "default"},
    {{kProductsAndCarousels, "", "C1", "default", ""}, "C1"},
    {{kProductsAndCarousels, "", "C1", "default", "template_"}, "template_C1"},
    {{kProductsAndCarousels, "B2", "", "default", ""}, "B2"},
    {{kProductsAndCarousels, "B2", "", "default", "template_"}, "template_B2"},
    {{kProductsAndCarousels, "B2", "A", "default", "template_"}, "template_B2"},
    {{kProductsAndCarousels, "B2", "C1", "default", "template_"},
     "template_B2"},
};

const std::vector<PersonalizedTableNameTestParams> kMenuProductsParams = {
    {{{}, "", "", "default", ""}, "default"},
    {{{}, "", "", "default", "template_"}, "default"},
    {{{}, "", "C1", "default", ""}, "default"},
    {{{}, "", "C1", "default", "template_"}, "default"},
    {{{}, "B2", "", "default", ""}, "default"},
    {{{}, "B2", "", "default", "template_"}, "default"},
    {{{}, "B2", "A", "default", "template_"}, "default"},
    {{{}, "B2", "C1", "default", "template_"}, "default"},
    {{kMenuProducts, "", "", "default", ""}, "default"},
    {{kMenuProducts, "", "", "default", "template_"}, "default"},
    {{kMenuProducts, "", "C1", "default", ""}, "C1"},
    {{kMenuProducts, "", "C1", "default", "template_"}, "template_C1"},
    {{kMenuProducts, "B2", "", "default", ""}, "B2"},
    {{kMenuProducts, "B2", "", "default", "template_"}, "template_B2"},
    {{kMenuProducts, "B2", "A", "default", "template_"}, "template_B2"},
    {{kMenuProducts, "B2", "C1", "default", "template_"}, "template_B2"},
    {{kCarouselsProducts, "", "", "default", ""}, "default"},
    {{kCarouselsProducts, "", "", "default", "template_"}, "default"},
    {{kCarouselsProducts, "", "C1", "default", ""}, "default"},
    {{kCarouselsProducts, "", "C1", "default", "template_"}, "default"},
    {{kCarouselsProducts, "B2", "", "default", ""}, "default"},
    {{kCarouselsProducts, "B2", "", "default", "template_"}, "default"},
    {{kCarouselsProducts, "B2", "A", "default", "template_"}, "default"},
    {{kCarouselsProducts, "B2", "C1", "default", "template_"}, "default"},
    {{kAllProducts, "", "", "default", ""}, "default"},
    {{kAllProducts, "", "", "default", "template_"}, "default"},
    {{kAllProducts, "", "C1", "default", ""}, "C1"},
    {{kAllProducts, "", "C1", "default", "template_"}, "template_C1"},
    {{kAllProducts, "B2", "", "default", ""}, "B2"},
    {{kAllProducts, "B2", "", "default", "template_"}, "template_B2"},
    {{kAllProducts, "B2", "A", "default", "template_"}, "template_B2"},
    {{kAllProducts, "B2", "C1", "default", "template_"}, "template_B2"},
    {{kCarouselsOnly, "", "", "default", ""}, "default"},
    {{kCarouselsOnly, "", "", "default", "template_"}, "default"},
    {{kCarouselsOnly, "", "C1", "default", ""}, "default"},
    {{kCarouselsOnly, "", "C1", "default", "template_"}, "default"},
    {{kCarouselsOnly, "B2", "", "default", ""}, "default"},
    {{kCarouselsOnly, "B2", "", "default", "template_"}, "default"},
    {{kCarouselsOnly, "B2", "A", "default", "template_"}, "default"},
    {{kCarouselsOnly, "B2", "C1", "default", "template_"}, "default"},
    {{kProductsAndCarousels, "", "", "default", ""}, "default"},
    {{kProductsAndCarousels, "", "", "default", "template_"}, "default"},
    {{kProductsAndCarousels, "", "C1", "default", ""}, "C1"},
    {{kProductsAndCarousels, "", "C1", "default", "template_"}, "template_C1"},
    {{kProductsAndCarousels, "B2", "", "default", ""}, "B2"},
    {{kProductsAndCarousels, "B2", "", "default", "template_"}, "template_B2"},
    {{kProductsAndCarousels, "B2", "A", "default", "template_"}, "template_B2"},
    {{kProductsAndCarousels, "B2", "C1", "default", "template_"},
     "template_B2"},
};

const std::vector<PersonalizedTableNameTestParams> kCategoriesTableParams = {
    {{{}, "", "", "default", ""}, ""},
    {{{}, "", "", "default", "template_"}, ""},
    {{{}, "", "C1", "default", ""}, ""},
    {{{}, "", "C1", "default", "template_"}, ""},
    {{{}, "B2", "", "default", ""}, ""},
    {{{}, "B2", "", "default", "template_"}, ""},
    {{{}, "B2", "A", "default", "template_"}, ""},
    {{{}, "B2", "C1", "default", "template_"}, ""},
    {{kCarouselsOnly, "", "", "default", ""}, ""},
    {{kCarouselsOnly, "", "", "default", "template_"}, ""},
    {{kCarouselsOnly, "", "C1", "default", ""}, "C1"},
    {{kCarouselsOnly, "", "C1", "default", "template_"}, "template_C1"},
    {{kCarouselsOnly, "B2", "", "default", ""}, "B2"},
    {{kCarouselsOnly, "B2", "", "default", "template_"}, "template_B2"},
    {{kCarouselsOnly, "B2", "A", "default", "template_"}, "template_B2"},
    {{kCarouselsOnly, "B2", "C1", "default", "template_"}, "template_B2"},
    {{kAllProducts, "", "", "default", ""}, ""},
    {{kAllProducts, "", "", "default", "template_"}, ""},
    {{kAllProducts, "", "C1", "default", ""}, ""},
    {{kAllProducts, "", "C1", "default", "template_"}, ""},
    {{kAllProducts, "B2", "", "default", ""}, ""},
    {{kAllProducts, "B2", "", "default", "template_"}, ""},
    {{kAllProducts, "B2", "A", "default", "template_"}, ""},
    {{kAllProducts, "B2", "C1", "default", "template_"}, ""},
    {{kProductsAndCarousels, "", "", "default", ""}, ""},
    {{kProductsAndCarousels, "", "", "default", "template_"}, ""},
    {{kProductsAndCarousels, "", "C1", "default", ""}, "C1"},
    {{kProductsAndCarousels, "", "C1", "default", "template_"}, "template_C1"},
    {{kProductsAndCarousels, "B2", "", "default", ""}, "B2"},
    {{kProductsAndCarousels, "B2", "", "default", "template_"}, "template_B2"},
    {{kProductsAndCarousels, "B2", "A", "default", "template_"}, "template_B2"},
    {{kProductsAndCarousels, "B2", "C1", "default", "template_"},
     "template_B2"},
};

const std::vector<GetOrderedProductsTestParams> kOrderedProductsTestParams{
    {{}, "category1", {}},
    {kCarouselsProducts, "category1", kCategory1Info.origin_ids_},
    {kCarouselsProducts, "category2", kCategory2Info.origin_ids_},
    {kCarouselsProducts, "category3", {}},
    {kProductsAndCarousels, "category1", kCategory1Info.origin_ids_},
    {kCarouselsOnly, "category1", {}},
};

const std::vector<GetNumberOfOrderedProductsTestParams>
    kNumberOfOrderedProductsTestParams{
        {{}, "category1", 0},
        {kCarouselsOnly, "category1", 10},
        {kProductsAndCarousels, "category1", 10},
        {kCarouselsOnly, "category2", 20},
        {kProductsAndCarousels, "category3", 0},
        {kCarouselsProducts, "category1", 0},
    };

models::NomenclatureProductIds GetOrderedProductsFromCategory(
    const std::string& category, const PersonalizationTypes& types) {
  auto delegate = std::make_unique<tests::PersonalizationDelegateForTesting>();
  delegate->SetCategoriesInfo(kCategoriesInfo);
  delegate->SetPersonalizationTypes(types);
  models::Personalization personalization(kBrandForTesting,
                                          std::move(delegate));

  const models::CategoryId category_id{category};
  return personalization.GetOrderedProductsFromCategory(category_id);
}

size_t GetNumberOfOrderedProductsFromCategory(
    const std::string& category, const PersonalizationTypes& types) {
  auto delegate = std::make_unique<tests::PersonalizationDelegateForTesting>();
  delegate->SetCategoriesInfo(kCategoriesInfo);
  delegate->SetPersonalizationTypes(types);
  models::Personalization personalization(kBrandForTesting,
                                          std::move(delegate));

  const models::CategoryId category_id{category};
  return personalization.GetNumberOfOrderedProductsFromCategory(category_id);
}

}  // namespace

TEST_P(DefaultTablNameTest, GetDefaultTableName) {
  auto delegate = std::make_unique<tests::PersonalizationDelegateForTesting>();
  delegate->SetPersonalizationTypes(GetParam().personalization_types);
  delegate->SetUserIncomeLevel(GetParam().user_income_level);
  delegate->SetIncomeByBrand(GetParam().income_level_by_brand);
  delegate->SetDefaultTableName(GetParam().default_table_name);

  models::Personalization personalization(kBrandForTesting,
                                          std::move(delegate));
  ASSERT_EQ(personalization.GetDefaultProductsTableName(),
            GetParam().expected_default_table_name);
}

INSTANTIATE_TEST_SUITE_P(Personalization, DefaultTablNameTest,
                         testing::ValuesIn(kDefaultTableNameParams));

TEST_P(PersonalizedCarouselsProductsTableNameTest, GetTableNameForProducts) {
  auto delegate = std::make_unique<tests::PersonalizationDelegateForTesting>();
  delegate->SetPersonalizationTypes(GetParam().personalization_types);
  delegate->SetUserIncomeLevel(GetParam().user_income_level);
  delegate->SetIncomeByBrand(GetParam().income_level_by_brand);
  delegate->SetDefaultTableName(GetParam().default_table_name);
  delegate->SetTableNameTemplate(GetParam().table_name_template);

  models::Personalization personalization(kBrandForTesting,
                                          std::move(delegate));
  ASSERT_EQ(personalization.GetTableNameForCarouselsProducts(),
            GetParam().expected_personalized_table_name);
}

INSTANTIATE_TEST_SUITE_P(Personalization,
                         PersonalizedCarouselsProductsTableNameTest,
                         testing::ValuesIn(kCarouselsProductsParams));

TEST_P(PersonalizedMenuProductsTableNameTest, GetTableNameForProducts) {
  auto delegate = std::make_unique<tests::PersonalizationDelegateForTesting>();
  delegate->SetPersonalizationTypes(GetParam().personalization_types);
  delegate->SetUserIncomeLevel(GetParam().user_income_level);
  delegate->SetIncomeByBrand(GetParam().income_level_by_brand);
  delegate->SetDefaultTableName(GetParam().default_table_name);
  delegate->SetTableNameTemplate(GetParam().table_name_template);

  models::Personalization personalization(kBrandForTesting,
                                          std::move(delegate));
  ASSERT_EQ(personalization.GetTableNameForMenuProducts(),
            GetParam().expected_personalized_table_name);
}

INSTANTIATE_TEST_SUITE_P(Personalization, PersonalizedMenuProductsTableNameTest,
                         testing::ValuesIn(kMenuProductsParams));

TEST_P(PersonalizedCategoriesTableNameTest, GetTableNameForCategories) {
  auto delegate = std::make_unique<tests::PersonalizationDelegateForTesting>();
  delegate->SetPersonalizationTypes(GetParam().personalization_types);
  delegate->SetUserIncomeLevel(GetParam().user_income_level);
  delegate->SetIncomeByBrand(GetParam().income_level_by_brand);
  delegate->SetDefaultTableName(GetParam().default_table_name);
  delegate->SetTableNameTemplate(GetParam().table_name_template);

  models::Personalization personalization(kBrandForTesting,
                                          std::move(delegate));
  ASSERT_EQ(personalization.GetTableNameForCategories(),
            GetParam().expected_personalized_table_name);
}

INSTANTIATE_TEST_SUITE_P(Personalization, PersonalizedCategoriesTableNameTest,
                         testing::ValuesIn(kCategoriesTableParams));

TEST_P(GetOrderedProductsTest, GetOrderedProductsFromCategory) {
  auto result = GetOrderedProductsFromCategory(
      GetParam().category, GetParam().personalization_types);
  ASSERT_EQ(result, GetParam().expected_result);
}

INSTANTIATE_TEST_SUITE_P(Personalization, GetOrderedProductsTest,
                         testing::ValuesIn(kOrderedProductsTestParams));

TEST_P(GetNumberOfOrderedProductsTest, GetNumberOfOrderedProducts) {
  auto result = GetNumberOfOrderedProductsFromCategory(
      GetParam().category, GetParam().personalization_types);
  ASSERT_EQ(result, GetParam().expected_result);
}

INSTANTIATE_TEST_SUITE_P(Personalization, GetNumberOfOrderedProductsTest,
                         testing::ValuesIn(kNumberOfOrderedProductsTestParams));

}  // namespace eats_products::tests
