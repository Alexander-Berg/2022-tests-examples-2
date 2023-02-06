#include <gtest/gtest.h>

#include <fstream>

#include <boost/iterator_adaptors.hpp>

#include <interpreter/interpreter.hpp>
#include <pricing-functions/lang/dynamic_context.hpp>
#include <pricing-functions/lang/models/block.hpp>
#include <pricing-functions/lang/models/calc_context.hpp>
#include <pricing-functions/lang/models/expression.hpp>
#include <pricing-functions/lang/models/expressions/binary_operation.hpp>
#include <pricing-functions/lang/models/expressions/concat.hpp>
#include <pricing-functions/lang/models/expressions/field_access.hpp>
#include <pricing-functions/lang/models/expressions/fold_left.hpp>
#include <pricing-functions/lang/models/expressions/function_call.hpp>
#include <pricing-functions/lang/models/expressions/linked_map.hpp>
#include <pricing-functions/lang/models/expressions/map.hpp>
#include <pricing-functions/lang/models/expressions/optional.hpp>
#include <pricing-functions/lang/models/expressions/scalar.hpp>
#include <pricing-functions/lang/models/expressions/ternary.hpp>
#include <pricing-functions/lang/models/expressions/tuple.hpp>
#include <pricing-functions/lang/models/expressions/unary_operation.hpp>
#include <pricing-functions/lang/models/expressions/value_or.hpp>
#include <pricing-functions/lang/models/features.hpp>
#include <pricing-functions/lang/models/function.hpp>
#include <pricing-functions/lang/models/instructions/return.hpp>
#include <pricing-functions/lang/models/link_context.hpp>
#include <pricing-functions/lang/models/program.hpp>
#include <pricing-functions/lang/models/scalars/taximeter_variable.hpp>
#include <pricing-functions/lang/models/scalars/value.hpp>
#include <pricing-functions/lang/models/type.hpp>
#include <pricing-functions/lang/models/types/binded_struct.hpp>
#include <pricing-functions/lang/models/types/named_tuple.hpp>
#include <pricing-functions/lang/models/types/optional.hpp>
#include <pricing-functions/lang/models/types/primitive_type.hpp>
#include <pricing-functions/lang/trip_details.hpp>
#include <userver/utest/utest.hpp>

namespace {
namespace lm = lang::models;
namespace lme = lang::models::expressions;

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
lm::Type MakePrimitiveType() {
  return lm::Type{lm::types::PrimitiveType{typeid(T)}};
}

lm::Type MakeNamedTupleType(std::unordered_map<std::string, lm::Type>&& types) {
  std::vector<lm::types::ValueField> args;
  std::vector<lm::Identifier> arg_names{};
  std::transform(
      types.begin(), types.end(), std::back_inserter(arg_names),
      [](const auto& kv) { return lm::CreateGlobalIdentifier(kv.first); });
  std::sort(arg_names.begin(), arg_names.end());
  size_t id = 0;
  for (const auto& arg_name : arg_names) {
    args.emplace_back(lm::types::ValueField{
        arg_name, id++, std::move(types[arg_name.GetName()]),
        lm::Feature::kNone});
  }

  return lm::Type{lm::types::NamedTuple{std::move(args)}};
}

template <typename T>
lm::Expression MakeScalar(T&& value) {
  return lm::Expression{std::make_shared<lme::Scalar>(
      lm::Scalar{lm::scalars::Value<T>{std::move(value)}})};
}

template <typename T>
lm::Expression MakeOptScalar(std::optional<T>&& value) {
  std::optional<lm::Expression> inner_value =
      (value)
          ? std::make_optional<lm::Expression>(MakeScalar(std::move(*value)))
          : std::nullopt;
  return lm::Expression{std::make_shared<lme::Optional>(
      MakePrimitiveType<T>().MakeOptional(), inner_value, false)};
}

template <typename T>
lm::Expression MakeVariable(const std::string& name) {
  lm::scalars::Variable variable{lm::CreateGlobalIdentifier(name),
                                 MakePrimitiveType<T>()};
  lm::Scalar scalar{variable};
  return lm::Expression{std::make_shared<lme::Scalar>(scalar)};
}

template <typename T>
lm::Expression MakeTaxVariable(const std::vector<size_t>& path) {
  lm::scalars::TaximeterVariable tax_variable{
      lm::Type{lm::types::PrimitiveType{typeid(T)}}, path};
  lm::Scalar scalar{tax_variable};
  return lm::Expression{std::make_shared<lme::Scalar>(scalar)};
}

lm::Expression MakeTernary(const lm::Expression& cond,
                           const lm::Expression& if_true,
                           const lm::Expression& if_false) {
  return lm::Expression{
      std::make_shared<lme::Ternary>(cond, if_true, if_false)};
}

lm::Expression MakeTuple(std::map<std::string, lm::Expression>&& data) {
  return lm::Expression{
      std::make_shared<lme::Tuple>(WrapContainerIdentifiers(std::move(data)))};
}

lm::Expression MakeLinkedMap(
    std::unordered_map<std::string, lm::Expression>&& data) {
  return lm::Expression{std::make_shared<lme::LinkedMap>(std::move(data))};
}

lm::Expression MakeMap(
    std::vector<std::pair<lm::Expression, lm::Expression>>&& data) {
  return lm::Expression{std::make_shared<lme::Map>(std::move(data))};
}

lm::Block MakeReturnBlock(const lm::Expression& expr) {
  lm::Block result;
  result.AddReturn(expr);
  return result;
}

lang::models::Function MakeFunction(
    const std::string& name, std::unordered_map<std::string, lm::Type>&& args,
    const lm::Block& body) {
  return {lm::CreateGlobalIdentifier(name),
          WrapContainerIdentifiers(std::move(args)), body};
}

template <typename RT>
lm::Expression MakeFunctionCall(const std::string& function_name,
                                const lm::Type& result_type,
                                std::map<std::string, lm::Expression>&& args) {
  return lm::Expression::MakeFunctionCall(
      function_name, result_type, WrapContainerIdentifiers(std::move(args)));
}

lm::Expression MakeFoldLeft(const lm::Expression& container,
                            const std::string& var_name,
                            const lm::Expression& fold_expr,
                            const lm::Expression& initial) {
  return lm::Expression{std::make_shared<lme::FoldLeft>(
      container, lm::CreateGlobalIdentifier(var_name), fold_expr, initial)};
}

template <typename T>
lm::Expression MakeSet(const std::unordered_set<T>& data) {
  return lm::Expression{
      std::make_shared<lme::Scalar>(lm::Scalar{std::cref(data)})};
}

struct Context {
  lang::models::Program ast{};
  lang::models::FeaturesSet features = lang::models::ListLatestFeatures();
  std::unique_ptr<lang::models::CalcContext> calc_context;
  lang::models::LinkContext link_context{ast, features, {}};
  price_calc::models::BinaryData bytecode{};
  lang::models::GlobalCompilationContext compilation_context{};
  price_calc::utils::OutputCodeStream os{bytecode, compilation_context};

  Context() { RecreateCalcContext(); }

  void RecreateCalcContext() {
    ast.SetMaxIdentifier(lang::models::GlobalIdentifierOffset() + 1);
    calc_context =
        std::make_unique<lang::models::CalcContext>(ast, features, false);
  }
};

template <class T>
bool OneOf(const T& testValue, const T& option1, const T& option2) {
  return (testValue == option1 || testValue == option2);
}

}  // namespace

UTEST(Scalars, ValueOrBaseTest) {
  namespace lme = lm::expressions;
  namespace lm = lang::models;
  auto double_a = MakeScalar<double>(1);
  auto double_b = MakeScalar<double>(2);
  auto bool_c = MakeScalar<bool>(true);
  lm::Expression double_a_opt{std::make_shared<lme::Optional>(
      double_a.GetType().MakeOptional(),
      std::optional<lm::Expression>{double_a}, false)};
  lm::Expression double_nullopt{std::make_shared<lme::Optional>(
      double_a.GetType().MakeOptional(), std::nullopt, false)};
  lme::ValueOr value_or{double_a_opt, double_b};
  lme::ValueOr value_or_nullopt{double_nullopt, double_b};
  Context context;

  /* Invalid initialization args */
  ASSERT_THROW(lme::ValueOr(double_a, double_b), std::domain_error);
  ASSERT_THROW(lme::ValueOr(double_a_opt, bool_c), std::domain_error);

  /* basic ops */
  ASSERT_EQ(value_or.CalculateFix(*context.calc_context), double_a.GetValue());
  ASSERT_EQ(value_or_nullopt.CalculateFix(*context.calc_context),
            double_b.GetValue());
  ASSERT_EQ(value_or.Link(context.link_context), double_a);
  /* TODO: is this the correct behavior?  */
  ASSERT_THROW(value_or_nullopt.Link(context.link_context), std::logic_error);
  ASSERT_EQ(value_or_nullopt.CalculateFix(*context.calc_context),
            double_b.GetValue());
  ASSERT_EQ(value_or.Serialize(), "VO(1.000000,2.000000)");
  ASSERT_EQ(value_or_nullopt.Serialize(),
            "VO(NULL(std::optional<double>),2.000000)");
  ASSERT_THROW(value_or.Compile(context.os), std::logic_error);

  /* Test comparison operators */
  ASSERT_EQ(value_or, value_or);
  ASSERT_EQ(value_or_nullopt, value_or_nullopt);
  ASSERT_FALSE(value_or_nullopt == value_or);
}

UTEST(Scalars, UnaryOperationComparasion) {
  auto m_one = MakeScalar<double>(1).UnaryLeft("-");
  auto m_one_too = MakeScalar<double>(1).UnaryLeft("-");
  auto m_two = MakeScalar<double>(2).UnaryLeft("-");
  auto check_one = MakeScalar<double>(2).UnaryLeft("?");
  ASSERT_EQ(m_one, m_one_too);
  ASSERT_FALSE(m_one == m_two);
  ASSERT_FALSE(m_one == check_one);
}

UTEST(Scalars, TernaryBasicOps) {
  Context ctx{};
  const auto cond = MakeScalar<bool>(true);
  const auto a = MakeScalar<double>(42);
  const auto b = MakeScalar<double>(24);
  const auto tax_dep_cond =
      MakeTaxVariable<double>({1, 0}).Binary(">", MakeScalar<double>(0));
  const auto tax_dep_cond2 =
      MakeTaxVariable<double>({1, 1}).Binary(">", MakeScalar<double>(0));
  ASSERT_THROW(
      lm::Expression(std::make_shared<lme::Ternary>(
          MakeScalar<double>(1), MakeScalar<double>(2), MakeScalar<double>(3))),
      std::invalid_argument);
  ASSERT_EQ(MakeTernary(cond.UnaryLeft("!"), a, b)
                .CalculateFix(*ctx.calc_context)
                .Serialize(),
            "24.000000");
  ASSERT_EQ(MakeTernary(cond, a, b).CalculateFix(*ctx.calc_context).Serialize(),
            "42.000000");
  ASSERT_EQ(MakeTernary(cond, MakeTuple({}), MakeTuple({}))
                .Link(ctx.link_context)
                .Serialize(),
            "NT()");

  /* Ternary with bools optimization */
  /* c ? true : false -> c */
  ASSERT_EQ(
      MakeTernary(tax_dep_cond, MakeScalar<bool>(true), MakeScalar<bool>(false))
          .Link(ctx.link_context)
          .Serialize(),
      "B(TX(1,0),>,0.000000)");
  /* c ? false : true -> !c */
  ASSERT_EQ(
      MakeTernary(tax_dep_cond, MakeScalar<bool>(false), MakeScalar<bool>(true))
          .Link(ctx.link_context)
          .Serialize(),
      "U(!,B(TX(1,0),>,0.000000))");
  /* c ? x : true -> !c || x*/
  ASSERT_EQ(MakeTernary(tax_dep_cond, tax_dep_cond2, MakeScalar<bool>(true))
                .Link(ctx.link_context)
                .Serialize(),
            "B(U(!,B(TX(1,0),>,0.000000)),||,B(TX(1,1),>,0.000000))");
  /* c ? x : false -> c && x */
  ASSERT_EQ(MakeTernary(tax_dep_cond, tax_dep_cond2, MakeScalar<bool>(false))
                .Link(ctx.link_context)
                .Serialize(),
            "B(B(TX(1,0),>,0.000000),&&,B(TX(1,1),>,0.000000))");

  /* Ternary with linked maps */
  /* c ? [] : [] -> [] */
  ASSERT_EQ(MakeTernary(tax_dep_cond, MakeLinkedMap({}), MakeLinkedMap({}))
                .Link(ctx.link_context)
                .Serialize(),
            "MAP()");
  /* c ? ["x":1] : ["x":1,"y":2] -> ["x":1, "y": (c ? null : 2)] */
  ASSERT_EQ(
      MakeTernary(tax_dep_cond, MakeLinkedMap({{"x", MakeScalar<double>(1)}}),
                  MakeLinkedMap({{"x", MakeScalar<double>(1)},
                                 {"y", MakeScalar<double>(2)}}))
          .Link(ctx.link_context)
          .Serialize(),
      "MAP(\"x\"=1.000000,\"y\"=T(B(TX(1,0),>,0.000000),NULL(std::optional<"
      "double>),2.000000))");
  /* c ? ["x":1,"y":2] : ["x":1] -> ["x":1, "y": (c ? 2 : null)] */
  ASSERT_EQ(MakeTernary(tax_dep_cond,
                        MakeLinkedMap({{"x", MakeScalar<double>(1)},
                                       {"y", MakeScalar<double>(2)}}),
                        MakeLinkedMap({{"x", MakeScalar<double>(1)}}))
                .Link(ctx.link_context)
                .Serialize(),
            "MAP(\"x\"=1.000000,\"y\"=T(B(TX(1,0),>,0.000000),2.000000,NULL("
            "std::optional<double>)))");
  /* c ? ["x":1] : ["x":2] -> ["x":(c?1:2)] */
  ASSERT_EQ(
      MakeTernary(tax_dep_cond, MakeLinkedMap({{"x", MakeScalar<double>(1)}}),
                  MakeLinkedMap({{"x", MakeScalar<double>(2)}}))
          .Link(ctx.link_context)
          .Serialize(),
      "MAP(\"x\"=T(B(TX(1,0),>,0.000000),1.000000,2.000000))");

  /* Initialization check */
  auto opt_a = a.MakeOptional(a.GetType(), a);
  auto opt_b = b.MakeOptional(b.GetType(), b);
  auto nullopt_v = a.MakeOptional(a.GetType());

  /* ?(c ? opt<x> : opt<y>) -> c?(?opt<x>):(?opt<y>) */
  /* TODO: it looks like in some cases we can drop the ternary operator */
  ASSERT_EQ(MakeTernary(tax_dep_cond, opt_a, opt_b).IsInitialized().Serialize(),
            "T(B(TX(1,0),>,0.000000),true,true)");
  ASSERT_EQ(
      MakeTernary(tax_dep_cond, opt_a, nullopt_v).IsInitialized().Serialize(),
      "T(B(TX(1,0),>,0.000000),true,false)");
  ASSERT_EQ(MakeTernary(tax_dep_cond, nullopt_v, nullopt_v)
                .IsInitialized()
                .Serialize(),
            "T(B(TX(1,0),>,0.000000),false,false)");
}

UTEST(Scalars, OptionalBasicOps) {
  Context ctx{};

  auto x = MakeScalar<double>(42);
  auto opt_x = x.MakeOptional(x.GetType(), x);
  auto nullopt_x = x.MakeOptional(x.GetType());
  ASSERT_EQ(opt_x.CalculateFix(*ctx.calc_context).Serialize(), "42.000000");
  ASSERT_THROW(nullopt_x.CalculateFix(*ctx.calc_context).Serialize(),
               std::invalid_argument);
  ASSERT_EQ(opt_x.Link(ctx.link_context).Serialize(), "42.000000");
  ASSERT_EQ(nullopt_x.Link(ctx.link_context).Serialize(),
            "NULL(std::optional<double>)");
  ASSERT_EQ(opt_x.Serialize(), "42.000000");
  ASSERT_EQ(nullopt_x.Serialize(), "NULL(std::optional<double>)");
  ASSERT_EQ(opt_x.Dereference().Serialize(), "42.000000");
  ASSERT_THROW(nullopt_x.Dereference().Serialize(), std::invalid_argument);
}

UTEST(Scalars, MapBasicOps) {
  Context ctx{};
  auto empty_map = MakeMap({});
  auto ok_map = MakeMap(
      {{MakeScalar<std::string>("a").Binary("+", MakeScalar<std::string>("b")),
        MakeScalar<double>(42)},
       {MakeScalar<std::string>("c"), MakeScalar<double>(24)}});
  auto ok_map_changed_value = MakeMap(
      {{MakeScalar<std::string>("a").Binary("+", MakeScalar<std::string>("b")),
        MakeScalar<double>(42)},
       {MakeScalar<std::string>("c"), MakeScalar<double>(244)}});
  auto map_invliad_key_type =
      MakeMap({{MakeScalar<bool>(true), MakeScalar<double>(42)}});
  auto map_invliad_value_type =
      MakeMap({{MakeScalar<std::string>("a"), MakeScalar<bool>(false)}});

  ASSERT_THROW(ctx.os << empty_map, std::logic_error);

  ASSERT_EQ(empty_map.Link(ctx.link_context).Serialize(), "MAP()");
  ASSERT_EQ(ok_map.Link(ctx.link_context).Serialize(),
            "MAP(\"ab\"=42.000000,\"c\"=24.000000)");
  ASSERT_THROW(map_invliad_key_type.Link(ctx.link_context).Serialize(),
               std::domain_error);
  ASSERT_EQ(map_invliad_value_type.Link(ctx.link_context).Serialize(),
            "MAP(\"a\"=false)");

  ASSERT_PRED3(OneOf<std::string>,
               ok_map.CalculateFix(*ctx.calc_context).Serialize(),
               "MAP(\"c\"=24.000000,\"ab\"=42.000000)",
               "MAP(\"ab\"=42.000000,\"c\"=24.000000)");
  ASSERT_THROW(map_invliad_value_type.CalculateFix(*ctx.calc_context),
               std::domain_error);
  ASSERT_THROW(map_invliad_key_type.CalculateFix(*ctx.calc_context),
               std::domain_error);

  ASSERT_EQ(ok_map, ok_map);
  ASSERT_FALSE(ok_map == ok_map_changed_value);
  ASSERT_FALSE(ok_map == MakeScalar<bool>(true));
  ASSERT_FALSE(ok_map == empty_map);
}

UTEST(Scalars, LinkedMapBasicOps) {
  Context ctx{};
  auto empty_map = MakeMap({}).Link(ctx.link_context);
  auto map_a = MakeMap({{MakeScalar<std::string>("a"), MakeScalar<double>(42)}})
                   .Link(ctx.link_context);
  auto map_b = MakeMap({{MakeScalar<std::string>("a"), MakeScalar<double>(43)}})
                   .Link(ctx.link_context);
  auto map_c = MakeMap({{MakeScalar<std::string>("a"), MakeScalar<double>(42)},
                        {MakeScalar<std::string>("e"), MakeScalar<double>(1)}})
                   .Link(ctx.link_context);
  ASSERT_EQ(empty_map.CalculateFix(*ctx.calc_context).Serialize(), "MAP()");
  ASSERT_EQ(map_a.CalculateFix(*ctx.calc_context).Serialize(),
            "MAP(\"a\"=42.000000)");
  ASSERT_THROW(ctx.os << map_a, std::logic_error);
  ASSERT_EQ(map_a, map_a);
  ASSERT_FALSE(map_a == map_b);
  ASSERT_FALSE(map_a == map_c);
}

UTEST(Scalars, FunctionCallBasicOps) {
  Context ctx{};

  auto fun_return_type =
      MakeNamedTupleType({{"res", MakePrimitiveType<double>()}});
  auto fc_a = MakeFunctionCall<double>("testf", fun_return_type, {});
  auto fc_b = MakeFunctionCall<double>("testf", fun_return_type,
                                       {{"x", MakeScalar<double>(42)}});
  auto fc_c = MakeFunctionCall<double>("other_f", fun_return_type,
                                       {{"x", MakeScalar<double>(42)}});
  auto fc_d = MakeFunctionCall<double>("testf", fun_return_type,
                                       {{"y", MakeScalar<double>(42)}});
  auto fc_e = MakeFunctionCall<double>("testf", fun_return_type,
                                       {{"x", MakeScalar<double>(43)}});
  auto fc_f = MakeFunctionCall<double>(
      "testf", fun_return_type,
      {{"x", MakeScalar<double>(43)}, {"y", MakeScalar<double>(2)}});

  /* test_f = x -> { res=x * 2 } */
  auto fun = MakeFunction(
      "testf", {{"x", MakePrimitiveType<double>()}},
      MakeReturnBlock(MakeTuple({{"res", MakeVariable<double>("x").Binary(
                                             "*", MakeScalar<double>(2))}})));
  ctx.ast.AddFunction(fun);
  ctx.ast.SetMaxIdentifier(lang::models::GlobalIdentifierOffset() + 1);
  ctx.RecreateCalcContext();

  ASSERT_EQ(fc_b.Serialize(), "FC(testf,NT(x=42.000000),R(res=double))");
  /* TODO: why do we have additional concat operation here? */
  ASSERT_EQ(fc_b.Link(ctx.link_context).Serialize(),
            "CONCAT(NT(),NT(res=84.000000))");
  ASSERT_EQ(fc_f.Link(ctx.link_context).Serialize(),
            "CONCAT(NT(),NT(res=86.000000))");
  ASSERT_THROW(fc_d.Link(ctx.link_context).Serialize(), std::out_of_range);
  ASSERT_THROW(fc_c.Link(ctx.link_context).Serialize(), std::out_of_range);

  /* TODO: Is it ok to pass more args than the function requires? */
  ASSERT_EQ(fc_b.CalculateFix(*ctx.calc_context).Serialize(),
            "NT(res=84.000000)");
  ASSERT_EQ(fc_f.CalculateFix(*ctx.calc_context).Serialize(),
            "NT(res=86.000000)");
  ASSERT_THROW(fc_d.CalculateFix(*ctx.calc_context).Serialize(),
               std::out_of_range);
  ASSERT_THROW(fc_c.CalculateFix(*ctx.calc_context).Serialize(),
               std::out_of_range);

  ASSERT_THROW(ctx.os << fc_b, std::invalid_argument);

  ASSERT_EQ(fc_b, fc_b);
  ASSERT_FALSE(fc_b == MakeScalar<double>(42));
  ASSERT_FALSE(fc_b == fc_c);
  ASSERT_FALSE(fc_b == fc_d);
  ASSERT_FALSE(fc_c == fc_b);
  ASSERT_FALSE(fc_d == fc_b);
  ASSERT_FALSE(fc_e == fc_b);
  ASSERT_FALSE(fc_b == fc_e);

  /* FIXME: now this function calls are compared as equals or not depending on
   * the order. Seems like a bug  */
  ASSERT_FALSE(fc_b == fc_a);
  ASSERT_EQ(fc_a, fc_b);
}

UTEST(Scalars, FoldLeftBasicOps) {
  Context ctx{};
  std::unordered_set<std::string> data{"a", "b", "c"};
  auto result_tuple = MakeTuple({{"res", MakeScalar<std::string>("")}});
  auto fl = MakeFoldLeft(
      MakeSet(data), "it",
      MakeTuple({{"res", MakeVariable<std::string>("it").Binary(
                             "+", MakeVariable<std::string>("res"))}}),
      result_tuple);
  auto fl_unresolved = MakeFoldLeft(
      MakeTaxVariable<std::unordered_set<std::string>>({1, 2}), "it",
      MakeTuple({{"res", MakeVariable<std::string>("it").Binary(
                             "+", MakeVariable<std::string>("res"))}}),
      result_tuple);
  ctx.RecreateCalcContext();
  ASSERT_EQ(fl.CalculateFix(*ctx.calc_context).Serialize(), "NT(res=\"cba\")");
  ASSERT_EQ(fl.Link(ctx.link_context).Serialize(), "NT(res=\"cba\")");
  ASSERT_THROW(fl_unresolved.Link(ctx.link_context), std::invalid_argument);
  ASSERT_THROW(ctx.os << fl_unresolved, std::invalid_argument);
  ASSERT_EQ(fl, fl);
  ASSERT_FALSE(fl == MakeScalar<double>(1));
  ASSERT_FALSE(fl == fl_unresolved);
}

UTEST(Scalars, FieldAccesBasicOps) {
  Context ctx{};

  auto double_val = MakeScalar<double>(1);
  lm::Expression double_opt{std::make_shared<lme::Optional>(
      double_val.GetType().MakeOptional(),
      std::optional<lm::Expression>{double_val}, false)};

  auto source_obj =
      MakeTuple({{"some_field", MakeScalar<double>(0)}, {"y", double_opt}});

  lm::Expression field_access{std::make_shared<lme::FieldAccess>(
      source_obj,
      lm::types::ValueField{lm::CreateGlobalIdentifier("some_field"), 0,
                            MakePrimitiveType<double>(), lm::Feature::kNone})};
  ASSERT_THROW(ctx.os << field_access, std::logic_error);

  ASSERT_EQ(field_access.Serialize(),
            "B(NT(some_field=0.000000,y=1.000000),.,F(some_field))");
  ASSERT_EQ(field_access.Dereference().Serialize(), "0.000000");
  ASSERT_EQ(field_access.Link(ctx.link_context).Serialize(), "0.000000");
  ASSERT_EQ(field_access.CalculateFix(*ctx.calc_context).Serialize(),
            "0.000000");

  lm::Expression opt_obj_access{std::make_shared<lme::FieldAccess>(
      source_obj.MakeOptional(source_obj.GetType(), source_obj),
      lm::types::ValueField{lm::CreateGlobalIdentifier("some_field"), 0,
                            MakePrimitiveType<double>(), lm::Feature::kNone})};
  ASSERT_EQ(opt_obj_access.Serialize(),
            "B(NT(some_field=0.000000,y=1.000000),.,F(some_field))");
  ASSERT_EQ(opt_obj_access.Dereference().Serialize(), "0.000000");
  ASSERT_EQ(opt_obj_access.Link(ctx.link_context).Serialize(), "0.000000");
  ASSERT_EQ(opt_obj_access.CalculateFix(*ctx.calc_context).Serialize(),
            "0.000000");

  lm::Expression opt_obj_opt_field_access{std::make_shared<lme::FieldAccess>(
      source_obj.MakeOptional(source_obj.GetType(), source_obj),
      lm::types::ValueField{lm::CreateGlobalIdentifier("y"), 0,
                            MakePrimitiveType<double>().MakeOptional(),
                            lm::Feature::kNone})};
  ASSERT_EQ(opt_obj_opt_field_access.Serialize(),
            "B(NT(some_field=0.000000,y=1.000000),.,F(y))");
  ASSERT_EQ(opt_obj_opt_field_access.Dereference().Serialize(),
            "U(*,1.000000)");
  ASSERT_EQ(opt_obj_opt_field_access.Link(ctx.link_context).Serialize(),
            "1.000000");
  ASSERT_EQ(
      opt_obj_opt_field_access.CalculateFix(*ctx.calc_context).Serialize(),
      "1.000000");
}

UTEST(Scalars, ConcatMerge) {
  Context ctx{};
  const auto tuple_a = MakeTuple({{"x", MakeScalar<double>(1)}});
  const auto tuple_b =
      MakeTuple({{"x", MakeScalar<double>(2)}, {"y", MakeScalar<double>(2)}});
  const auto tuple_c =
      MakeTuple({{"complex", MakeTuple({{"v", MakeScalar<double>(1)}})}});
  const auto tuple_d = MakeTuple({{"y", MakeScalar<double>(12)}});
  const auto tuple_e =
      MakeTuple({{"complex", MakeTuple({{"f", MakeScalar<double>(22)}})}});
  const auto tuple_empty = MakeTuple({});

  const auto map_a =
      MakeScalar<std::unordered_map<std::string, double>>({{"x", 1}});
  const auto map_empty =
      MakeScalar<std::unordered_map<std::string, double>>({});
  const auto map_b =
      MakeScalar<std::unordered_map<std::string, double>>({{"x", 2}, {"y", 2}});
  const auto map_d =
      MakeScalar<std::unordered_map<std::string, double>>({{"y", 12}});

  const auto lm_a = MakeLinkedMap({{"x", MakeScalar<double>(1)}});
  const auto lm_empty = MakeLinkedMap({});
  const auto lm_b = MakeLinkedMap(
      {{"x", MakeScalar<double>(2)}, {"y", MakeScalar<double>(2)}});
  const auto lm_d = MakeLinkedMap({{"y", MakeScalar<double>(12)}});

  ASSERT_EQ(tuple_a.Concat(tuple_b).Serialize(),
            "CONCAT(NT(x=1.000000),NT(x=2.000000,y=2.000000))");

  ASSERT_EQ(tuple_a.Concat(tuple_b).CalculateFix(*ctx.calc_context).Serialize(),
            "NT(x=2.000000,y=2.000000)");
  ASSERT_EQ(tuple_a.Concat(tuple_a).CalculateFix(*ctx.calc_context).Serialize(),
            "NT(x=1.000000)");
  ASSERT_EQ(
      tuple_a.Concat(tuple_empty).CalculateFix(*ctx.calc_context).Serialize(),
      "NT(x=1.000000)");
  ASSERT_EQ(tuple_a.Concat(tuple_c).CalculateFix(*ctx.calc_context).Serialize(),
            "NT(complex=NT(v=1.000000),x=1.000000)");

  ASSERT_EQ(tuple_b.Concat(tuple_a).CalculateFix(*ctx.calc_context).Serialize(),
            "NT(x=1.000000,y=2.000000)");
  ASSERT_EQ(tuple_b.Concat(tuple_a).CalculateFix(*ctx.calc_context).Serialize(),
            "NT(x=1.000000,y=2.000000)");
  ASSERT_EQ(tuple_a.Concat(tuple_d).CalculateFix(*ctx.calc_context).Serialize(),
            "NT(x=1.000000,y=12.000000)");
  ASSERT_EQ(tuple_c.Concat(tuple_e).CalculateFix(*ctx.calc_context).Serialize(),
            "NT(complex=NT(f=22.000000,v=1.000000))");

  /* TODO: here we have unordered_maps, so order is not well-defined */
  ASSERT_PRED3(OneOf<std::string>,
               map_a.Concat(map_b).CalculateFix(*ctx.calc_context).Serialize(),
               "MAP(\"x\"=2.000000,\"y\"=2.000000)",
               "MAP(\"y\"=2.000000,\"x\"=2.000000)");
  ASSERT_PRED3(OneOf<std::string>,
               map_b.Concat(map_a).CalculateFix(*ctx.calc_context).Serialize(),
               "MAP(\"y\"=2.000000,\"x\"=1.000000)",
               "MAP(\"x\"=1.000000,\"y\"=2.000000)");
  ASSERT_EQ(map_a.Concat(map_a).CalculateFix(*ctx.calc_context).Serialize(),
            "MAP(\"x\"=1.000000)");
  ASSERT_EQ(map_a.Concat(map_empty).CalculateFix(*ctx.calc_context).Serialize(),
            "MAP(\"x\"=1.000000)");
  ASSERT_PRED3(OneOf<std::string>,
               map_a.Concat(map_d).CalculateFix(*ctx.calc_context).Serialize(),
               "MAP(\"x\"=1.000000,\"y\"=12.000000)",
               "MAP(\"y\"=12.000000,\"x\"=1.000000)");

  ASSERT_EQ(tuple_a.Concat(tuple_b).Link(ctx.link_context).Serialize(),
            "NT(x=2.000000,y=2.000000)");
  ASSERT_EQ(tuple_a.Concat(tuple_a).Link(ctx.link_context).Serialize(),
            "NT(x=1.000000)");
  ASSERT_EQ(tuple_a.Concat(tuple_empty).Link(ctx.link_context).Serialize(),
            "NT(x=1.000000)");
  ASSERT_EQ(tuple_a.Concat(tuple_c).Link(ctx.link_context).Serialize(),
            "NT(complex=NT(v=1.000000),x=1.000000)");
  ASSERT_EQ(tuple_a.Concat(tuple_d).Link(ctx.link_context).Serialize(),
            "NT(x=1.000000,y=12.000000)");

  ASSERT_EQ(lm_a.Concat(lm_b).Link(ctx.link_context).Serialize(),
            "MAP(\"x\"=2.000000,\"y\"=2.000000)");
  ASSERT_EQ(lm_a.Concat(lm_a).Link(ctx.link_context).Serialize(),
            "MAP(\"x\"=1.000000)");
  ASSERT_EQ(lm_a.Concat(lm_empty).Link(ctx.link_context).Serialize(),
            "MAP(\"x\"=1.000000)");
  ASSERT_PRED3(OneOf<std::string>,
               map_a.Concat(map_b).Link(ctx.link_context).Serialize(),
               "MAP(\"y\"=2.000000,\"x\"=2.000000)",
               "MAP(\"x\"=2.000000,\"y\"=2.000000)");

  /* simple scalars merging */
  ASSERT_EQ(MakeOptScalar<double>({})
                .Concat(MakeScalar<double>(1))
                .Link(ctx.link_context)
                .Serialize(),
            "1.000000");
  ASSERT_EQ(MakeScalar<double>(1)
                .Concat(MakeOptScalar<double>({}))
                .Link(ctx.link_context)
                .Serialize(),
            "1.000000");
  ASSERT_EQ(MakeScalar<double>(1)
                .Concat(MakeScalar<double>(2))
                .Link(ctx.link_context)
                .Serialize(),
            "2.000000");
}

void CheckBinaryOp(const lm::Expression& expr, const std::string& ast,
                   const std::string& result) {
  Context ctx{};
  ASSERT_EQ(expr.Serialize(), ast);
  ASSERT_EQ(expr.CalculateFix(*ctx.calc_context).Serialize(), result);
  ASSERT_EQ(expr.Link(ctx.link_context).Serialize(), result);
}

UTEST(Scalars, BinaryOpBasicOps) {
  /* simple scalar operations */
  CheckBinaryOp(MakeScalar<double>(2).Binary("^", MakeScalar<double>(3)),
                "B(2.000000,^,3.000000)", "8.000000");
  CheckBinaryOp(MakeScalar<double>(2).Binary("*", MakeScalar<double>(3)),
                "B(2.000000,*,3.000000)", "6.000000");
  CheckBinaryOp(MakeScalar<double>(2).Binary("/", MakeScalar<double>(3)),
                "B(2.000000,/,3.000000)", "0.666667");
  CheckBinaryOp(MakeScalar<double>(2).Binary("+", MakeScalar<double>(3)),
                "B(2.000000,+,3.000000)", "5.000000");
  CheckBinaryOp(MakeScalar<double>(2).Binary("-", MakeScalar<double>(3)),
                "B(2.000000,-,3.000000)", "-1.000000");
  CheckBinaryOp(
      MakeScalar<double>(2).Binary("round_to", MakeScalar<double>(10)),
      "B(2.000000,round_to,10.000000)", "10.000000");
  CheckBinaryOp(MakeScalar<double>(2).Binary("<=", MakeScalar<double>(3)),
                "B(2.000000,<=,3.000000)", "true");
  CheckBinaryOp(MakeScalar<double>(2).Binary(">=", MakeScalar<double>(3)),
                "B(2.000000,>=,3.000000)", "false");
  CheckBinaryOp(MakeScalar<double>(2).Binary("<", MakeScalar<double>(3)),
                "B(2.000000,<,3.000000)", "true");
  CheckBinaryOp(MakeScalar<double>(2).Binary(">", MakeScalar<double>(3)),
                "B(2.000000,>,3.000000)", "false");

  /* ride.price multiplication */
  Context ctx{};

  const auto tax_dep_cond =
      MakeTaxVariable<double>({1, 0}).Binary(">", MakeScalar<double>(0));
  const auto mult_ternary = MakeScalar<double>(3).Binary(
      "*",
      MakeTernary(tax_dep_cond, MakeScalar<double>(1), MakeScalar<double>(2)));
  ASSERT_EQ(mult_ternary.Link(ctx.link_context).Serialize(),
            "T(B(TX(1,0),>,0.000000),3.000000,6.000000)");
}

UTEST(Scalars, GenericScalarDoubleOps) {
  Context ctx{};
  lm::Scalar scalar{lm::scalars::Value<double>{42}};

  ASSERT_TRUE(scalar.IsResolved());
  ASSERT_EQ(scalar.GetType(), lm::Type{typeid(double)});
  ASSERT_FALSE(scalar.IsTaximeterVariable());
  ASSERT_THROW(scalar.GetTaximeterPath(), std::domain_error);
  ASSERT_THROW(scalar.Enumerate(), std::domain_error);
  ASSERT_THROW(scalar.ListFields(), std::domain_error);
  ASSERT_THROW(scalar.GetField(lm::CreateGlobalIdentifier("x")),
               std::domain_error);
  ASSERT_THROW(scalar.ExtractField(lm::CreateGlobalIdentifier("x")),
               std::domain_error);
  ASSERT_EQ(scalar.Serialize(), "42.000000");
  ASSERT_EQ(scalar.Link(ctx.link_context).Serialize(), "42.000000");
  ASSERT_EQ(scalar.CalculateFix(*ctx.calc_context).Serialize(), "42.000000");
  ASSERT_NE(scalar, lm::Scalar{lm::scalars::Value<double>{43}});
  ASSERT_EQ(scalar.GetReference().GetType(), lm::Type{typeid(double&)});
}

UTEST(Scalars, UnresolvedScalarGetReference) {
  lm::scalars::TaximeterVariable tax_variable{
      lm::Type{lm::types::PrimitiveType{typeid(double)}}, {1, 2}};
  lm::Scalar scalar{tax_variable};
  ASSERT_EQ(scalar.GetReference(), scalar);
}

UTEST(Scalars, ProgramDoubleFunctionInsert) {
  Context ctx{};

  /* test_f = x -> { res=x * 2 } */
  auto fun = MakeFunction(
      "testf", {{"x", MakePrimitiveType<double>()}},
      MakeReturnBlock(MakeTuple({{"res", MakeVariable<double>("x").Binary(
                                             "*", MakeScalar<double>(2))}})));

  ctx.ast.AddFunction(fun);
  ASSERT_THROW(ctx.ast.AddFunction(fun), std::invalid_argument);
}

UTEST(Scalars, ProgramNoReturn) {
  Context ctx;
  lm::Block empty_block{};
  ctx.ast.SetBody(empty_block);
  lang::variables::BackendVariables bv{};
  lang::variables::TripDetails trip{};
  lang::variables::DynamicContext dynamic{{}, price_calc::models::Price()};
  lm::FeaturesSet feature_set{};

  lang::models::GlobalLinkContext link_context{};
  ASSERT_THROW(ctx.ast.CalculateFix(bv, trip, dynamic, feature_set, {}),
               std::logic_error);
  ASSERT_THROW(ctx.ast.Link(bv, std::nullopt, feature_set, link_context),
               std::logic_error);
}

UTEST(Scalars, FunctionBasicOps) {
  Context ctx{};
  auto fun = MakeFunction(
      "testf", {{"x", MakePrimitiveType<double>()}},
      MakeReturnBlock(MakeTuple({{"res", MakeVariable<double>("x").Binary(
                                             "*", MakeScalar<double>(2))}})));

  auto no_ret_fun =
      MakeFunction("testf_noret", {{"x", MakePrimitiveType<double>()}}, {});

  ASSERT_EQ(fun({{lm::CreateGlobalIdentifier("x"), MakeScalar<double>(3)}})
                .Serialize(),
            "FC(testf,NT(x=3.000000),R(res=double))");
  ASSERT_THROW(fun({}), std::invalid_argument);
  ASSERT_THROW(fun({{lm::CreateGlobalIdentifier("x"), MakeScalar<bool>(true)}}),
               std::invalid_argument);
  ASSERT_THROW(fun({{lm::CreateGlobalIdentifier("y"), MakeScalar<bool>(true)}}),
               std::invalid_argument);
  ASSERT_THROW(
      no_ret_fun({{lm::CreateGlobalIdentifier("x"), MakeScalar<double>(3)}}),
      std::logic_error);
  ASSERT_THROW(no_ret_fun.CalculateFix(*ctx.calc_context), std::logic_error);
  ASSERT_THROW(no_ret_fun.Link(ctx.link_context), std::logic_error);
}

UTEST(Scalars, GenericExpressionIvalidUsages) {
  lm::Expression double_ = MakeScalar<double>(5);
  lm::Expression sum_ = MakeScalar<double>(5) + MakeScalar<double>(3);
  lm::Expression empty_expr{};
  ASSERT_THROW(double_.GetLinkedMap(), std::domain_error);
  ASSERT_THROW(double_.GetMap(), std::domain_error);
  ASSERT_THROW(sum_.GetValue(), std::domain_error);
  ASSERT_THROW(double_.GetTernary(), std::invalid_argument);
  ASSERT_FALSE(double_.IsMap());
  ASSERT_EQ(empty_expr.GetSourceCodeLocationInfo(), std::nullopt);
}

UTEST(Scalars, GenericExpressionBasicOps) {
  ASSERT_EQ((MakeScalar<double>(3) + MakeScalar<double>(2)).Serialize(),
            "B(3.000000,+,2.000000)");
  ASSERT_EQ((MakeScalar<double>(3) * MakeScalar<double>(2)).Serialize(),
            "B(3.000000,*,2.000000)");
  ASSERT_EQ((MakeScalar<double>(3) / MakeScalar<double>(2)).Serialize(),
            "B(3.000000,/,2.000000)");
  ASSERT_EQ((MakeScalar<bool>(true) && MakeScalar<bool>(false)).Serialize(),
            "B(true,&&,false)");
  ASSERT_EQ(MakeScalar<double>(3).ValueOr(MakeScalar<double>(2)),
            MakeScalar<double>(3));
  ASSERT_EQ(MakeScalar<double>(3)
                .LegacyFoldLeft(lm::CreateGlobalIdentifier("it"),
                                MakeScalar<double>(1), {})
                .Serialize(),
            "FL(3.000000,it,NT(),1.000000)");
}

UTEST(Scalars, InvalidOperation) {
  ASSERT_THROW(MakeScalar<double>(3).UnaryLeft("!"), std::out_of_range);
  ASSERT_THROW(MakeScalar<bool>(false).Binary("*", MakeScalar<bool>(true)),
               std::out_of_range);
}
