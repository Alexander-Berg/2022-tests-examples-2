#include <ostream>
#include <variant>
#include <vector>

#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include "lexer.hpp"
#include "token.hpp"

namespace math_expr {

namespace {

void TestLex(const std::string& expr, std::vector<Token> tokens) {
  math_expr::Lexer lex(expr);

  std::vector<testing::Matcher<Token>> matchers;
  matchers.reserve(tokens.size());

  while (true) {
    const auto token = lex.Lex();

    matchers.push_back(testing::AllOf(
        testing::Field("type", &Token::type, token.type),
        testing::Field("identifier_data", &Token::identifier_data,
                       token.identifier_data),
        testing::Field("numeric_literal_value", &Token::numeric_literal_value,
                       testing::DoubleEq(token.numeric_literal_value))));

    if (token.type == TokenType::kEof) {
      break;
    }
  }

  ASSERT_THAT(tokens, testing::ElementsAreArray(matchers));
}

const Token kUnknown{TokenType::kUnknown};
const Token kEof{TokenType::kEof};
const Token kPlus{TokenType::kPlus};
const Token kMinus{TokenType::kMinus};
const Token kComma{TokenType::kComma};
const Token kAmpAmp{TokenType::kAmpAmp};
const Token kPipePipe{TokenType::kPipePipe};
const Token kEqualEqual{TokenType::kEqualEqual};
const Token kExclaimEqual{TokenType::kExclaimEqual};
const Token kExclaim{TokenType::kExclaim};
const Token kLess{TokenType::kLess};
const Token kLessEqual{TokenType::kLessEqual};
const Token kGreater{TokenType::kGreater};
const Token kGreaterEqual{TokenType::kGreaterEqual};
const Token kStar{TokenType::kStar};
const Token kSlash{TokenType::kSlash};
const Token kLParen{TokenType::kLParen};
const Token kRParen{TokenType::kRParen};
const Token kMin{TokenType::kMin, "min"};
const Token kMax{TokenType::kMax, "max"};
const Token kAbs{TokenType::kAbs, "abs"};
const Token kUndscrId{TokenType::kIdentifier, "_id"};
const Token kJustI{TokenType::kIdentifier, "i"};
const Token kIdentifierUndscr0{TokenType::kIdentifier, "identifier_0"};
const Token kJust43{TokenType::kNumericConstant, 43};
const Token kPoint43{TokenType::kNumericConstant, .43};
const Token kZero{TokenType::kNumericConstant, 0};

}  // namespace

// Pretty printers

inline void PrintTo(const TokenType& type, std::ostream* os) {
  *os << "'" << static_cast<size_t>(type) << "'";
}

inline void PrintTo(const Token& token, std::ostream* os) {
  *os << "type: ";
  PrintTo(token.type, os);
  *os << ", identifier_data: '" << token.identifier_data
      << "', numeric_literal_value: " << token.numeric_literal_value;
}

inline void PrintTo(const std::vector<Token>& tokens, std::ostream* os) {
  *os << '\n';
  for (size_t i = 0; i < tokens.size(); i++) {
    *os << "element #" << i << " ";
    PrintTo(tokens[i], os);
    *os << '\n';
  }
}

}  // namespace math_expr

TEST(Lexer, Lex) {
  math_expr::TestLex("", {math_expr::kEof});
  math_expr::TestLex("+", {math_expr::kPlus, math_expr::kEof});
  math_expr::TestLex("-", {math_expr::kMinus, math_expr::kEof});
  math_expr::TestLex(",", {math_expr::kComma, math_expr::kEof});
  math_expr::TestLex("&&", {math_expr::kAmpAmp, math_expr::kEof});
  math_expr::TestLex("||", {math_expr::kPipePipe, math_expr::kEof});
  math_expr::TestLex("==", {math_expr::kEqualEqual, math_expr::kEof});
  math_expr::TestLex("min", {math_expr::kMin, math_expr::kEof});
  math_expr::TestLex("max", {math_expr::kMax, math_expr::kEof});
  math_expr::TestLex("abs", {math_expr::kAbs, math_expr::kEof});
  math_expr::TestLex("_id", {math_expr::kUndscrId, math_expr::kEof});
  math_expr::TestLex("i", {math_expr::kJustI, math_expr::kEof});
  math_expr::TestLex("43", {math_expr::kJust43, math_expr::kEof});
  math_expr::TestLex("0.43", {math_expr::kPoint43, math_expr::kEof});
  math_expr::TestLex("0", {math_expr::kZero, math_expr::kEof});
  math_expr::TestLex("identifier_0",
                     {math_expr::kIdentifierUndscr0, math_expr::kEof});
  math_expr::TestLex(
      "===", {math_expr::kEqualEqual, math_expr::kUnknown, math_expr::kEof});
  math_expr::TestLex(
      "_id/43==\t\t\f0$$",
      {math_expr::kUndscrId, math_expr::kSlash, math_expr::kJust43,
       math_expr::kEqualEqual, math_expr::kZero, math_expr::kUnknown,
       math_expr::kUnknown, math_expr::kEof});
  math_expr::TestLex("!(identifier_0 > 0)",
                     {math_expr::kExclaim, math_expr::kLParen,
                      math_expr::kIdentifierUndscr0, math_expr::kGreater,
                      math_expr::kZero, math_expr::kRParen, math_expr::kEof});
  math_expr::TestLex("_id-43 == 0", {math_expr::kUndscrId, math_expr::kMinus,
                                     math_expr::kJust43, math_expr::kEqualEqual,
                                     math_expr::kZero, math_expr::kEof});
  math_expr::TestLex(
      "\t_id + 43 <= 0.43",
      {math_expr::kUndscrId, math_expr::kPlus, math_expr::kJust43,
       math_expr::kLessEqual, math_expr::kPoint43, math_expr::kEof});
  math_expr::TestLex(
      "_id+ 43 <=0.43",
      {math_expr::kUndscrId, math_expr::kPlus, math_expr::kJust43,
       math_expr::kLessEqual, math_expr::kPoint43, math_expr::kEof});
  math_expr::TestLex("_id+43<=0.43", {math_expr::kUndscrId, math_expr::kPlus,
                                      math_expr::kJust43, math_expr::kLessEqual,
                                      math_expr::kPoint43, math_expr::kEof});
  math_expr::TestLex(
      "((identifier_0 + _id)/0.43 + i*0.43 >= 0) && 0 < _id || i != 0.43",
      {math_expr::kLParen,
       math_expr::kLParen,
       math_expr::kIdentifierUndscr0,
       math_expr::kPlus,
       math_expr::kUndscrId,
       math_expr::kRParen,
       math_expr::kSlash,
       math_expr::kPoint43,
       math_expr::kPlus,
       math_expr::kJustI,
       math_expr::kStar,
       math_expr::kPoint43,
       math_expr::kGreaterEqual,
       math_expr::kZero,
       math_expr::kRParen,
       math_expr::kAmpAmp,
       math_expr::kZero,
       math_expr::kLess,
       math_expr::kUndscrId,
       math_expr::kPipePipe,
       math_expr::kJustI,
       math_expr::kExclaimEqual,
       math_expr::kPoint43,
       math_expr::kEof});
}
