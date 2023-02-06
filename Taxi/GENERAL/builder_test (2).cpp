#include <set>
#include <vector>

#include <gtest/gtest.h>

#include <eats-catalog-predicate/builder.hpp>

namespace eats_catalog_predicate {

namespace {

using ::clients::catalog::libraries::eats_catalog_predicate::Argument;
using ::clients::catalog::libraries::eats_catalog_predicate::Predicate;
using ::clients::catalog::libraries::eats_catalog_predicate::PredicateInit;
using ::clients::catalog::libraries::eats_catalog_predicate::PredicateType;
using ::clients::catalog::libraries::eats_catalog_predicate::ValueType;

// T is string or int
template <class T>
std::unordered_set<std::variant<std::string, int>> SetToVariantSet(
    const std::unordered_set<T>& value) {
  return {value.begin(), value.end()};
}

}  // namespace

TEST(PredicateBuilder, BrandIdInSetInt) {
  const std::unordered_set<int> value = {1};
  auto predicate = PredicateBuilder().BrandId().InSet(value).Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kBrandId;
  expected_init.set_elem_type = ValueType::kInt;
  expected_init.set = SetToVariantSet(value);

  Predicate expected;
  expected.type = PredicateType::kInSet;
  expected.init = expected_init;

  ASSERT_EQ(predicate, expected);
}

TEST(PredicateBuilder, PlaceIdEqStr) {
  const std::string value = "value";
  auto predicate = PredicateBuilder().PlaceId().Eq(value).Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kPlaceId;
  expected_init.arg_type = ValueType::kString;
  expected_init.value = value;

  Predicate expected;
  expected.type = PredicateType::kEq;
  expected.init = expected_init;

  ASSERT_EQ(predicate, expected);
}

TEST(PredicateBuilder, BrandIdNeqInt) {
  const int value = 23;
  auto predicate = PredicateBuilder().BrandId().Neq(value).Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kBrandId;
  expected_init.arg_type = ValueType::kInt;
  expected_init.value = value;

  Predicate expected;
  expected.type = PredicateType::kNeq;
  expected.init = expected_init;

  ASSERT_EQ(predicate, expected);
}

TEST(PredicateBuilder, All) {
  auto predicate = PredicateBuilder()
                       .All({
                           PredicateBuilder().PlaceId().Eq(1).Build(),
                           PredicateBuilder()
                               .BrandId()
                               .InSet(std::unordered_set<int>{2, 4, 6})
                               .Build(),
                       })
                       .Build();

  std::vector<Predicate> predicates;
  {
    const int value = {1};

    PredicateInit expected_init;
    expected_init.arg_name = Argument::kPlaceId;
    expected_init.arg_type = ValueType::kInt;
    expected_init.value = value;

    Predicate expected;
    expected.type = PredicateType::kEq;
    expected.init = expected_init;

    predicates.push_back(expected);
  }

  {
    const std::unordered_set<int> value = {2, 4, 6};

    PredicateInit expected_init;
    expected_init.arg_name = Argument::kBrandId;
    expected_init.set_elem_type = ValueType::kInt;
    expected_init.set = SetToVariantSet(value);

    Predicate expected;
    expected.type = PredicateType::kInSet;
    expected.init = expected_init;

    predicates.push_back(expected);
  }

  Predicate expected;
  expected.type = PredicateType::kAllOf;
  expected.predicates = predicates;

  auto size =
      std::min(expected.predicates->size(), predicate.predicates->size());

  for (size_t i = 0; i < size; i++) {
    ASSERT_EQ((*expected.predicates)[i], (*predicate.predicates)[i]);
  }
  ASSERT_EQ(predicate.type, expected.type);
  ASSERT_EQ(predicate.init, expected.init);
  ASSERT_EQ(predicate, expected);
}

TEST(PredicateBuilder, Any) {
  auto predicate = PredicateBuilder()
                       .Any({
                           PredicateBuilder().Shop().Build(),
                           PredicateBuilder()
                               .BrandId()
                               .InSet(std::unordered_set<int>{2, 3, 6})
                               .Build(),
                       })
                       .Build();

  std::vector<Predicate> predicates;
  {
    const std::string value = {"shop"};

    PredicateInit expected_init;
    expected_init.arg_name = Argument::kBusiness;
    expected_init.arg_type = ValueType::kString;
    expected_init.value = value;

    Predicate expected;
    expected.type = PredicateType::kEq;
    expected.init = expected_init;

    predicates.push_back(expected);
  }

  {
    const std::unordered_set<int> value = {2, 3, 6};

    PredicateInit expected_init;
    expected_init.arg_name = Argument::kBrandId;
    expected_init.set_elem_type = ValueType::kInt;
    expected_init.set = SetToVariantSet(value);

    Predicate expected;
    expected.type = PredicateType::kInSet;
    expected.init = expected_init;

    predicates.push_back(expected);
  }

  Predicate expected;
  expected.type = PredicateType::kAnyOf;
  expected.predicates = predicates;

  auto size =
      std::min(expected.predicates->size(), predicate.predicates->size());

  for (size_t i = 0; i < size; i++) {
    ASSERT_EQ((*expected.predicates)[i], (*predicate.predicates)[i]);
  }
  ASSERT_EQ(predicate.type, expected.type);
  ASSERT_EQ(predicate.init, expected.init);
  ASSERT_EQ(predicate, expected);
}

TEST(PredicateBuilder, PromoTypesIntersects) {
  const std::unordered_set<int> value = {1, 2};
  auto predicate = PredicateBuilder().PromoType().Intersects(value).Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kPromoType;
  expected_init.set_elem_type = ValueType::kInt;
  expected_init.set = SetToVariantSet(value);

  Predicate expected;
  expected.type = PredicateType::kIntersects;
  expected.init = expected_init;

  ASSERT_EQ(predicate, expected);
}

TEST(PredicateBuilder, DeliveryTimeMaxLess) {
  const int kDeliveryTimeLimit = 30;

  auto predicate =
      PredicateBuilder().DeliveryTimeMax().Lt(kDeliveryTimeLimit).Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kDeliveryTimeMax;
  expected_init.arg_type = ValueType::kInt;
  expected_init.value = kDeliveryTimeLimit;

  Predicate expected;
  expected.type = PredicateType::kLt;
  expected.init = expected_init;

  ASSERT_EQ(predicate.init, expected.init);
}

TEST(PredicateBuilder, DeliveryTimeMinLessOrEqual) {
  const int kDeliveryTimeLimit = 30;

  auto predicate =
      PredicateBuilder().DeliveryTimeMin().Lte(kDeliveryTimeLimit).Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kDeliveryTimeMin;
  expected_init.arg_type = ValueType::kInt;
  expected_init.value = kDeliveryTimeLimit;

  Predicate expected;
  expected.type = PredicateType::kLte;
  expected.init = expected_init;

  ASSERT_EQ(predicate, expected);
}

TEST(PredicateBuilder, DeliveryType) {
  const std::string kDeliveryType = "native";

  auto predicate = PredicateBuilder().DeliveryType().Eq(kDeliveryType).Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kDeliveryType;
  expected_init.arg_type = ValueType::kString;
  expected_init.value = kDeliveryType;

  Predicate expected;
  expected.type = PredicateType::kEq;
  expected.init = expected_init;

  ASSERT_EQ(predicate, expected);
}

TEST(PredicateBuilder, ContainsCategoryId) {
  const int kCategoryId = 1;

  auto predicate =
      PredicateBuilder().CategoryId().Contains(kCategoryId).Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kCategoryId;
  expected_init.arg_type = ValueType::kInt;
  expected_init.value = kCategoryId;

  Predicate expected;
  expected.type = PredicateType::kContains;
  expected.init = expected_init;

  ASSERT_EQ(predicate, expected);
}

TEST(PredicateBuilder, PlaceIdNotEq) {
  const int kPlaceId = 1;

  auto predicate = PredicateBuilder()
                       .Not(PredicateBuilder().PlaceId().Eq(kPlaceId).Build())
                       .Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kPlaceId;
  expected_init.arg_type = ValueType::kInt;
  expected_init.value = kPlaceId;

  Predicate eq;
  eq.type = PredicateType::kEq;
  eq.init = expected_init;

  Predicate expected;
  expected.type = PredicateType::kNot;
  expected.predicates = {eq};

  ASSERT_EQ(predicate, expected);
}

TEST(PredicateBuilder, PlaceSlugEq) {
  const auto actual = PredicateBuilder().PlaceSlug().Eq("a").Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kPlaceSlug;
  expected_init.arg_type = ValueType::kString;
  expected_init.value = "a";

  Predicate expected;
  expected.type = PredicateType::kEq;
  expected.init = expected_init;

  ASSERT_EQ(expected, actual);
}

TEST(PredicateBuilder, PlaceSlugInSet) {
  const std::unordered_set<std::string> set{"a", "b", "c"};
  const auto actual = PredicateBuilder().PlaceSlug().InSet(set).Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kPlaceSlug;
  expected_init.set_elem_type = ValueType::kString;
  expected_init.set = SetToVariantSet(set);

  Predicate expected;
  expected.type = PredicateType::kInSet;
  expected.init = expected_init;

  ASSERT_EQ(expected, actual);
}

}  // namespace eats_catalog_predicate
