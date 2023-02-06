#include <gtest/gtest.h>

#include <functional>
#include <pricing-functions/lang/internal/backend_variables_io.hpp>
#include <pricing-functions/parser/scalar.hpp>
#include <utils/variant_match.hpp>

TEST(Double, Simple) {
  using boost::spirit::ascii::space;

  const std::string str = "2.3";
  lang::models::Scalar scalar;
  auto iter = str.cbegin();
  parser::Scalar<double> sg;
  parser::Rule<lang::models::Scalar(),
               parser::qi::locals<parser::models::ParseContext>>
      g;
  g = sg(boost::spirit::qi::labels::_a);

  parser::Skipper skipper = space;
  ASSERT_TRUE(phrase_parse(iter, str.cend(), g, skipper, scalar));
  ASSERT_EQ(iter, str.cend());
  ASSERT_EQ(scalar.Get<double>(), 2.3);
}

TEST(String, String) {
  using boost::spirit::ascii::space;

  const std::string str = "\"hello_2132 dd\"";
  lang::models::Scalar scalar;
  auto iter = str.cbegin();
  parser::Scalar<std::string> sg;
  parser::Rule<lang::models::Scalar(),
               parser::qi::locals<parser::models::ParseContext>>
      g;
  g = sg(boost::spirit::qi::labels::_a);
  parser::Skipper skipper = space;
  ASSERT_TRUE(phrase_parse(iter, str.cend(), g, skipper, scalar));
  ASSERT_EQ(iter, str.cend());
  ASSERT_EQ(scalar.Get<std::string>(), "hello_2132 dd");
}

TEST(Enum, Enum) {
  using boost::spirit::ascii::space;
  using boost::spirit::qi::eps;
  using boost::spirit::qi::labels::_a;
  const std::string str =
      "handlers::libraries::pricing_functions::ForcedSkipLabel::kWithoutSurge";
  lang::models::Scalar scalar;
  auto iter = str.cbegin();
  parser::Scalar<lang::variables::ForcedSkipLabel> sg;
  parser::Rule<lang::models::Scalar(),
               parser::qi::locals<parser::models::ParseContext>>
      g;
  lang::models::Program prg;
  parser::models::ParseContext context(prg);
  g %= eps[_a = boost::ref(context)] >> sg(_a);
  parser::Skipper skipper = space;
  ASSERT_TRUE(phrase_parse(iter, str.cend(), g, skipper, scalar));
  ASSERT_EQ(iter, str.cend());
  ASSERT_EQ(scalar.Get<lang::variables::ForcedSkipLabel>(),
            lang::variables::ForcedSkipLabel::kWithoutSurge);
}

TEST(Boolean, True) {
  using boost::spirit::ascii::space;

  const std::string str = "true";
  lang::models::Scalar scalar;
  auto iter = str.cbegin();
  parser::Scalar<bool> sg;
  parser::Rule<lang::models::Scalar(),
               parser::qi::locals<parser::models::ParseContext>>
      g;
  g = sg(boost::spirit::qi::labels::_a);
  parser::Skipper skipper = space;
  ASSERT_TRUE(phrase_parse(iter, str.cend(), g, skipper, scalar));
  ASSERT_EQ(iter, str.cend());
  ASSERT_EQ(scalar.Get<bool>(), true);
}

TEST(Boolean, False) {
  using boost::spirit::ascii::space;

  const std::string str = "false";
  lang::models::Scalar scalar;
  auto iter = str.cbegin();
  parser::Scalar<bool> sg;
  parser::Rule<lang::models::Scalar(),
               parser::qi::locals<parser::models::ParseContext>>
      g;
  g = sg(boost::spirit::qi::labels::_a);
  parser::Skipper skipper = space;
  ASSERT_TRUE(phrase_parse(iter, str.cend(), g, skipper, scalar));
  ASSERT_EQ(iter, str.cend());
  ASSERT_EQ(scalar.Get<bool>(), false);
}
