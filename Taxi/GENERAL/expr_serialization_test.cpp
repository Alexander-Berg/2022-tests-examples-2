#include <string>
#include <unordered_map>

#include <gtest/gtest.h>

#include <math-expr/expr.hpp>
#include <math-expr/math-expr.hpp>

namespace {

void TestSerialize(const std::string& expr,
                   std::unordered_map<std::string, double> parameters = {}) {
  auto e1 = math_expr::Parse(expr);
  for (const auto& [name, value] : parameters) {
    e1.SetParameter(name, value);
  }
  const auto value = e1.Calc();
  auto json = e1.ToJson();
  const auto e2 = math_expr::Expr::FromJson(json);
  EXPECT_DOUBLE_EQ(e2.Calc(), value);
}

}  // namespace

TEST(Expr, Serialize) {
  TestSerialize("max(0,43,4.3)+max(0,43,4.3,-4.3)+max(0,43,4.3,-4.3,-43)");
  TestSerialize("max(0,43,4.3)+max(0,43,4.3,-4.3)+min(0,43,4.3,-4.3,-43)");
  TestSerialize("min(a,b)<0 && max(a,b)>0", {{"a", 1}, {"b", -1}});
  TestSerialize("min(a,b)<0 && max(a,b)>0", {{"a", 1}, {"b", -1}});
  TestSerialize("4/2-3");
  TestSerialize("-2+4/2-3*2");
  TestSerialize("2*2/3 + 7/6");
  TestSerialize("43./5");
  TestSerialize("2+2<5");
  TestSerialize("2+2<5 && 2+3==5");
  TestSerialize("0.43 < 1");
  TestSerialize("(0.43 + 43) * 2 - 1");
  TestSerialize("a + + + + 2 < 10", {{"a", 5}});
  TestSerialize("a + 2", {{"a", 5}});
  TestSerialize("a/b + c + 0.125", {{"a", 10}, {"b", 7}, {"c", 0.125}});
  TestSerialize("0 && 1 || 0");
  TestSerialize("0 && 1 || (0 || 1 || 0) && 0");
  TestSerialize("0 && 1 || 0 || 1 || 0 && 0");
}
