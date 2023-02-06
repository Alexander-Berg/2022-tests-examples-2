#include <set>
#include <vector>

#include <gtest/gtest.h>

#include <expression/builder.hpp>

namespace eats_menu_categories::expression {

namespace {

using handlers::Argument;
using handlers::Predicate;
using handlers::PredicateInit;
using handlers::PredicateType;
using handlers::ValueType;

// T is string or int
template <class T>
std::unordered_set<std::variant<std::string, int>> SetToVariantSet(
    const std::unordered_set<T>& value) {
  return {value.begin(), value.end()};
}

}  // namespace

TEST(PredicateBuilder, ItemIdInSetInt) {
  const std::unordered_set<int> value = {1};
  auto predicate = PredicateBuilder().ItemId().InSet(value).Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kItemId;
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

TEST(PredicateBuilder, ItemIdNeqInt) {
  const int value = 23;
  auto predicate = PredicateBuilder().ItemId().Neq(value).Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kItemId;
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
                               .ItemId()
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
    expected_init.arg_name = Argument::kItemId;
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
                           PredicateBuilder().ItemName().Eq("my item").Build(),
                           PredicateBuilder()
                               .ItemId()
                               .InSet(std::unordered_set<int>{2, 3, 6})
                               .Build(),
                       })
                       .Build();

  std::vector<Predicate> predicates;
  {
    const std::string value = {"my item"};

    PredicateInit expected_init;
    expected_init.arg_name = Argument::kItemName;
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
    expected_init.arg_name = Argument::kItemId;
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

TEST(PredicateBuilder, ItemIdsIntersects) {
  const std::unordered_set<int> value = {1, 2};
  auto predicate = PredicateBuilder().ItemId().Intersects(value).Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kItemId;
  expected_init.set_elem_type = ValueType::kInt;
  expected_init.set = SetToVariantSet(value);

  Predicate expected;
  expected.type = PredicateType::kIntersects;
  expected.init = expected_init;

  ASSERT_EQ(predicate, expected);
}

TEST(PredicateBuilder, ItemIdLess) {
  const int kItemIdLimit = 30;

  auto predicate = PredicateBuilder().ItemId().Lt(kItemIdLimit).Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kItemId;
  expected_init.arg_type = ValueType::kInt;
  expected_init.value = kItemIdLimit;

  Predicate expected;
  expected.type = PredicateType::kLt;
  expected.init = expected_init;

  ASSERT_EQ(predicate.init, expected.init);
}

TEST(PredicateBuilder, ItemIdLessOrEqual) {
  const int kItemIdLimit = 30;

  auto predicate = PredicateBuilder().ItemId().Lte(kItemIdLimit).Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kItemId;
  expected_init.arg_type = ValueType::kInt;
  expected_init.value = kItemIdLimit;

  Predicate expected;
  expected.type = PredicateType::kLte;
  expected.init = expected_init;

  ASSERT_EQ(predicate, expected);
}

TEST(PredicateBuilder, ContainsItemId) {
  const int kItemId = 1;

  auto predicate = PredicateBuilder().ItemId().Contains(kItemId).Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kItemId;
  expected_init.arg_type = ValueType::kInt;
  expected_init.value = kItemId;

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

TEST(PredicateBuilder, ItemNameEq) {
  const auto actual = PredicateBuilder().ItemName().Eq("a").Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kItemName;
  expected_init.arg_type = ValueType::kString;
  expected_init.value = "a";

  Predicate expected;
  expected.type = PredicateType::kEq;
  expected.init = expected_init;

  ASSERT_EQ(expected, actual);
}

TEST(PredicateBuilder, ItemNameInSet) {
  const std::unordered_set<std::string> set{"a", "b", "c"};
  const auto actual = PredicateBuilder().ItemName().InSet(set).Build();

  PredicateInit expected_init;
  expected_init.arg_name = Argument::kItemName;
  expected_init.set_elem_type = ValueType::kString;
  expected_init.set = SetToVariantSet(set);

  Predicate expected;
  expected.type = PredicateType::kInSet;
  expected.init = expected_init;

  ASSERT_EQ(expected, actual);
}

}  // namespace eats_menu_categories::expression
