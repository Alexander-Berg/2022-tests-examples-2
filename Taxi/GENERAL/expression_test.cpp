#include <gtest/gtest.h>

#include <boost/spirit/include/phoenix_core.hpp>
#include <boost/spirit/include/phoenix_operator.hpp>
#include <functional>
#include <pricing-functions/parser/any_expression.hpp>
#include <utils/variant_match.hpp>

#include <pricing-functions/parser/any_expression.hpp>
#include <pricing-functions/parser/error_util.hpp>
#include <pricing-functions/parser/exceptions.hpp>
#include <pricing-functions/parser/type_utils.hpp>

namespace {

static lang::models::Program prg;

parser::models::ParseContext Context(const std::string& name,
                                     const lang::models::Expression& expr) {
  parser::models::ParseContext ctx(prg);
  ctx.AddVariable(ctx.MakeIdentifier(name), expr);
  return ctx;
}

struct ExpressionTestData {
  std::string source;
  std::type_index type;
  parser::models::ParseContext variables;

  std::function<void(
      const ExpressionTestData&,
      const parser::Rule<lang::models::Expression(),
                         parser::qi::locals<parser::models::ParseContext>>&)>
      check_override;

  void CheckSuccess(
      const parser::Rule<lang::models::Expression(),
                         parser::qi::locals<parser::models::ParseContext>>& g)
      const {
    if (check_override) {
      check_override(*this, g);
      return;
    }

    using boost::spirit::ascii::space;

    parser::Skipper skipper = space;
    lang::models::Expression expr;
    auto iter = source.cbegin();
    try {
      ASSERT_TRUE(phrase_parse(iter, source.cend(), g, skipper, expr));
    } catch (
        const boost::spirit::qi::expectation_failure<parser::Iterator>& e) {
      throw parser::ParseException(source + ": " + parser::PrintInfo(e.what_));
    }
    ASSERT_EQ(iter, source.cend());
    ASSERT_EQ(expr.GetType().GetTypeName(), parser::MakeTypeName(type));
  }

  void CheckThrow(
      const parser::Rule<lang::models::Expression(),
                         parser::qi::locals<parser::models::ParseContext>>& g,
      size_t off) const {
    using boost::spirit::ascii::space;

    parser::Skipper skipper = space;
    lang::models::Expression expr;
    auto iter = source.cbegin();
    try {
      phrase_parse(iter, source.cend(), g, skipper, expr);
      FAIL();
    } catch (
        const boost::spirit::qi::expectation_failure<parser::Iterator>& re) {
      EXPECT_EQ(std::distance(source.begin(), re.first), off);
    }
  }

  ExpressionTestData Throw(size_t off) const {
    ExpressionTestData result = *this;
    result.check_override =
        [off](const ExpressionTestData& o,
              const parser::Rule<
                  lang::models::Expression(),
                  parser::qi::locals<parser::models::ParseContext>>& g) {
          o.CheckThrow(g, off);
        };
    return result;
  }
};

template <typename T>
ExpressionTestData Expr(const std::string& str,
                        const parser::models::ParseContext& variables =
                            parser::models::ParseContext(prg)) {
  return {str, typeid(T), variables, {}};
}

lang::models::Expression kBoolScalar =
    lang::models::Expression{lang::models::Scalar{false}};
lang::models::Expression kDoubleScalar =
    lang::models::Expression{lang::models::Scalar{0.5}};

}  // namespace

class Expression : public ::testing::TestWithParam<ExpressionTestData> {};

TEST_P(Expression, Parse) {
  using boost::spirit::ascii::space;
  using parser::qi::eps;
  using parser::qi::labels::_1;
  using parser::qi::labels::_a;
  using parser::qi::labels::_val;

  const auto data = GetParam();

  parser::AnyExpression exp_g{};
  parser::Rule<lang::models::Expression(),
               parser::qi::locals<parser::models::ParseContext>>
      g;

  g = eps[_a = boost::cref(data.variables)] >> exp_g(_a)[_val = _1];

  data.CheckSuccess(g);
}

INSTANTIATE_TEST_SUITE_P(                                                  //
    Expression, Expression,                                                //
    ::testing::Values(                                                     //
        Expr<std::unordered_set<std::string>>("fix.user_tags"),            // 0
        Expr<std::unordered_map<std::string, double>>(                     //
            "fix.tariff.requirement_prices"),                              //
        Expr<std::string>("\"some_string\""),                              //
        Expr<bool>("!(1>2)"),                                              //
        Expr<bool>("1>2"),                                                 //
        Expr<bool>("!(1>2)"),                                              //
        Expr<bool>("true"),                                                //
        Expr<bool>("2>3 == 3 < 4"),                                        //
        Expr<bool>("\"test\" in fix.user_tags"),                           //
        Expr<bool>("b", Context("b", kBoolScalar)),                        //
        Expr<bool>("b && b", Context("b", kBoolScalar)),                   // 10
        Expr<bool>("(b) ? !b : b && b", Context("b", kBoolScalar)),        //
        Expr<bool>("\"hello\" in fix.requirements.select"),                //
        Expr<double>("2"),                                                 //
        Expr<double>("-1"),                                                //
        Expr<double>("-(2+4)"),                                            //
        Expr<double>("2+2*2"),                                             //
        Expr<double>("(2+2)*2"),                                           //
        Expr<double>("2 + (2 + 3)"),                                       //
        Expr<double>("b", Context("b", kDoubleScalar)),                    //
        Expr<double>("b + 2", Context("b", kDoubleScalar)),                // 20
        Expr<double>("sin(2+3)"),                                          //
        Expr<double>("(2>4) ? 5 : 4+6"),                                   //
        Expr<double>("fix.tariff.boarding_price"),                         //
        Expr<double>("fix.tariff.requirement_prices[\"hello\"]"),          //
        Expr<double>("*(ride.price)"),                                     //
        Expr<double>("*ride.price"),                                       //
        Expr<double>(                                                      //
            "(fix.surge_params.surcharge_alpha as alpha) ? alpha : 0"),    //
        Expr<double>("2 + 2"),                                             //
        Expr<double>("fix.tariff.waiting_price.free_waiting_time"),        //
        Expr<double>("(fix.coupon as c) ? (c.percent as p) ? p : 0 : 0"),  // 30
        Expr<double>("(fix.coupon.value as v) ? v : 0"),                   //
        Expr<std::optional<int>>("fix.coupon.percent"),                    //
        Expr<double>("(fix.coupon.percent as p) ? p : 0"),                 //
        Expr<double>("ride.ride.waiting_time"),                            //
        Expr<double>("ride.ride.waiting_in_transit_time"),                 //
        Expr<double>("ride.ride.waiting_in_destination_time"),             //
        Expr<double>("ride.ride.waiting_time"),                            //
        Expr<double>("trip.time"),                                         //
        Expr<double>("(fix.discount as disc) ? "                           //
                     "(disc.calc_data_table_data as tbl) ?"                //
                     " length(tbl) : 0 : 0"),                              //
        Expr<bool>("!2").Throw(1),                                         // 40
        Expr<bool>("2 + \"s\"").Throw(3),                                  //
        Expr<bool>("(fix.discount as disc) ? "                             //
                   "disc.id == \"id\" :"                                   //
                   "0 < 1"),                                               //
        Expr<price_calc::models::Price>("ride.price * 4"),                 //
        Expr<price_calc::models::Price>("4 * ride.price"),                 //
        Expr<double>("round_to(10, 1)")                                    //
        )                                                                  //
);
