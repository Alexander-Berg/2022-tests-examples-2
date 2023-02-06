#include <gtest/gtest.h>

#include <boost/filesystem.hpp>
#include <fstream>
#include <functional>
#include <interpreter/interpreter.hpp>
#include <pricing-functions/helpers/bv_optional_parse.hpp>
#include <pricing-functions/lang/models/link_context.hpp>
#include <pricing-functions/lang/models/types/value_field.hpp>
#include <pricing-functions/parser/ast_parser.hpp>
#include <pricing-functions/parser/parser.hpp>
#include <tests/test_utils.hpp>
#include <userver/crypto/base64.hpp>
#include <userver/logging/log.hpp>
#include <userver/utest/utest.hpp>
#include "pricing-functions/parser/typename_maker.hpp"

using price_calc::interpreter::TripDetails;

UTEST(Compiler, RecursionDepthCheck) {
  const int depth = 13;
  parser::Parse(R"(
return (((({}))));
)",
                {}, depth);
  ASSERT_THROW(parser::Parse(R"(
  return (((((({})))))));
  )",
                             {}, depth),
               parser::ParseException);
  ASSERT_THROW(parser::Parse(R"(
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
if (true) {
return {};}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
return {};
)",
                             {}, depth),
               parser::ParseException);
  ASSERT_THROW(parser::Parse(R"(
    return {res=1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 +
  1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1
  + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 +
  1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1}
  )",
                             {}, depth),
               parser::ParseException);
}

UTEST(Compiler, Simplify) {
  const auto& ast = parser::ParseAst(
      "GENERATE(L(req,B(B(fix,.,F(requirements)),.,F(simple))),I(simple_cost="
      "0."
      "000000),C(),U(simple_cost=B(GV(simple_cost),+,T(B(GV(req),in,B(B(fix,."
      ","
      "F(tariff)),.,F(requirement_prices))),B(B(B(fix,.,F(tariff)),.,F("
      "requirement_prices)),.,GV(req)),0.000000))));GENERATE(L(req,B(B(fix,.,"
      "F("
      "requirements)),.,F(select))),I(select_cost=0.000000),C(GENERATE(L(opt,"
      "B("
      "GV(req),.,F(second))),I(options_cost=0.000000),C(),U(options_cost=B("
      "GV("
      "options_cost),+,T(B(T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,F("
      "first)),+,\".\"),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first))),in,B("
      "B("
      "fix,.,F(tariff)),.,F(requirement_prices))),B(B(B(fix,.,F(tariff)),.,F("
      "requirement_prices)),.,T(B(GV(opt),.,F(independent)),B(B(B(GV(req),.,"
      "F("
      "first)),+,\".\"),+,B(GV(opt),.,F(name))),B(GV(req),.,F(first)))),0."
      "000000))))),U(select_cost=B(GV(select_cost),+,GV(options_cost))));CR("
      "boarding=B(B(ride,.,F(price)),.,F(boarding)),distance=B(B(ride,.,F("
      "price)),.,F(distance)),time=B(B(ride,.,F(price)),.,F(time)),waiting=B("
      "B("
      "ride,.,F(price)),.,F(waiting)),requirements=B(GV(simple_cost),+,GV("
      "select_cost)),transit_waiting=B(B(ride,.,F(price)),.,F(transit_"
      "waiting))"
      ",destination_waiting=B(B(ride,.,F(price)),.,F(destination_waiting)))");
  lang::variables::BackendVariables vars{};

  vars.requirements.simple.insert("req1");
  vars.requirements.simple.insert("req2");
  vars.requirements.simple.insert("req3");
  vars.requirements.select["sr1"].push_back({"op1", false});
  vars.requirements.select["sr1"].push_back({"op1", false});
  vars.requirements.select["sr2"].push_back({"op1", true});
  vars.requirements.select["sr2"].push_back({"op2", true});
  vars.requirements.select["sr3"].push_back({"op1", true});
  vars.tariff.requirement_prices["req1"] = 2;
  vars.tariff.requirement_prices["req2"] = 7;
  vars.tariff.requirement_prices["sr1"] = 1;
  vars.tariff.requirement_prices["sr2.op1"] = 10;
  vars.tariff.requirement_prices["sr2.op2"] = 30;

  vars.discount = lang::variables::DiscountInfo{
      "id",                         // id
      std::nullopt,                 // is_cashback
      std::nullopt,                 // calc_data_coeff;
      {{0, {0, 0, 0}, {0, 0, 0}}},  // calc_data_hyperbolas;
      {{{0, 0}, {100, 100}}},       // calc_data_table_data
      {},                           // restrictions
      std::nullopt,                 // limited_rides
      std::nullopt,                 // with_restriction_by_usages
      std::nullopt,                 // description
      std::nullopt,                 // discount_class
      std::nullopt,                 // method
      std::nullopt,                 // limit_id
      std::nullopt,                 // is_price_striketheough
      std::nullopt,                 // payment_system
      std::nullopt                  // competitors
  };

  TripDetails trip_details(1, std::chrono::seconds(2), std::chrono::seconds(3),
                           std::chrono::seconds(0), std::chrono::seconds(0), {},
                           {});

  for (size_t i = 0; i < 10000; ++i) {
    lang::variables::TripDetails trip = {
        1,  // distance
        2   // time
    };
    const auto& features = lang::models::ListLatestFeatures();
    lang::models::GlobalLinkContext link_context{};
    const auto simplified_ast =
        ast.Link(vars, std::nullopt, features, link_context);
    const auto simplified_ast_fix =
        ast.Link(vars, trip, features, link_context);

    lang::models::GlobalCompilationContext compilation_context{};
    EXPECT_EQ(simplified_ast.Serialize(),
              "CR(boarding=TX(1,0),destination_waiting=TX(1,6),distance=TX(1,1)"
              ",metadata=MAP(),requirements=51.000000,time=TX(1,2),transit_"
              "waiting=TX(1,5),waiting=TX(1,3))");  // test simplifier
    simplified_ast.Compile({}, {true /* drop_empty_return */},
                           compilation_context);

    EXPECT_EQ(simplified_ast_fix.Serialize(),
              "CR(boarding=TX(1,0),destination_waiting=TX(1,6),distance=TX(1,1)"
              ",metadata=MAP(),requirements=51.000000,time=TX(1,2),transit_"
              "waiting=TX(1,5),waiting=TX(1,3))");  // test simplifier
    simplified_ast_fix.Compile({}, {true /* drop_empty_return */},
                               compilation_context);
  }
}

UTEST(Compiler, CalculateFix) {
  const auto& ast = parser::Parse(
      R"(
if (fix.editable_requirements as editable_requirements) {
  with (sum_cost = 0, meta=[]) generate(req : editable_requirements)
    let req_name = req.first;
    let req_price = (req_name in fix.tariff.requirement_prices) ? fix.tariff.requirement_prices[req_name] : 0;
    let count_inp = (req_name in ride.ride.user_options) ? ride.ride.user_options[req_name] : 0;
    let req_info = req.second;
    let count_intermediate = (req_info.min_value as min_value)
                                 ? ((count_inp < min_value) ? min_value : count_inp)
                                 : count_inp;
    let count_final = (req_info.max_value as max_value)
                          ? ((count_intermediate > max_value) ? max_value : count_intermediate)
                          : count_intermediate;
    let req_cost = count_final * req_price;
    let cmeta = (req_name in fix.tariff.requirement_prices) ? [
      "req:" + req_name + ":count": count_final,
      "req:" + req_name + ":per_unit": round_to(req_price, fix.rounding_factor),
      "req:" + req_name + ":price": round_to(req_cost, fix.rounding_factor)
    ] : [];
  endgenerate(sum_cost = sum_cost + req_cost, meta = meta + cmeta)
  return {
    requirements = ride.price.requirements + sum_cost,
    metadata = meta
  };
}
return ride.price;
    )",
      {});
  lang::variables::BackendVariables vars =
      formats::parse::ParseBackendVariablesOptional(
          formats::json::FromString(R"(
{
  "editable_requirements": {
    "fake_middle_point_cargocorp_van.no_loaders_point": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "fake_middle_point_cargocorp_lcv_m.one_loader_point": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "discrete_overweight.small": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "fake_middle_point_cargocorp_lcv_m.no_loaders_point": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "fake_middle_point_cargocorp_lcv_l.one_loader_point": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "fake_middle_point_cargocorp_lcv_l.no_loaders_point": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "fake_middle_point_cargocorp_lcv_m.two_loaders_point": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "composite_pricing__source_point_visited": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "linear_overweight": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "discrete_overweight.large": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "fake_middle_point_cargocorp_van.one_loader_point": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "composite_pricing__source_point_completed": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "composite_pricing__return_point_visited": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "composite_pricing__return_point_completed": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "discrete_overweight.medium": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "fake_middle_point_cargocorp_van.two_loaders_point": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "composite_pricing__destination_point_completed": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "composite_pricing__destination_point_visited": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "fake_middle_point_cargocorp_lcv_l.two_loaders_point": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    },
    "fake_middle_point_express": {
      "default_value": 0,
      "min_value": 0,
      "max_value": 100
    }
  }
}
)"));

  TripDetails trip_details(1, std::chrono::seconds(2), std::chrono::seconds(3),
                           std::chrono::seconds(0), std::chrono::seconds(0), {},
                           {});

  for (size_t i = 0; i < 5000; ++i) {
    lang::variables::TripDetails trip = {
        1,  // distance
        2   // time
    };
    ast.CalculateFix(vars, trip,
                     lang::variables::DynamicContext{
                         {}, price_calc::models::Price(100, 500)},
                     lang::models::ListLatestFeatures(), {});
  }
}

price_calc::models::BinaryData CompileExtraReturnField(
    const lang::models::Program& ast, const std::string& field_name) {
  price_calc::models::BinaryData result;
  lang::models::GlobalCompilationContext compilation_context{};
  price_calc::utils::OutputCodeStream os(result, compilation_context);
  lang::variables::BackendVariables vars{};
  const auto& features = lang::models::ListLatestFeatures();
  lang::models::LinkContext context(ast, features, {});
  context.SaveLocal(
      "fix", lang::models::Expression(lang::models::Scalar(std::cref(vars))));
  auto linked_body = ast.GetBody().Link(context);
  auto linked_expr = linked_body.expression->Link(context);
  for (const auto& field : linked_expr.GetType().ListFields()) {
    const auto id = field.GetId().name;
    if (id.GetName() == field_name) {
      os << linked_expr.GetField(id);
      return result;
    }
  }
  return result;
}

UTEST(Compiler, SerializeFundamentalRef) {
  const auto& ast = parser::Parse(
      R"(
        let v = fix.category;
        return {x=((ride.price.boarding > 0)?v:v + "a")};
  )",
      {});
  lang::variables::BackendVariables vars{};
  const auto& features = lang::models::ListLatestFeatures();
  lang::models::GlobalLinkContext link_context{};
  const auto linked_ast = ast.Link(vars, std::nullopt, features, link_context);
  ASSERT_EQ(linked_ast.Serialize(),
            "CR(boarding=TX(1,0),destination_waiting=TX(1,6),distance=TX(1,1),"
            "metadata=MAP(),requirements=TX(1,4),time=TX(1,2),transit_waiting="
            "TX(1,5),waiting=TX(1,3),x=T(B(TX(1,0),>,0.000000),\"\",\"a\"))");
  const auto compiled = CompileExtraReturnField(ast, "x");
  ASSERT_EQ(
      fmt::format("[{}]", fmt::join(compiled, ", ")),
      "[20, 0, 17, 0, 0, 0, 0, 0, 0, 0, 0, 80, 22, 0, 0, 22, 0, 1, 97, 0]");
}

UTEST(Compiler, SerializeRef) {
  const auto& ast = parser::Parse(
      R"(
        let v = fix.category;
        return {x=fix.exps};
  )",
      {});
  lang::variables::BackendVariables vars{};
  const auto& features = lang::models::ListLatestFeatures();
  lang::models::GlobalLinkContext link_context{};
  const auto linked_ast = ast.Link(vars, std::nullopt, features, link_context);
  ASSERT_EQ(
      linked_ast.Serialize(),
      "CR(boarding=TX(1,0),destination_waiting=TX(1,6),distance=TX(1,1),"
      "metadata=MAP(),requirements=TX(1,4),time=TX(1,2),transit_waiting=TX(1,5)"
      ",waiting=TX(1,3),x=Ref<std::unordered_map<std::string,std::unordered_"
      "map<std::string,lang::variables::ExperimentSubValue>>>)");

  ASSERT_THROW(CompileExtraReturnField(ast, "x"), std::domain_error);
}

UTEST(Compiler, UresolvedBvLink) {
  const auto& ast = parser::Parse(
      R"(
        return {boarding=fix.rounding_factor};
  )",
      {});
  lang::variables::BackendVariables vars{};
  price_calc::models::BinaryData result;
  lang::models::GlobalCompilationContext compilation_context{};
  price_calc::utils::OutputCodeStream os(result, compilation_context);
  auto features = lang::models::ListLatestFeatures();
  lang::models::LinkContext context(ast, features, {});
  ASSERT_THROW(ast.GetBody().Link(context), std::logic_error);
}

UTEST(Compiler, TaximeterVariableComp) {
  const auto& ast = parser::Parse(
      R"(
        return {boarding=fix.rounding_factor};
  )",
      {});
  lang::variables::BackendVariables vars{};
  price_calc::models::BinaryData result;
  lang::models::GlobalCompilationContext compilation_context{};
  price_calc::utils::OutputCodeStream os(result, compilation_context);
  auto features = lang::models::ListLatestFeatures();
  lang::models::LinkContext context(ast, features, {});
  ASSERT_THROW(ast.GetBody().Link(context), std::logic_error);
}

UTEST(Compiler, ForceInlining) {
  auto text = R"(
        let x = ride.price.distance * ride.price.time;
        return {boarding=ride.price.boarding + x};
  )";
  {
    auto ast = parser::Parse(text, {});
    lang::variables::BackendVariables vars{};
    auto features = lang::models::ListLatestFeatures();
    lang::models::LinkContext context(ast, features, {});
    context.SetForceInline();
    auto result = ast.GetBody().Link(context);
    ASSERT_EQ(result.expression->Serialize(),
              "NT(boarding=B(TX(1,0),+,B(TX(1,1),*,TX(1,2))))");
  }

  {
    auto ast = parser::Parse(text, {});
    lang::variables::BackendVariables vars{};
    auto features = lang::models::ListLatestFeatures();
    lang::models::LinkContext context(ast, features, {});
    context.UnsetForceInline();
    auto result = ast.GetBody().Link(context);
    ASSERT_EQ(result.expression->Serialize(),
              "NT(boarding=B(TX(1,0),+,RT(0)))");
  }
}

struct NoExceptionCatched : std::logic_error {
  NoExceptionCatched(const std::string& message) : std::logic_error(message) {}
};

std::string CatchAssertionMessage(const std::string& rule,
                                  const bool debug_enable = true) {
  const auto& ast = parser::Parse(rule + "\nreturn {};", {});
  lang::variables::BackendVariables vars{};
  TripDetails trip_details(1, std::chrono::seconds(2), std::chrono::seconds(3),
                           std::chrono::seconds(0), std::chrono::seconds(0), {},
                           {});
  lang::variables::TripDetails trip{};
  try {
    ast.CalculateFix(vars, trip,
                     lang::variables::DynamicContext{
                         {}, price_calc::models::Price(100, 500)},
                     lang::models::ListLatestFeatures(), {}, debug_enable);
  } catch (const parser::AssertionError& err) {
    return err.what();
  }
  throw NoExceptionCatched("Assertion error expected, but nothing happens");
}

UTEST(Compiler, AssertionTest) {
  ASSERT_EQ(CatchAssertionMessage("assert(2>3);"),
            "Assertion failed : At line 1. Expression: 2.0 > 3.0");
  ASSERT_EQ(CatchAssertionMessage("assert((2>3)?true:false);"),
            "Assertion failed : At line 1. Expression: false ? true : false");
  ASSERT_EQ(CatchAssertionMessage("assert(\"x\" in fix.exps);"),
            "Assertion failed : At line 1. Expression: \"x\" in {}");
  ASSERT_THROW(CatchAssertionMessage("assert(\"x\" in fix.exps);", false),
               NoExceptionCatched);
}

template <typename T>
struct T1 {};

template <typename T, typename U>
struct T2 {};

UTEST(Compiler, ParsingTemplateParameters) {
  parser::Parse(
      R"(
          function foo(v:  std::pair<std::string,lang::variables::CargoRequirementParams>) {
            return {};
          }
          if (fix.cargo_requirements as cr) {
            let r = fold(cr as v, foo, {});
          }
          return {};
        )",
      {});
  ASSERT_EQ("std::string", FixTypeNameTester<std::string>());
  ASSERT_EQ("T1<int>", FixTypeNameTester<T1<int>>());

  T2<T1<int>, T1<int>> v1;
  ASSERT_EQ("T2<T1<int>, T1<int>>", FixTypeNameTester<decltype(v1)>());

  T1<T1<T1<T1<int>>>> v2;
  ASSERT_EQ("T1<T1<T1<T1<int>>>>", FixTypeNameTester<decltype(v2)>());

  T2<T1<T1<T1<T1<int>>>>, T1<T1<T1<T1<int>>>>> v3;
  ASSERT_EQ("T2<T1<T1<T1<T1<int>>>>, T1<T1<T1<T1<int>>>>>",
            FixTypeNameTester<decltype(v3)>());

  T2<T2<T1<T1<T1<T1<int>>>>, T1<T1<T1<T1<int>>>>>,
     T2<T1<T1<T1<T1<int>>>>, T1<T1<T1<T1<int>>>>>>
      v4;
  ASSERT_EQ(
      "T2<T2<T1<T1<T1<T1<int>>>>, T1<T1<T1<T1<int>>>>>, "
      "T2<T1<T1<T1<T1<int>>>>, T1<T1<T1<T1<int>>>>>>",
      FixTypeNameTester<decltype(v4)>());
}

UTEST(Compiler, TestPreviousMetadata) {
  auto text = R"(
          using (MetadataRead) {
            let x = metadata["x"];
            return {boarding=ride.price.boarding + x};
          }
          return {};
    )";
  auto ast = parser::Parse(text, {});
  lang::variables::BackendVariables vars{};

  {
    lang::models::GlobalLinkContext link_context{};
    auto feature_set = lang::models::ListFeatures("9182490");
    auto calc_result =
        ast.CalculateFix(vars, {},
                         lang::variables::DynamicContext{
                             {}, price_calc::models::Price(100, 500)},
                         feature_set, {{{"x", 123}}});
    EXPECT_EQ(calc_result.price.boarding, 223);
  }

  {
    lang::models::GlobalLinkContext link_context{};
    auto feature_set = lang::models::ListFeatures("8495361");
    auto calc_result =
        ast.CalculateFix(vars, {},
                         lang::variables::DynamicContext{
                             {}, price_calc::models::Price(100, 500)},
                         feature_set, {{{"x", 123}}});
    EXPECT_EQ(calc_result.price.boarding, 100);
  }
}

struct CompilationResult {
  std::string serialized_ast;
  std::string bytecode;
};

std::vector<CompilationResult> CompileSequence(
    const std::vector<std::string>& rules) {
  std::vector<CompilationResult> result{};
  lang::models::GlobalLinkContext link_context{};
  lang::variables::BackendVariables vars{};
  lang::models::GlobalCompilationContext compilation_context{};
  auto feature_set = lang::models::ListFeatures("9182490");
  std::vector<lang::models::LinkedProgram> linked_programs;
  for (const auto& rule : rules) {
    auto ast = parser::Parse(rule, {});
    linked_programs.emplace_back(ast.Link(vars, {}, feature_set, link_context));
    result.push_back({linked_programs.back().Serialize(), ""});
  }

  auto result_it = result.rbegin();
  for (auto it = linked_programs.rbegin(); it != linked_programs.rend();
       ++it, ++result_it) {
    result_it->bytecode =
        test_utils::ToHex(it->Compile({}, {}, compilation_context));
  }
  return result;
}

UTEST(Compiler, TestPreviousMetaLink) {
  {
    auto result = CompileSequence({R"(
            if (fix.surge_params.value < 2) {
              return {metadata=["x":42]};
            }
            return {};)",
                                   R"(
          using (MetadataRead) {
            let x = metadata["x"];
            return {boarding=ride.price.boarding + x};
          }
          return {};
    )"});
    EXPECT_EQ(result[1].serialized_ast,
              "CR(boarding=B(TX(1,0),+,42.000000),destination_waiting=TX(1,6),"
              "distance=TX(1,1),metadata=MAP(),requirements=TX(1,4),time=TX(1,"
              "2),transit_waiting=TX(1,5),waiting=TX(1,3))");
    EXPECT_EQ(result[1].bytecode,
              "14 00 11 40 45 00 00 00 00 00 00 20 14 01 14 02 14 03 14 04 14 "
              "05 14 06 81");
  }

  {
    auto result = CompileSequence(
        {R"(return {metadata=["x": 42, "y": ride.price.boarding*2]};)",
         R"(
          using (MetadataRead) {
            let y = metadata["y"];
            return {boarding=ride.price.boarding + y};
          }
          return {};
    )"});
    EXPECT_EQ(result[0].serialized_ast,
              "SG(0,B(TX(1,0),*,2.000000));E(\"x\",42.000000);E(\"y\",B(TX(1,0)"
              ",*,2.000000));CR(boarding=TX(1,0),destination_waiting=TX(1,6),"
              "distance=TX(1,1),metadata=MAP(\"x\"=42.000000,\"y\"=B(TX(1,0),*,"
              "2.000000)),requirements=TX(1,4),time=TX(1,2),transit_waiting=TX("
              "1,5),waiting=TX(1,3))");
    EXPECT_EQ(result[0].bytecode,
              "14 00 11 40 00 00 00 00 00 00 00 22 85 00 00 14 00 14 01 14 02 "
              "14 03 14 04 14 05 14 06 81");
    EXPECT_EQ(result[1].serialized_ast,
              "SV(0,RG(0));CR(boarding=B(TX(1,0),+,RT(0)),destination_waiting="
              "TX(1,6),distance=TX(1,1),metadata=MAP(),requirements=TX(1,4),"
              "time=TX(1,2),transit_waiting=TX(1,5),waiting=TX(1,3))");
    EXPECT_EQ(result[1].bytecode,
              "19 00 00 82 00 00 14 00 17 00 00 20 14 01 14 02 14 03 14 04 14 "
              "05 14 06 81");
  }

  {
    auto result = CompileSequence({R"(
                if (ride.price.boarding > 100) {
                  return {metadata=["x": 42, "y": ride.price.boarding*2]};
                }
                return {};
        )",
                                   R"(using (MetadataRead) {
              return {boarding=ride.price.boarding + metadata["x"]};
          }
          return {};
    )"});
    EXPECT_EQ(result[0].serialized_ast,
              "SG(0,T(B(TX(1,0),>,100.000000),42.000000,NULL(std::optional<"
              "double>)));SG(1,T(B(TX(1,0),>,100.000000),B(TX(1,0),*,2.000000),"
              "NULL(std::optional<double>)));E(\"x\",T(B(TX(1,0),>,100.000000),"
              "42.000000,NULL(std::optional<double>)));E(\"y\",T(B(TX(1,0),>,"
              "100.000000),B(TX(1,0),*,2.000000),NULL(std::optional<double>)));"
              "CR(boarding=TX(1,0),destination_waiting=TX(1,6),distance=TX(1,1)"
              ",metadata=MAP(\"x\"=T(B(TX(1,0),>,100.000000),42.000000,NULL("
              "std::optional<double>)),\"y\"=T(B(TX(1,0),>,100.000000),B(TX(1,"
              "0),*,2.000000),NULL(std::optional<double>))),requirements=TX(1,"
              "4),time=TX(1,2),transit_waiting=TX(1,5),waiting=TX(1,3))");
    EXPECT_EQ(result[1].serialized_ast,
              "SV(0,T(U(?,RG(0)),RG(0),0.000000));CR(boarding=B(TX(1,0),+,RT(0)"
              "),destination_waiting=TX(1,6),distance=TX(1,1),metadata=MAP(),"
              "requirements=TX(1,4),time=TX(1,2),transit_waiting=TX(1,5),"
              "waiting=TX(1,3))");
    EXPECT_EQ(result[0].bytecode,
              "14 00 11 40 59 00 00 00 00 00 00 50 11 40 45 00 00 00 00 00 00 "
              "18 00 85 00 00 14 00 14 01 14 02 14 03 14 04 14 05 14 06 81");
    EXPECT_EQ(result[1].bytecode,
              "19 00 00 54 19 00 00 11 00 00 00 00 00 00 00 00 00 82 00 00 14 "
              "00 17 00 00 20 14 01 14 02 14 03 14 04 14 05 14 06 81");
  }

  {
    auto result = CompileSequence({R"(
                if (ride.price.boarding > 100) {
                  return {metadata=["x": 42, "y": ride.price.boarding*2]};
                }
                return {};
        )",
                                   R"(using (MetadataRead) {
              return {boarding=("x" in metadata)?42:24};
          }
          return {};
    )"});
    EXPECT_EQ(result[1].serialized_ast,
              "CR(boarding=T(U(?,RG(0)),42.000000,24.000000),destination_"
              "waiting=TX(1,6),distance=TX(1,1),metadata=MAP(),requirements=TX("
              "1,4),time=TX(1,2),transit_waiting=TX(1,5),waiting=TX(1,3))");
    EXPECT_EQ(result[1].bytecode,
              "19 00 00 54 11 40 45 00 00 00 00 00 00 11 40 38 00 00 00 00 00 "
              "00 00 14 01 14 02 14 03 14 04 14 05 14 06 81");
  }
}
