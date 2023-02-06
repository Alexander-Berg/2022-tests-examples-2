#include "compile.hpp"

#include <boost/algorithm/string/join.hpp>
#include <boost/range/adaptor/transformed.hpp>

#include <fmt/format.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/utils/assert.hpp>

#include <js-pipeline/compilation/codegen/pipeline/compile.hpp>
#include <js-pipeline/compilation/codegen/templates.hpp>
#include <js-pipeline/compilation/conventions.hpp>
#include <js-pipeline/models/pipeline_testing.hpp>

namespace js_pipeline::compilation::codegen::pipeline_tests {
namespace {
using handlers::libraries::js_pipeline::CombinedOutputCheck;
using handlers::libraries::js_pipeline::ImperativeOutputCheck;
using handlers::libraries::js_pipeline::OutputChecks;

std::string EncloseIds(const std::vector<std::string>& ids) {
  return boost::join(ids | boost::adaptors::transformed([](const auto& id) {
                       return fmt::format("'{}'", id);
                     }),
                     ", ");
}

void AddMocksBodies(Builder& builder, const models::ResourcesMocks& mocks) {
  for (const auto& [resource, mocks_by_id] : mocks.extra) {
    const auto mock_scope =
        builder.OpenScopeGuarded(fmt::format("{}: {{\n", resource), "},");
    for (const auto& [mock_id, mock_body] : mocks_by_id.extra) {
      builder.AddCode(fmt::format("{}: ", mock_id));
      const auto mock_scope = builder.OpenScopeGuarded(
          templates::GenFunctionPrefix(
              "", {conventions::testing::kResourceRequestUserCode}),
          "},");

      builder.AddComment("[mock body] user code begin\n");
      builder.AddUserCode(mock_body.mock_body,
                          fmt::format("mock_{}_{}", resource, mock_id));
      builder.AddCode("\n// [mock body] user code end\n");
    }
  }
}

void AddOutputCheck(Builder& builder,
                    const std::variant<CombinedOutputCheck,
                                       ImperativeOutputCheck>& output_check) {
  if (const auto* combined_check =
          std::get_if<CombinedOutputCheck>(&output_check)) {
    builder.AddCode(fmt::format(
        "let __etalon__ = {};\n"
        "assert_eq({}, __etalon__, {});\n",
        formats::json::ToString(combined_check->expected_output.extra),
        conventions::testing::kOutputUserCode,
        combined_check->additional_properties));
  } else if (const auto* imperative_check =
                 std::get_if<ImperativeOutputCheck>(&output_check)) {
    builder.AddComment("[check output] user code begin\n");
    builder.AddUserCode(imperative_check->source_code, "check_output");
    builder.AddCode("\n// [check output] user code end\n");
  } else {
    UINVARIANT(false, "Neither combined nor imperative check");
  }
}

void AddOutputChecksMap(Builder& builder, const OutputChecks& output_checks) {
  for (const auto& [check_id, check] : output_checks.extra) {
    builder.AddCode(fmt::format("{}: ", check_id));
    const auto check_scope =
        builder.OpenScopeGuarded(templates::GenFunctionPrefix("", {}), "},");
    AddOutputCheck(builder, check);
  }
}

void AddFetchResourceAssert(Builder& builder) {
  builder.AddCode(fmt::format(
      "function assert(__condition__, __message__) {{\n"
      "  if(!__condition__) {{\n"
      "    throw 'Assertion failed while fetching resource field \\'' + "
      "__field__ + '\\' at testcase ' + {0} + '.' + "
      "{1} + ': ' + __message__;\n"
      "  }}\n"
      "}}\n",
      conventions::testing::kTest, conventions::testing::kTestCase));
}

void AddCheckAssert(Builder& builder) {
  builder.AddCode(fmt::format(
      "function assert(__condition__, __message__) {{\n"
      "  if(!__condition__) {{\n"
      "    throw 'Assertion failed in testcase ' + {0} + '.' + "
      "{1} + ': ' + __message__;\n"
      "  }}\n"
      "}}\n",
      conventions::testing::kTest, conventions::testing::kTestCase));
}

void AddOutputChecks(Builder& builder,
                     const models::PipelineTestRequest& testing_data) {
  {
    const auto check_output_scope = builder.OpenScopeGuarded(
        templates::GenFunctionPrefix(
            conventions::testing::kCheckOutput,
            {conventions::testing::kOutputUserCode, conventions::testing::kTest,
             conventions::testing::kTestCase}),
        templates::FunctionSuffix);
    AddCheckAssert(builder);
    builder.AddCode(fmt::format(
        "function assert_eq(__obj__, __expected__, __addtitional_properties__"
        " = false, __path__ = []) {{\n"
        "  if (!__expected__ || !__obj__) {{\n"
        "    assert(__expected__ === __obj__, 'differ in path \"' + "
        "__path__.join('.') + '\": \\n+  ' + JSON.stringify(__expected__) + "
        "'\\n-  ' + JSON.stringify(__obj__));\n"
        "    return;\n"
        "  }}\n"
        "  if (!(__expected__ instanceof Object)) {{\n"
        "    assert(__expected__ === __obj__, 'differ in path \"' + "
        "__path__.join('.') + '\": \\n+  ' + JSON.stringify(__expected__) + "
        "'\\n-  ' + JSON.stringify(__obj__));\n"
        "    return;\n"
        "  }}\n"
        "  assert(__is_array__(__expected__) == __is_array__(__obj__),"
        " 'different types for \"' + __path__.join('.') + "
        "'\":\\n+  ' + JSON.stringify(__expected__) + '\\n-  '"
        " + JSON.stringify(__obj__));\n"
        "  let __seen__ = new Set();\n"
        "  for (var __prop__ in __expected__) {{\n"
        "    if (__prop__ instanceof Function) {{\n"
        "      assert((__prop__)(__obj__), 'functional check failed: for ' + "
        "__path__.join('.') + '\\n  value: ' + JSON.stringify(__obj__) + '\\n  "
        "fn: ' + __prop__.toString());\n"
        "    }} else if (__prop__ == '{0}') {{\n"
        "      let __check_fn__ = __expected__['{0}'];\n"
        "      assert(typeof __check_fn__ == 'string', __path__.join('.') + "
        "'.{0} is not a string');\n"
        "      assert(eval(__check_fn__)(__obj__), 'functional check failed: "
        "for ' + __path__.join('.') + '\\n  value: ' + JSON.stringify(__obj__)"
        " + '\\n  fn: ' + __check_fn__);\n"
        "    }} else if (__expected__.hasOwnProperty(__prop__)) {{\n"
        "      __path__.push(__prop__);\n"
        "      assert(__obj__.hasOwnProperty(__prop__), 'no ' + "
        "__path__.join('.') + ' field');\n"
        "      assert_eq(__obj__[__prop__], __expected__[__prop__], "
        "__addtitional_properties__, __path__);\n"
        "      __path__.pop();\n"
        "      __seen__.add(__prop__);\n"
        "    }}\n"
        "  }}\n"
        "  if(!__addtitional_properties__) {{\n"
        "    for(var __prop__ in __obj__) {{\n"
        "      if(__obj__.hasOwnProperty(__prop__) && !__seen__.has(__prop__))"
        " {{\n"
        "        __path__.push(__prop__);\n"
        "        assert(false, 'Found unexpected property ' + "
        "__path__.join('.'));\n"
        "      }}\n"
        "    }}\n"
        "  }}\n"
        "}}\n",
        conventions::testing::kEqCheckJs));
    {
      const auto checks_global_scope = builder.OpenScopeGuarded(
          "let __checks_global__ = {\n", templates::FunctionSuffix + ";");
      AddOutputChecksMap(builder, testing_data.output_checks);
    }
    {
      const auto tests_checks_scope = builder.OpenScopeGuarded(
          "let __checks_by_test__ = {\n", templates::FunctionSuffix + ";");
      for (const auto& test : testing_data.tests) {
        if (!test.output_checks) {
          continue;
        }
        const auto test_checks_scope =
            builder.OpenScopeGuarded(fmt::format("{} : {{\n", test.name), "},");
        AddOutputChecksMap(builder, *test.output_checks);
      }
    }
    {
      const auto chosen_checks_scope =
          builder.OpenScopeGuarded("let __chosen_checks__ = {\n", "};");
      for (const auto& test : testing_data.tests) {
        if (test.testcases.empty()) {
          continue;
        }
        const auto test_checks_scope =
            builder.OpenScopeGuarded(fmt::format("{} : {{\n", test.name), "},");
        for (const auto& testcase : test.testcases) {
          builder.AddCode(fmt::format("{}: [{}],\n", testcase.name,
                                      EncloseIds(testcase.output_checks)));
        }
      }
    }
    builder.AddCode(fmt::format(
        "let __checks__ =  __chosen_checks__[{0}][{1}];\n"
        "for(let __check_idx__ in __checks__) {{\n"
        "  let __check_id__ = __checks__[__check_idx__];\n"
        "  let __checks_bodies_test__ = __checks_by_test__[{0}];\n"
        "  if(__checks_bodies_test__ && (__check_id__ in "
        "__checks_bodies_test__)) {{\n"
        "    (__checks_bodies_test__[__check_id__])();\n"
        "    continue;\n"
        "  }}\n"
        "  assert(__check_id__ in __checks_global__, 'check id not found: ' "
        "+ __check_id__);\n"
        "  (__checks_global__[__check_id__])();\n"
        "}}\n",
        conventions::testing::kTest, conventions::testing::kTestCase));
  }
  builder.AddCode(fmt::format(
      "{0}({1}.{2}, {1}.{3}, {1}.{4});\n", conventions::testing::kCheckOutput,
      conventions::kContextPath, conventions::kContextOutputSuffix,
      conventions::testing::kTest, conventions::testing::kTestCase));
}

void AddMocks(Builder& builder,
              const models::PipelineTestRequest& testing_data) {
  const auto mocked_resources_scope = builder.OpenScopeGuarded(
      templates::GenFunctionPrefix(
          conventions::kGetMockedResources,
          {conventions::testing::kResourcesRequest, conventions::testing::kTest,
           conventions::testing::kTestCase}),
      templates::FunctionSuffix);
  AddFetchResourceAssert(builder);
  {
    const auto global_mocks_bodies_scope =
        builder.OpenScopeGuarded("const __global_mocks__ = {\n", "};");
    AddMocksBodies(builder, testing_data.resources_mocks);
  }
  {
    const auto tests_mocks_bodies_scope =
        builder.OpenScopeGuarded("const __tests_mocks__ = {\n", "};");
    for (const auto& test : testing_data.tests) {
      const auto test_scope =
          builder.OpenScopeGuarded(fmt::format("{}: {{\n", test.name), "},");
      if (test.resources_mocks) {
        AddMocksBodies(builder, *test.resources_mocks);
      }
    }
  }
  {
    const auto chosen_mocks_scope = builder.OpenScopeGuarded(
        "const __chosen_mocks_by_testcase__ = {\n", "};");
    for (const auto& test : testing_data.tests) {
      const auto test_scope =
          builder.OpenScopeGuarded(fmt::format("{}: {{\n", test.name), "},");
      for (const auto& testcase : test.testcases) {
        const auto testcase_scope = builder.OpenScopeGuarded(
            fmt::format("{}: {{\n", testcase.name), "},");
        for (const auto& [resource, mock_id] : testcase.resource_mocks.extra) {
          builder.AddCode(
              fmt::format("{}: {},\n", resource, fmt::format("'{}'", mock_id)));
        }
      }
    }
  }
  builder.AddCode(fmt::format(
      "let __result__ = {{}};\n"
      "let __chosen_mocks__ = __chosen_mocks_by_testcase__[{0}]"
      "[{1}];\n"
      "for (var __field__ in __resources_request__) {{\n"
      "  let __request__ = __resources_request__[__field__];\n"
      "  let __mock_id__ = __chosen_mocks__[__request__.name];\n"
      "  let __test_mocks__ = __tests_mocks__[{0}];\n"
      "  let __mock_body__;\n"
      "  if(__request__.name in __test_mocks__ && __mock_id__ in "
      "__test_mocks__[__request__.name]) {{\n"
      "    __mock_body__ = __test_mocks__[__request__.name][__mock_id__];\n"
      "  }} else {{\n"
      "    assert(__request__.name in __global_mocks__, 'no mocks for ' + "
      "__request__.name); \n"
      "    assert(__mock_id__ in __global_mocks__[__request__.name], "
      "'mock id not found: ' + __mock_id__); \n"
      "    __mock_body__ = __global_mocks__[__request__.name][__mock_id__];\n"
      "  }}\n"
      "  __result__[__field__] = (__mock_body__)(__request__.args);\n"
      "}}\n"
      "return __result__;\n",
      conventions::testing::kTest, conventions::testing::kTestCase));
}
}  // namespace

void Compile(const parsing::pipeline::Model& model, Builder& builder,
             const models::PipelineTestRequest& testing_data) {
  builder.AddCode(
      "function __fetch_resources__(fetch_args) {\n"
      "  let resources_request = {};\n"
      "  for (let field in fetch_args) {\n"
      "    if (!(field in __ctx__.__resource_name_by_field__)) {\n"
      "      throw 'no resource with field ' + field + ' defined';\n"
      "    }\n"
      "    resources_request[field] = {\n"
      "      name: __ctx__.__resource_name_by_field__[field],\n"
      "      args: fetch_args[field]\n"
      "    };\n"
      "  }\n"
      "  let instances = __get_mocked_resources__(resources_request, "
      "__ctx__.__test__, __ctx__.__testcase__);\n"
      "  __ctx__.__resource__.__extend__(instances);\n"
      "}\n");
  pipeline::Compile(model, builder, /*is_testing=*/true);
  AddOutputChecks(builder, testing_data);
  builder.CloseScope(0);
  AddMocks(builder, testing_data);
}

}  // namespace js_pipeline::compilation::codegen::pipeline_tests
