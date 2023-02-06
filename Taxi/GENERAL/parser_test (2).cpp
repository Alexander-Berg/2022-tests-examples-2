#include <stdexcept>
#include <string>
#include <unordered_map>

#include <gtest/gtest.h>

#include <math-expr/exceptions.hpp>
#include "math-expr/expr.hpp"
#include "math-expr/math-expr.hpp"
#include "parser.hpp"

namespace {

void SetParameters(math_expr::Expr& e,
                   std::unordered_map<std::string, double> parameters) {
  for (const auto& [name, value] : parameters) {
    e.SetParameter(name, value);
  }
}

void TestParse(const std::string& expr, double value,
               const std::unordered_map<std::string, double>& parameters = {}) {
  auto e = math_expr::Parser::Parse(expr);
  SetParameters(e, parameters);
  EXPECT_DOUBLE_EQ(e.Calc(), value);
}

void TestParseLogic(
    const std::string& expr, bool value,
    const std::unordered_map<std::string, double>& parameters = {}) {
  auto e = math_expr::Parser::Parse(expr);
  SetParameters(e, parameters);
  EXPECT_EQ(e.CalcLogic(), value);
}

void TestParseIsInf(
    const std::string& expr,
    const std::unordered_map<std::string, double>& parameters = {}) {
  auto e = math_expr::Parser::Parse(expr);
  SetParameters(e, parameters);
  EXPECT_TRUE(std::isinf(e.Calc()));
}

void TestParseIsNan(
    const std::string& expr,
    const std::unordered_map<std::string, double>& parameters = {}) {
  auto e = math_expr::Parser::Parse(expr);
  SetParameters(e, parameters);
  EXPECT_TRUE(std::isnan(e.Calc()));
}

void TestParseSyntaxError(const std::string& expr) {
  EXPECT_THROW(math_expr::Parser::Parse(expr), math_expr::SyntaxError);
}

void TestCalcUnexpectedExpressionType(const std::string& expr) {
  const auto e = math_expr::Parser::Parse(expr);
  EXPECT_THROW(e.CalcLogic(), math_expr::UnexpectedExpressionType);
}

void TestCalcUndefinedIdentifier(
    const std::string& expr,
    const std::unordered_map<std::string, double>& parameters = {}) {
  auto e = math_expr::Parser::Parse(expr);
  SetParameters(e, parameters);
  EXPECT_THROW(e.Calc(), math_expr::UndefinedIdentifier);
}

}  // namespace

TEST(Parser, ParsePlainLiteral) {
  TestParse("0", 0);
  TestParse("1", 1);
  TestParse("1.", 1);
  TestParse("1.0", 1);
  TestParse("0.43", .43);
  TestParse("4.3", 4.3);
  TestParse("4e3", 4000);
  TestParse("32.6193819415", 32.6193819415);
  TestParse("326193.819415", 326193.819415);
}

TEST(Parser, ParsePlainIdentifier) {
  TestParse("a", 0, {{"a", 0}});
  TestParse("a", 1, {{"a", 1}});
  TestParse("a", 43, {{"a", 43}});
  TestParse("a", .43, {{"a", .43}});
  TestParse("a", 4000, {{"a", 4e3}});
  TestParseIsInf("inf", {{"inf", 1. / 0}});
  TestParseIsNan("nan", {{"nan", 0. / 0}});
}

TEST(Parser, ParseUnaryPlusAndMinus) {
  TestParse("+0", 0);
  TestParse("++0", 0);
  TestParse("-1", -1);
  TestParse("+1", 1);
  TestParse("--1", 1);
  TestParse("+-1", -1);
  TestParse("++-1", -1);
  TestParse("-a", -1, {{"a", 1}});
  TestParse("+a", 1, {{"a", 1}});
  TestParse("--a", 1, {{"a", 1}});
  TestParse("+-a", -1, {{"a", 1}});
  TestParse("++-a", -1, {{"a", 1}});
  TestParse("-0.43", -0.43);
  TestParse("+0.43", +0.43);
  TestParse("--0.43", 0.43);
  TestParse("+-0.43", -0.43);
  TestParse("++-0.43", -0.43);
  TestParse("-a", -0.43, {{"a", 0.43}});
  TestParse("+a", +0.43, {{"a", 0.43}});
  TestParse("--a", 0.43, {{"a", 0.43}});
  TestParse("+-a", -0.43, {{"a", 0.43}});
  TestParse("++-a", -0.43, {{"a", 0.43}});
}

TEST(Parser, ParseLogicNegation) {
  TestParse("!0", true);
  TestParse("!a", true, {{"a", 0}});
  TestParse("!1", false);
  TestParse("!0.43", false);
  TestParse("!43", false);
  TestParse("!4.3", false);
  TestParse("!4e3", false);
  TestParse("!a", false, {{"a", 1}});
  TestParse("!a", false, {{"a", .43}});
  TestParse("!a", false, {{"a", 43}});
}

TEST(Parser, ParseAddition) {
  TestParse("   2  +2", 4);
  TestParse("\t 2\t+2", 4);
  TestParse("  +2  +2", 4);
  TestParse(" ++2  +2", 4);
  TestParse("+++2  +2", 4);
  TestParse("  +2 ++2", 4);
  TestParse(" ++2 ++2", 4);
  TestParse("+++2 ++2", 4);
  TestParse("  +2+++2", 4);
  TestParse(" ++2+++2", 4);
  TestParse("+++2+++2", 4);
  TestParse("+++a+++2", 4, {{"a", 2}});
  TestParse("+++a+++a", 4, {{"a", 2}});
  TestParse("+++a+++b", 4, {{"a", 2}, {"b", 2}});
}

TEST(Parser, ParseSubstraction) {
  TestParse("   2  -2", 0);
  TestParse("\t 2\t-2", 0);
  TestParse("  -2  -2", -4);
  TestParse(" --2  -2", 0);
  TestParse("---2  -2", -4);
  TestParse("  -2 --2", 0);
  TestParse(" --2 --2", 4);
  TestParse("---2 --2", 0);
  TestParse("  -2---2", -4);
  TestParse(" --2---2", 0);
  TestParse("---2---2", -4);
  TestParse("---a---2", -4, {{"a", 2}});
  TestParse("---a---a", -4, {{"a", 2}});
  TestParse("---a---b", -4, {{"a", 2}, {"b", 2}});
}

TEST(Parser, ParseMultiplication) {
  TestParse("   0.43 *    0.43", .1849);
  TestParse("   0.43 *   -0.43", -.1849);
  TestParse("\t 0.43 * \t-0.43", -.1849);
  TestParse("  -0.43 *   -0.43", .1849);
  TestParse(" --0.43 *   -0.43", -.1849);
  TestParse("---0.43 *   -0.43", .1849);
  TestParse("  -0.43 *  --0.43", -.1849);
  TestParse(" --0.43 *  --0.43", .1849);
  TestParse("---0.43 *  --0.43", -.1849);
  TestParse("  -0.43 * ---0.43", .1849);
  TestParse(" --0.43 * ---0.43", -.1849);
  TestParse("---0.43 * ---0.43", .1849);
  TestParse("   0.43 *   -2", -.86);
  TestParse("\t 0.43 * \t-2", -.86);
  TestParse("  -0.43 *   -2", .86);
  TestParse(" --0.43 *   -2", -.86);
  TestParse("---0.43 *   -2", .86);
  TestParse("  -0.43 *  --2", -.86);
  TestParse(" --0.43 *  --2", .86);
  TestParse("---0.43 *  --2", -.86);
  TestParse("  -0.43 * ---2", .86);
  TestParse(" --0.43 * ---2", -.86);
  TestParse("---0.43 * ---2", .86);
  TestParse("---a * ---2", .86, {{"a", .43}});
  TestParse("---a * ---b", .86, {{"a", .43}, {"b", 2}});
}

TEST(Parser, ParseDivision) {
  TestParse("   0.43 /    0.43", 1);
  TestParse("   0.43 /   -0.43", -1);
  TestParse("\t 0.43 / \t-0.43", -1);
  TestParse("  -0.43 /   -0.43", 1);
  TestParse(" --0.43 /   -0.43", -1);
  TestParse("---0.43 /   -0.43", 1);
  TestParse("  -0.43 /  --0.43", -1);
  TestParse(" --0.43 /  --0.43", 1);
  TestParse("---0.43 /  --0.43", -1);
  TestParse("  -0.43 / ---0.43", 1);
  TestParse(" --0.43 / ---0.43", -1);
  TestParse("---0.43 / ---0.43", 1);
  TestParse("   0.43 /   -2", -.215);
  TestParse("\t 0.43 / \t-2", -.215);
  TestParse("  -0.43 /   -2", .215);
  TestParse(" --0.43 /   -2", -.215);
  TestParse("---0.43 /   -2", .215);
  TestParse("  -0.43 /  --2", -.215);
  TestParse(" --0.43 /  --2", .215);
  TestParse("---0.43 /  --2", -.215);
  TestParse("  -0.43 / ---2", .215);
  TestParse(" --0.43 / ---2", -.215);
  TestParse("---0.43 / ---2", .215);
  TestParse("---a / ---2", .215, {{"a", .43}});
  TestParse("---a / ---b", .215, {{"a", .43}, {"b", 2}});
  TestParseIsInf("a", {{"a", 1. / 0}});
  TestParseIsInf("0.43/0");
  TestParseIsNan("a", {{"a", 0. / 0}});
  TestParseIsNan("a/b", {{"a", 1. / 0}, {"b", 1. / 0}});
  TestParseIsNan("0/0");
}

TEST(Parser, ParseLogicAnd) {
  TestParseLogic("1 && 1", true);
  TestParseLogic("1 && 0", false);
  TestParseLogic("0 && 1", false);
  TestParseLogic("0 && 0", false);
  TestParseLogic("a && 1", true, {{"a", 1}});
  TestParseLogic("a && 0", false, {{"a", 1}});
  TestParseLogic("a && 1", false, {{"a", 0}});
  TestParseLogic("a && 0", false, {{"a", 0}});
  TestParseLogic("1 && a", true, {{"a", 1}});
  TestParseLogic("1 && a", false, {{"a", 0}});
  TestParseLogic("0 && a", false, {{"a", 1}});
  TestParseLogic("0 && a", false, {{"a", 0}});
  TestParseLogic("a && b", true, {{"a", 1}, {"b", 1}});
  TestParseLogic("a && b", false, {{"a", 1}, {"b", 0}});
  TestParseLogic("a && b", false, {{"a", 0}, {"b", 1}});
  TestParseLogic("a && b", false, {{"a", 0}, {"b", 0}});
}

TEST(Parser, ParseLogicOr) {
  TestParseLogic("43 || 1", true);
  TestParseLogic("1 || 0", true);
  TestParseLogic("0 || 1", true);
  TestParseLogic("0 || 0", false);
  TestParseLogic("0 && 43 || 0", false);
  TestParseLogic("0 && 1 || 0 || 1 || 0 && 0", true);
}

TEST(Parser, ParseRelOp) {
  TestParseLogic("1>0", true);
  TestParseLogic("0>0.43", false);
  TestParseLogic("a>43", true, {{"a", 1. / 0}});
  TestParseLogic("a>43/0", false, {{"a", 1. / 0}});
  TestParseLogic("a>43", false, {{"a", 0. / 0}});
  TestParseLogic("a>0/0", false, {{"a", 0. / 0}});
  TestParseLogic("1>=0", true);
  TestParseLogic("0>=0.43", false);
  TestParseLogic("0>=0", true);
  TestParseLogic("0<4.3", true);
  TestParseLogic("4.3<0", false);
  TestParseLogic("a<43", false, {{"a", 1. / 0}});
  TestParseLogic("a<43", false, {{"a", 0. / 0}});
  TestParseLogic("0<=4.3", true);
  TestParseLogic("4.3<=0", false);
  TestParseLogic("0<=0", true);
  TestParseLogic("0==0", true);
  TestParseLogic("0!=0", false);
  TestParseLogic("0/0!=0", true);
  TestParseLogic("1/0==0", false);
}

TEST(Parser, ParseParentheses) {
  TestParse("3+9/3", 6);
  TestParse("3+(9/3)", 6);
  TestParse("(3+9/3)", 6);
  TestParse("(4+9)/3", 4.333333333333333);
  TestParseLogic("(0 && 43 || 0)", false);
  TestParseLogic("0 && 1 || (0 || 1 || 0) && 0", false);
  TestParse("(2+2)/2", 2);
  TestParseLogic("!(2+2<5) && 2+3==5", false);
  TestParseLogic("!(2+2<5) || 2+3==5", true);
  TestParse("(min(4,id43)+max(id0,9))/max(id0,1,abs(-3))", 4.333333333333333,
            {{"id43", 43}, {"id0", 0}});
  TestParse("(a + 43) * b - 1", 85.86, {{"a", 0.43}, {"b", 2}});
  TestParse("(a + 43) * b - 1 > 10", true, {{"a", 0.43f}, {"b", 2}});
  TestParse("(a + 43) * b - 1 > 10 && b > a", true, {{"a", 0.43f}, {"b", 2}});
}

TEST(Parser, ParseFunctionCall) {
  TestParse("abs(0)", 0);
  TestParse("abs(1)", 1);
  TestParse("abs(-1)", 1);
  TestParse("abs(abs(-1))", 1);
  TestParse("abs(abs(abs(-1)))", 1);
  TestParse("abs(-a)", 43, {{"a", 43}});
  TestParse("min(43,0)", 0);
  TestParse("min(-43,0)", -43);
  TestParse("min(43, 4.3)", 4.3);
  TestParse("min(0, 43, 4.3)", 0);
  TestParse("min(0, 43, 4.3, -4.3)", -4.3);
  TestParse("min(0, 43, 4.3, -4.3, -43)", -43);
  TestParse("min(43,0) + min(-43,0,43) + min(43, 4.3)", -38.7);
  TestParse("max(43,0)", 43);
  TestParse("max(-43, 0)", 0);
  TestParse("max(43, 4.3)", 43);
  TestParse("max(0, 4.3)", 4.3);
  TestParse("max(0, 43, 4.3)", 43);
  TestParse("max(0, 43, 4.3, -4.3)", 43);
  TestParse("max(0, 43, 4.3, -4.3, -43)", 43);
  TestParse("max + 3 == 43", true, {{"max", 40}});
  TestParse("min + 3 == 43", true, {{"min", 40}});
  TestParse("abs + 3 == 43", true, {{"abs", 40}});
}

TEST(Parser, ParseMisc) {
  TestParse("max(0,43,4.3)+max(0,43,4.3,-4.3)+max(0,43,4.3,-4.3,-43)", 129);
  TestParse("max(0,43,4.3)+max(0,43,4.3,-4.3)+min(0,43,4.3,-4.3,-43)", 43);
  TestParse("min(a,b)<0 && max(a,b)>0", true, {{"a", 1}, {"b", -1}});
  TestParse("min(a,b)<0 && max(a,b)>0", true, {{"a", 1}, {"b", -1}});
  TestParse("4/2-3", -1);
  TestParse("-2+4/2-3*2", -6);
  TestParse("2*2/3 + 7/6", 2.5);
  TestParse("43./5", 43. / 5);
  TestParse("2+2<5", true);
  TestParseLogic("2+2<5 && 2+3==5", true);
  TestParseLogic("0.43 < 1", true);
  TestParse("(0.43 + 43) * 2 - 1", 85.86);
  TestParse("a + + + + 2 < 10", true, {{"a", 5}});
  TestParse("a + 2", 7, {{"a", 5}});
  TestParse("a/b + c + 0.125", 1.678571428571429,
            {{"a", 10}, {"b", 7}, {"c", 0.125}});
  TestParseLogic("0 && 1 || 0", false);
  TestParseLogic("0 && 1 || (0 || 1 || 0) && 0", false);
  TestParseLogic("0 && 1 || 0 || 1 || 0 && 0", true);
}

TEST(Parser, ParseSyntaxError) {
  TestParseSyntaxError("");
  TestParseSyntaxError("$$$!!!");
  TestParseSyntaxError("(2+2");
  TestParseSyntaxError("2+/2");
  TestParseSyntaxError("2//2");
  TestParseSyntaxError("2**2");
  TestParseSyntaxError("2+2)");
  TestParseSyntaxError("2(+)2");
  TestParseSyntaxError("((2+2)");
  TestParseSyntaxError("(2+2))");
  TestParseSyntaxError("a b");
  TestParseSyntaxError("a b c");
  TestParseSyntaxError("a b - c");
  TestParseSyntaxError("a - b c");
  TestParseSyntaxError("abs()");
  TestParseSyntaxError("abs(a,b)");
  TestParseSyntaxError("abs(a,b,c)");
  TestParseSyntaxError("min()");
  TestParseSyntaxError("min(a)");
  TestParseSyntaxError("max()");
  TestParseSyntaxError("max(a)");
  TestParseSyntaxError("not_supported_fun(a)");
  TestParseSyntaxError("not_supported_fun(a,b)");
  TestParseSyntaxError("not_supported_fun(a,b,c)");
}

TEST(Parser, CalcUndefinedIdentifier) {
  TestCalcUndefinedIdentifier("a + 2 < 0");
  TestCalcUndefinedIdentifier("a + b + 2 < 0", {{"a", 43}});
}

TEST(Parser, CalcUnexpectedExpressionType) {
  TestCalcUnexpectedExpressionType("43.");
  TestCalcUnexpectedExpressionType("43. + 0.");
}
