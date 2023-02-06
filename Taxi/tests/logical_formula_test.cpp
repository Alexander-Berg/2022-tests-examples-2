#include <set>
#include <string>
#include <unordered_set>
#include <variant>
#include <vector>

#include <gtest/gtest.h>

#include <logical-formula/logical_formula.hpp>

namespace {

struct NoneOfOp {
  NoneOfOp(std::initializer_list<std::string> vars) : none_of(vars) {}
  std::set<std::string> none_of;
};

struct AllOfOp {
  AllOfOp(std::initializer_list<std::string> vars) : all_of(vars) {}
  std::set<std::string> all_of;
};

struct AnyOfOp {
  AnyOfOp(std::initializer_list<std::string> vars) : any_of(vars) {}
  std::set<std::string> any_of;
};

using FirstOrderOp = std::variant<NoneOfOp, AllOfOp, AnyOfOp>;

struct AndOp {
  AndOp(std::vector<FirstOrderOp> rules) : and_(std::move(rules)) {}
  std::vector<FirstOrderOp> and_;
};

struct OrOp {
  OrOp(std::vector<FirstOrderOp> rules) : or_(std::move(rules)) {}
  std::vector<FirstOrderOp> or_;
};

using Operation = std::variant<NoneOfOp, AllOfOp, AnyOfOp, AndOp, OrOp>;

struct OperationTypes {
  using NoneOf = NoneOfOp;
  using AnyOf = AnyOfOp;
  using AllOf = AllOfOp;
  using And = AndOp;
  using Or = OrOp;
};

}  // namespace

namespace logical_formula {

TEST(TestLogicalFormula, TestEvaluate) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  const auto evaluate = [&vals](const Operation& operation) {
    return Evaluate<OperationTypes>(operation, vals);
  };

  ASSERT_EQ(evaluate(AnyOfOp({"a", "d"})), true);

  ASSERT_EQ(evaluate(AnyOfOp({"d"})), false);

  ASSERT_EQ(evaluate(AllOfOp({"a", "b"})), true);
  ASSERT_EQ(evaluate(AllOfOp({"b", "d"})), false);

  ASSERT_EQ(evaluate(NoneOfOp({"d", "e"})), true);
  ASSERT_EQ(evaluate(NoneOfOp({"b", "d"})), false);
  ASSERT_EQ(evaluate(AndOp({})), true);
  ASSERT_EQ(evaluate(AndOp({
                AnyOfOp({"a"}),  // true
                AnyOfOp({"a"}),  // true
            })),
            true);
  ASSERT_EQ(evaluate(AndOp({
                AnyOfOp({"a"}),  // true
                AnyOfOp({"e"}),  // false
            })),
            false);

  ASSERT_EQ(evaluate(OrOp({})), false);
  ASSERT_EQ(evaluate(OrOp({
                AnyOfOp({"a"}),  // true
                AnyOfOp({"a"}),  // true
            })),
            true);
  ASSERT_EQ(evaluate(OrOp({
                AnyOfOp({"a"}),  // true
                AnyOfOp({"e"}),  // false
            })),
            true);
}

}  // namespace logical_formula
