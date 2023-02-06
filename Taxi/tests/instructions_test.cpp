#include <gmock/gmock-matchers.h>
#include <gtest/gtest.h>

#include <userver/logging/log.hpp>
#include <userver/utest/utest.hpp>

#include <pricing-functions/lang/models/calc_context.hpp>
#include <pricing-functions/lang/models/expressions/scalar.hpp>
#include <pricing-functions/lang/models/expressions/tuple.hpp>
#include <pricing-functions/lang/models/instructions/assertion.hpp>
#include <pricing-functions/lang/models/instructions/assumption.hpp>
#include <pricing-functions/lang/models/instructions/condition.hpp>
#include <pricing-functions/lang/models/instructions/feature_guard.hpp>
#include <pricing-functions/lang/models/instructions/generate.hpp>
#include <pricing-functions/lang/models/instructions/store_value.hpp>
#include <pricing-functions/lang/models/link_context.hpp>
#include <pricing-functions/lang/models/program.hpp>
#include <pricing-functions/lang/models/scalars/value.hpp>
#include <pricing-functions/lang/models/type_mapper.hpp>
#include <pricing-functions/parser/exceptions.hpp>
#include <pricing-functions/parser/type_utils.hpp>
#include <pricing-functions/parser/typename_maker.hpp>

namespace lmi = lang::models::instructions;
namespace lme = lang::models::expressions;
namespace lm = lang::models;

namespace {

class Instructions : public testing::Test {
 protected:
  static void SetUpTestSuite() {}

  static void TearDownTestSuite() { parser::ResetTypeinfoMaps(); }

  void SetUp() override {}

  void TearDown() override {}
};

template <template <typename...> class Container, typename T>
auto WrapContainerIdentifiers(Container<std::string, T>&& data) {
  Container<lm::Identifier, T> transformed_data{};
  std::transform(
      data.begin(), data.end(),
      std::inserter(transformed_data, transformed_data.end()), [](auto& kv) {
        return std::make_pair<lm::Identifier, T>(
            lm::CreateGlobalIdentifier(kv.first), std::move(kv.second));
      });
  return transformed_data;
}

template <typename T>
lm::Expression MakeRefScalar(const T& value) {
  return lm::Expression{
      std::make_shared<lme::Scalar>(lm::Scalar{std::cref(value)})};
}

template <typename T>
lm::Expression MakeScalar(T&& value) {
  return lm::Expression{std::make_shared<lme::Scalar>(
      lm::Scalar{lm::scalars::Value<T>{std::move(value)}})};
}

template <typename T>
lm::Expression MakeTaxVariable(const std::vector<size_t>& path) {
  lm::scalars::TaximeterVariable tax_variable{
      lm::Type{lm::types::PrimitiveType{typeid(T)}}, path};
  lm::Scalar scalar{tax_variable};
  return lm::Expression{std::make_shared<lme::Scalar>(scalar)};
}

template <typename T>
void RegisterType() {
  lang::models::types::MakeTypeMapping<T>();
  parser::AddTypeinfo(parser::details::TypeNameMaker<T>::Make(), typeid(T));
}

struct Context {
  lang::models::Program ast{};
  lang::models::FeaturesSet features = lang::models::ListLatestFeatures();
  lang::models::CalcContext calc_context{ast, features, true};
  lang::models::LinkContext link_context{ast, features, {}};
  price_calc::models::BinaryData bytecode{};
  lang::models::GlobalCompilationContext compilation_context{};
  price_calc::utils::OutputCodeStream os{bytecode, compilation_context};
  lang::models::CalcContext calc_prod_context{ast, features, false};
};

lm::Block MakeReturnBlock(const lm::Expression& expr) {
  lm::Block result;
  result.AddReturn(expr);
  return result;
}

lm::Expression MakeTuple(std::map<std::string, lm::Expression>&& data) {
  return lm::Expression{
      std::make_shared<lme::Tuple>(WrapContainerIdentifiers(std::move(data)))};
}

}  // namespace

namespace tests::instructions {

struct SomeStruct {
  int x;
};

}  // namespace tests::instructions

BOOST_FUSION_ADAPT_STRUCT(tests::instructions::SomeStruct, (int, x))

TEST_F(Instructions, GenerateOps) {
  std::vector<tests::instructions::SomeStruct> nums;
  RegisterType<std::vector<tests::instructions::SomeStruct>>();
  Context ctx{};
  lmi::Generate generate{
      {{lm::CreateGlobalIdentifier("x"), MakeScalar<double>(1)}},
      lm::CreateGlobalIdentifier("it"),
      MakeRefScalar(nums),
      {},
      {{lm::CreateGlobalIdentifier("x"), MakeScalar<double>(1)}}};

  ASSERT_EQ(generate.Serialize(),
            "GENERATE(L(it,Ref<std::vector<tests::instructions::SomeStruct>>),"
            "I(x=1.000000),C(),U(x=1.000000))");
  ASSERT_FALSE(generate.HasMeta("x"));
  ASSERT_FALSE(generate.GetType().has_value());
}

TEST_F(Instructions, GenerateInvalidUsages) {
  std::vector<tests::instructions::SomeStruct> nums;
  RegisterType<std::vector<tests::instructions::SomeStruct>>();
  Context ctx{};
  lmi::Generate generate_unresolved_container{
      {{lm::CreateGlobalIdentifier("x"), MakeScalar<double>(1)}},
      lm::CreateGlobalIdentifier("it"),
      MakeTaxVariable<std::vector<int>>({1, 2, 3}),
      {},
      {{lm::CreateGlobalIdentifier("x"), MakeScalar<double>(1)}}};

  ASSERT_THROW(generate_unresolved_container.Link(ctx.link_context),
               std::invalid_argument);
}

TEST_F(Instructions, HasMetaCheck) {
  Context ctx{};
  lmi::StoreValue sv{lm::CreateGlobalIdentifier("x"), MakeScalar<double>(1)};
  ASSERT_FALSE(sv.HasMeta("x"));

  lmi::FeatureGuard fg{ctx.features, lm::Block{}};
  ASSERT_FALSE(fg.HasMeta("x"));
}

TEST_F(Instructions, FeatureGuardGetType) {
  Context ctx{};
  lmi::FeatureGuard fg{ctx.features, lm::Block{}};
  lmi::FeatureGuard fg_double_ret{
      ctx.features, MakeReturnBlock(MakeTuple({{"x", MakeScalar<double>(3)}}))};
  ASSERT_FALSE(fg.GetType().has_value());
  ASSERT_TRUE(fg_double_ret.GetType()->IsOptional());
  ASSERT_TRUE(fg_double_ret.GetType()->InnerType().IsComposite());
  ASSERT_TRUE(fg_double_ret.GetType()->InnerType().HasField(
      lm::CreateGlobalIdentifier("x")));
}

TEST_F(Instructions, ConditionOps) {
  /* if (true) { return {res=1}; } */
  lmi::Condition cond{
      MakeScalar<bool>(true),
      MakeReturnBlock(MakeTuple({{"res", MakeScalar<double>(1)}})),
      std::nullopt};
  ASSERT_FALSE(cond.HasReturn());
  ASSERT_FALSE(cond.HasMeta("x"));
  ASSERT_EQ(cond.Serialize(), "IF(true,CR(res=1.000000))");

  /* if (true) { return {res=1}; } else { return {res=2}; } */
  lmi::Condition cond_two_rets{
      MakeScalar<bool>(true),
      MakeReturnBlock(MakeTuple({{"res", MakeScalar<double>(1)}})),
      MakeReturnBlock(MakeTuple({{"res", MakeScalar<double>(2)}}))};
  ASSERT_TRUE(cond_two_rets.HasReturn());
  ASSERT_EQ(cond_two_rets.Serialize(),
            "IF(true,CR(res=1.000000),CR(res=2.000000))");
}

TEST_F(Instructions, ConditionLink) {
  Context ctx{};
  auto tuple_res_1 = MakeTuple({{"res", MakeScalar<double>(1)}});
  auto tuple_res_2 = MakeTuple({{"res", MakeScalar<double>(2)}});

  {
    /* if (true) { return {res=1}; } */
    lmi::Condition cond{MakeScalar<bool>(true), MakeReturnBlock(tuple_res_1),
                        std::nullopt};
    ASSERT_EQ(cond.Link(ctx.link_context).expression->Serialize(),
              "NT(res=1.000000)");
    ASSERT_EQ(cond.GetType().value(), tuple_res_1.GetType());
  }

  {
    /* if (false) { return {res=1}; } */
    lmi::Condition cond{MakeScalar<bool>(false), MakeReturnBlock(tuple_res_1),
                        std::nullopt};
    ASSERT_FALSE(cond.Link(ctx.link_context).expression.has_value());
    ASSERT_EQ(cond.GetType(), tuple_res_1.GetType());
  }

  {
    /* if (tax_var) { return {res=1}; } else { return {res=2}; } */
    lmi::Condition cond{MakeTaxVariable<bool>({1, 2, 3}),
                        MakeReturnBlock(tuple_res_1),
                        MakeReturnBlock(tuple_res_2)};
    ASSERT_EQ(cond.Link(ctx.link_context).expression->Serialize(),
              "T(TX(1,2,3),NT(res=1.000000),NT(res=2.000000))");
    ASSERT_EQ(cond.GetType(), tuple_res_1.GetType());
  }

  {
    /* if (tax_var) { if (false) { return {res=1};} } */
    lm::Block inner{};
    inner.AddCondition(MakeScalar<bool>(false), MakeReturnBlock(tuple_res_1),
                       std::nullopt);
    lmi::Condition cond{MakeTaxVariable<bool>({1, 2, 3}), inner, std::nullopt};
    ASSERT_FALSE(cond.Link(ctx.link_context).expression.has_value());
    ASSERT_TRUE(cond.Link(ctx.link_context).expression_factory == nullptr);
    ASSERT_EQ(cond.GetType(), tuple_res_1.GetType());
  }

  {
    /* if (tax_var) { if (false) { return {res=1};} } else { if (false) { return
     * {res=1};} } */
    lm::Block inner{};
    inner.AddCondition(MakeScalar<bool>(false), MakeReturnBlock(tuple_res_1),
                       std::nullopt);
    lmi::Condition cond{MakeTaxVariable<bool>({1, 2, 3}), inner, inner};
    ASSERT_FALSE(cond.Link(ctx.link_context).expression.has_value());
    ASSERT_TRUE(cond.Link(ctx.link_context).expression_factory == nullptr);
    ASSERT_EQ(cond.GetType(), tuple_res_1.GetType());
  }

  {
    /* if (tax_var) { if (true) { return {res=1};} } */
    lm::Block inner{};
    inner.AddCondition(MakeScalar<bool>(true), MakeReturnBlock(tuple_res_1),
                       std::nullopt);
    lmi::Condition cond{MakeTaxVariable<bool>({1, 2, 3}), inner, std::nullopt};
    ASSERT_FALSE(cond.Link(ctx.link_context).expression.has_value());
    ASSERT_EQ(
        cond.Link(ctx.link_context).expression_factory(tuple_res_2).Serialize(),
        "T(TX(1,2,3),NT(res=1.000000),NT(res=2.000000))");
    ASSERT_EQ(cond.GetType(), tuple_res_1.GetType());
  }

  {
    /* if (tax_var) { if (true) { return {res=1};} } else { if (false) { return
     * {res=2}; } } */
    lm::Block linner{};
    linner.AddCondition(MakeScalar<bool>(true), MakeReturnBlock(tuple_res_1),
                        std::nullopt);
    lm::Block rinner{};
    rinner.AddCondition(MakeScalar<bool>(false), MakeReturnBlock(tuple_res_1),
                        std::nullopt);
    lmi::Condition cond{MakeTaxVariable<bool>({1, 2, 3}), linner, rinner};
    ASSERT_FALSE(cond.Link(ctx.link_context).expression.has_value());
    ASSERT_EQ(
        cond.Link(ctx.link_context).expression_factory(tuple_res_2).Serialize(),
        "T(TX(1,2,3),NT(res=1.000000),NT(res=2.000000))");
    ASSERT_EQ(cond.GetType(), tuple_res_1.GetType());
  }
}

TEST_F(Instructions, Assertion) {
  Context ctx{};
  lmi::Assertion assert_f{MakeScalar<bool>(false), boost::none};
  lmi::Assertion assert_f_msg{MakeScalar<bool>(false),
                              boost::make_optional<std::string>("message")};
  lmi::Assertion assert_t{MakeScalar<bool>(true), boost::none};
  lmi::Assertion assert_t_msg{
      MakeScalar<bool>(true),
      boost::make_optional<std::string>("some message")};
  lmi::Assertion assert_double{MakeScalar<double>(1), boost::none};
  lmi::Assertion assert_double_msg{
      MakeScalar<double>(1), boost::make_optional<std::string>("message")};

  ASSERT_EQ(assert_t.CalculateFix(ctx.calc_context), std::nullopt);
  ASSERT_EQ(assert_t_msg.CalculateFix(ctx.calc_context), std::nullopt);
  ASSERT_THROW(assert_f.CalculateFix(ctx.calc_context), parser::AssertionError);
  ASSERT_THROW(assert_f_msg.CalculateFix(ctx.calc_context),
               parser::AssertionError);
  ASSERT_THROW(assert_double.CalculateFix(ctx.calc_context), std::domain_error);
  ASSERT_THROW(assert_double_msg.CalculateFix(ctx.calc_context),
               std::domain_error);

  /* run with disabled debug */
  ASSERT_EQ(assert_t.CalculateFix(ctx.calc_prod_context), std::nullopt);
  ASSERT_EQ(assert_f.CalculateFix(ctx.calc_prod_context), std::nullopt);
  ASSERT_EQ(assert_double.CalculateFix(ctx.calc_prod_context), std::nullopt);

  ASSERT_FALSE(assert_t.Link(ctx.link_context));
  ASSERT_FALSE(assert_f.Link(ctx.link_context));
  ASSERT_FALSE(assert_double.Link(ctx.link_context));

  ASSERT_EQ(assert_t.Serialize(), "ASSERT(true)");
  ASSERT_EQ(assert_t_msg.Serialize(), "ASSERT(true,\"some message\")");
  ASSERT_EQ(assert_f.Serialize(), "ASSERT(false)");
  ASSERT_EQ(assert_f_msg.Serialize(), "ASSERT(false,\"message\")");
  ASSERT_EQ(assert_double_msg.Serialize(), "ASSERT(1.000000,\"message\")");
  ASSERT_EQ(assert_double.Serialize(), "ASSERT(1.000000)");

  ASSERT_EQ(assert_t.GetType(), std::nullopt);
}

TEST_F(Instructions, Assumption) {
  Context ctx{};
  lmi::Assumption assumption{MakeScalar<double>(42)};
  ASSERT_EQ(assumption.CalculateFix(ctx.calc_context), std::nullopt);
  ASSERT_FALSE(assumption.Link(ctx.link_context));
  ASSERT_EQ(assumption.Serialize(), "ASSUME(42.000000)");
}
