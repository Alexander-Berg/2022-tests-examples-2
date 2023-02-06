#include <gtest/gtest.h>

#include <functional>

#include <pricing-functions/parser/any_expression.hpp>
#include <pricing-functions/parser/identifier.hpp>

class Identifier
    : public ::testing::TestWithParam<std::tuple<std::string, bool>> {};

TEST_P(Identifier, Parse) {
  using boost::spirit::ascii::space;
  using boost::spirit::qi::eps;
  using parser::qi::labels::_a;

  const auto [str, pass] = GetParam();

  lang::models::Identifier result;
  auto iter = str.cbegin();
  parser::Identifier identifier;
  parser::Rule<lang::models::Identifier(),
               parser::qi::locals<parser::models::ParseContext>>
      g;
  lang::models::Program prg;
  parser::models::ParseContext context(prg);
  g %= eps[_a = boost::ref(context)] >>
       identifier(boost::spirit::qi::labels::_a);

  parser::Skipper skipper = space;
  ASSERT_EQ(phrase_parse(iter, str.cend(), g, skipper, result) &&
                (iter == str.cend()),
            pass);
  if (pass) {
    ASSERT_EQ(result.GetName(), str);
  }
}

INSTANTIATE_TEST_SUITE_P(Identifier, Identifier,
                         ::testing::Values(std::make_tuple("a", true),       //
                                           std::make_tuple("_a", true),      //
                                           std::make_tuple("a_", true),      //
                                           std::make_tuple("2s", false),     //
                                           std::make_tuple("s3", true),      //
                                           std::make_tuple("__2", true),     //
                                           std::make_tuple("__2 d", false),  //
                                           std::make_tuple("", false)        //
                                           ));
