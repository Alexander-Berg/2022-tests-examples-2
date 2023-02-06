#include <gtest/gtest.h>

#include <fstream>
#include <interpreter/interpreter.hpp>
#include <pricing-functions/lang/models/block.hpp>
#include <pricing-functions/lang/models/calc_context.hpp>
#include <pricing-functions/lang/models/expressions/scalar.hpp>
#include <pricing-functions/lang/models/link_context.hpp>
#include <pricing-functions/lang/models/program.hpp>
#include <pricing-functions/lang/models/types/primitive_type.hpp>
#include <pricing-functions/lang/trip_details.hpp>
#include <userver/utest/utest.hpp>

UTEST(Scalars, TypedScalarTypeCheck) {
  namespace lm = lang::models;
  lm::Scalar scalar{std::string{"test"}};
  ASSERT_THROW(scalar.Get<bool>(), std::domain_error);
}

UTEST(Scalars, UnresolvedScalarCheck) {
  namespace lm = lang::models;
  lm::scalars::Variable var_scalar{lm::CreateGlobalIdentifier("some_var"),
                                   lm::Type{typeid(int)},
                                   lm::scalars::VariableType::kVariable};
  lm::Scalar scalar{var_scalar};
  price_calc::models::BinaryData result;
  lang::models::GlobalCompilationContext compilation_context{};
  price_calc::utils::OutputCodeStream os(result, compilation_context);
  ASSERT_THROW(scalar.Get<int>(), std::domain_error);
  ASSERT_THROW(scalar.GetTaximeterPath(), std::domain_error);
  ASSERT_THROW(os << scalar, std::domain_error);
  ASSERT_THROW(var_scalar.GetReference(), std::domain_error);
}

UTEST(Scalars, ContextComparasion) {
  namespace lm = lang::models;
  lm::Scalar ctxl{lm::Context<lang::variables::BackendVariables>()};
  lm::Scalar ctxr{lm::Context<lang::variables::BackendVariables>()};
  ASSERT_EQ(ctxl, ctxr);
  ASSERT_FALSE(ctxl.IsResolved());
}

UTEST(Scalars, TupleComparasion) {
  namespace lm = lang::models;
  lm::Identifier id1 = lm::CreateGlobalIdentifier("id1");
  lm::Identifier id2 = lm::CreateGlobalIdentifier("id2");
  std::map<lm::Identifier, lm::Scalar> original_map{
      {id1, lm::Scalar{std::string{"test"}}},
      {id2, lm::Scalar{std::string{"test2"}}}};
  std::map<lm::Identifier, lm::Scalar> map_no_el{
      {id1, lm::Scalar{std::string{"test"}}}};
  std::map<lm::Identifier, lm::Scalar> map_el_diff{
      {id1, lm::Scalar{std::string{"test"}}},
      {id2, lm::Scalar{std::string{"test3"}}}};
  std::map<lm::Identifier, lm::Scalar> map_diff_types{
      {id1, lm::Scalar{std::string{"test"}}}, {id2, lm::Scalar{42}}};
  lm::Scalar str_scalar{};
  auto original_map_copy = original_map;
  lm::Scalar original{std::move(original_map)};
  lm::Scalar no_el{std::move(map_no_el)};
  lm::Scalar copy{std::move(original_map_copy)};
  lm::Scalar el_diff{std::move(map_el_diff)};
  lm::Scalar diff_types{std::move(map_diff_types)};
  ASSERT_EQ(original, copy);
  ASSERT_NE(original, no_el);
  ASSERT_NE(original, el_diff);
  ASSERT_NE(original, str_scalar);
  ASSERT_NE(original, diff_types);
  ASSERT_EQ(original.GetField(id1), lm::Scalar{std::string{"test"}});
  ASSERT_TRUE(original.IsResolved());
}

UTEST(Scalars, ValueMethods) {
  namespace lm = lang::models;
  price_calc::models::BinaryData result;
  lang::models::GlobalCompilationContext compilation_context{};
  price_calc::utils::OutputCodeStream os(result, compilation_context);
  lm::scalars::Value<bool> scalar{true};
  lm::Program ast{};
  const auto features = lang::models::ListLatestFeatures();
  lm::LinkContext link_context{ast, features, {}};
  lm::CalcContext calc_context{ast, features, false};
  ASSERT_TRUE(scalar.IsResolved());
  ASSERT_EQ(scalar.Serialize(), "true");
  ASSERT_THROW(scalar.Compile(os), std::domain_error);
  ASSERT_THROW(scalar.Link(link_context), std::domain_error);
  ASSERT_THROW(scalar.CalculateFix(calc_context), std::domain_error);
  ASSERT_EQ(scalar.Get<bool>(), true);
}

UTEST(Scalars, TaximeterVariableComp) {
  namespace lm = lang::models;
  lm::scalars::TaximeterVariable variable{
      lm::Type{lm::types::PrimitiveType{typeid(double)}}, {1, 2}};
  lm::scalars::TaximeterVariable variable2{
      lm::Type{lm::types::PrimitiveType{typeid(double)}}, {2, 1}};
  lm::scalars::TaximeterVariable variable3{
      lm::Type{lm::types::PrimitiveType{typeid(bool)}}, {2, 1}};
  lm::scalars::TaximeterVariable variable4{
      lm::Type{lm::types::PrimitiveType{typeid(double)}}, {}};
  lm::scalars::TaximeterVariable bool_val{
      lm::Type{lm::types::PrimitiveType{typeid(double)}}, {}};
  ASSERT_EQ(variable, variable);
  ASSERT_FALSE(variable == variable2);
  ASSERT_FALSE(variable == variable3);
  ASSERT_FALSE(variable == variable4);
  ASSERT_FALSE(variable == bool_val);
}
