#include <userver/utest/utest.hpp>
#include <utils/utils.hpp>

#include <set>
#include <variant>

#include <common/formula_for_ttl.hpp>

namespace std {

std::ostream& operator<<(std::ostream& os, const std::optional<int>& opt_int) {
  return os << (opt_int ? std::to_string(*opt_int) : "(none)");
}

}  // namespace std

namespace {

struct NoneOfOp {
  NoneOfOp(std::initializer_list<std::string> vars) : none_of(vars) {}
  std::unordered_set<std::string> none_of;
};

struct AllOfOp {
  AllOfOp(std::initializer_list<std::string> vars) : all_of(vars) {}
  std::unordered_set<std::string> all_of;
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
  using AnyOf = AnyOfOp;
  using AllOf = AllOfOp;
  using NoneOf = NoneOfOp;
  using And = AndOp;
  using Or = OrOp;
};

std::optional<int> AsSeconds(std::optional<models::TimePoint> tp) {
  if (!tp) {
    return std::nullopt;
  }
  return std::chrono::duration_cast<std::chrono::seconds>(
             tp->time_since_epoch())
      .count();
}

}  // namespace

namespace common {

TEST(TtlFormula, Test) {
  const std::set<std::string> tags = {"a", "b", "c"};
  const std::map<std::string, int> ttls = {
      {"a", 100},
      {"b", 150},
  };

  const auto get_ttl_func =
      [&ttls,
       &tags](const std::string& val) -> std::optional<models::TimePoint> {
    if (const auto found = ttls.find(val); found != ttls.end()) {
      return models::TimePoint(std::chrono::seconds(found->second));
    }
    if (const auto found = tags.find(val); found != tags.end()) {
      return models::TimePoint::max();
    }
    return std::nullopt;
  };

  const auto evaluate_ttl = [&](auto&& operation) {
    const auto result = EvaluateTtlOverFormula<OperationTypes>(
        Operation{std::forward<decltype(operation)>(operation)}, tags,
        get_ttl_func);
    return AsSeconds(result);
  };

  const auto infinity = AsSeconds(models::TimePoint::max());

  ASSERT_EQ(evaluate_ttl(AllOfOp{"a", "b"}), 100);
  ASSERT_EQ(evaluate_ttl(AnyOfOp{"a", "b"}), 150);
  ASSERT_EQ(evaluate_ttl(AnyOfOp{"a", "d"}), 100);
  ASSERT_EQ(evaluate_ttl(NoneOfOp{"d"}), infinity);

  ASSERT_EQ(evaluate_ttl(AndOp({AnyOfOp{"c"}, AnyOfOp{"a"}})), 100);
  ASSERT_EQ(evaluate_ttl(AndOp({AllOfOp{"a"}, AllOfOp{"b"}})), 100);
  ASSERT_EQ(evaluate_ttl(AndOp({AllOfOp{"c"}, AnyOfOp{"a", "b"}})), 150);
  ASSERT_EQ(evaluate_ttl(AndOp({AnyOfOp{"a", "b"}})), 150);

  ASSERT_EQ(evaluate_ttl(OrOp({AllOfOp{"c"}, AnyOfOp{"a", "b"}})), infinity);
  ASSERT_EQ(evaluate_ttl(OrOp({AllOfOp{"d"}, AllOfOp{"a", "b"}})), 100);
  ASSERT_EQ(evaluate_ttl(OrOp({AllOfOp{"a"}, AllOfOp{"b"}})), 150);

  ASSERT_EQ(evaluate_ttl(AndOp({AllOfOp{"a", "b"}, NoneOfOp{"c"}})), 100);
  ASSERT_EQ(evaluate_ttl(OrOp({AllOfOp{"a", "b"}, NoneOfOp{"c"}})), infinity);
}

}  // namespace common
