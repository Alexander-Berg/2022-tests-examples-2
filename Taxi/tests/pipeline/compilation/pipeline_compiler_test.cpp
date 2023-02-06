#include <js-pipeline/compilation/codegen/pipeline/compile.hpp>
#include <js-pipeline/compilation/codegen/pipeline_tests/compile.hpp>
#include <js-pipeline/compilation/compiled_pipelines.hpp>
#include <js-pipeline/compilation/parsing/pipeline/model.hpp>
#include <js-pipeline/compilation/parsing/validator.hpp>
#include <js-pipeline/errors.hpp>
#include <js-pipeline/fetching/schema/registry.hpp>
#include <js-pipeline/models/handles.hpp>
#include <js-pipeline/models/pipeline_testing.hpp>
#include <js-pipeline/types.hpp>

#include "../../common.hpp"

namespace js_pipeline::compilation {

namespace {

/// Rewrite all expected output for tests
constexpr bool kRewriteExpected = false;

void RewriteExpectedOutput(const std::string& filename,
                           const std::string& new_value) {
  const auto* test_info = testing::UnitTest::GetInstance()->current_test_info();
  const auto file =
      boost::filesystem::path(test_info->file()).filename().stem().string();

  std::ofstream out(kPathStatic + file + "/" + filename);
  out << new_value;
}

models::Pipeline MakePipeline(std::string id, std::string name,
                              models::StageOrGroups stages) {
  models::Pipeline result;
  result.id = std::move(id);
  result.name = std::move(name);
  result.stages = std::move(stages);
  return result;
}

void CheckCode(const char* expected_file_name, const std::string& code) {
  if (kRewriteExpected) {
    RewriteExpectedOutput(expected_file_name, code);
    FAIL() << "Reason: Rewrite enabled";
  } else {
    EXPECT_EQ(ReadResource(expected_file_name), code);
  }
}

}  // namespace

const ResourceMetadataMap kBlockingResourcesMetadata{
    {"surge_experiment", {false}}, {"surge_zone", {true}}};

const ResourceMetadataMap kNonBlockingResourcesMetadata{
    {"surge_experiment", {false}}, {"surge_zone", {false}}};

const models::Stage kFetchSurgeZone = [] {
  models::Stage result;
  result.name = "fetch_surge_zone";
  result.optional = false;
  result.source_code =
      "// using base_class and base_class_rule here;\n"
      "return {\n"
      "  surge_zone: {point: [0,0]},\n"
      "  surge_experiment: {point: [0,0]},\n"
      "};\n";
  result.in_bindings = {{{models::DataDomain::kInput}, {"point_a{point}", {}}}};
  result.conditions = {};
  result.resources = {{"surge_experiment", "surge_experiment"},
                      {"surge_zone", "surge_zone"}};
  return result;
}();

const std::string kUserCode1 = "// using class_name, rule and base_class here;";
const std::string kUserCode2 =
    "// using base_class and base_class_rule here;\n"
    "return {\n"
    "  value_raw: 1.2,\n"
    "  ps: 0.09,\n"
    "  f_derivative: -1.4,\n"
    "};\n";

CompiledPipeline Compile(
    const models::Pipeline& model, const ResourceMetadataMap& resource_meta,
    bool extended_check = true,
    const models::PipelineTestRequest* test_data_opt = nullptr) {
  compilation::parsing::Validator validator{resource_meta, extended_check};
  auto parsed_pipeline = parsing::pipeline::Model::Parse(model, validator);
  compilation::codegen::Builder builder{model.id, model.name,
                                        parsed_pipeline.global_user_code};

  if (test_data_opt) {
    codegen::pipeline_tests::Compile(parsed_pipeline, builder, *test_data_opt);
  } else {
    codegen::pipeline::Compile(parsed_pipeline, builder);
  }

  return {model.id, model.name, std::move(builder).GetCompiledPipelineBody()};
}

struct PrefetchConsumerTag : fetching::schema::ConsumerTagBase {
  static constexpr auto kName = "sample-consumer";
};

TEST(PipelineCompilerTest, Empty) {
  models::Pipeline pipeline = MakePipeline("id1", "empty_pipeline", {});
  EXPECT_THROW(Compile(pipeline, kBlockingResourcesMetadata),
               js_pipeline::CompileError);
  EXPECT_NO_THROW(
      Compile(pipeline, kBlockingResourcesMetadata, /*extended_check=*/false));
}

TEST(PipelineCompilerTest, Basic) {
  models::Pipeline pipeline = MakePipeline(
      "id1", "pipeline1",
      {kFetchSurgeZone,
       models::Stage{
           /*name=*/"stage1",
           /*optional=*/false,
           /*in_bindings=*/
           {
               {
                   {models::DataDomain::kResource},
                   {"surge_experiment.rules.*{class_name:rule}", {{}}},
               },
               {
                   {models::DataDomain::kResource},
                   {"surge_zone.base_class", {{}}},
               },
               {
                   {models::DataDomain::kResource},
                   {"surge_zone.some_array[0]{some_item0}", {{}}},
               },
               {
                   {models::DataDomain::kResource},
                   {"surge_zone.some_array[11]{some_item11}", {{}}},
               },
           },
           /*conditions=*/{{}},
           /*out_bindings=*/{{}},
           /*resources=*/std::nullopt,
           /*source_code=*/kUserCode1}});

  auto compiled = Compile(pipeline, kBlockingResourcesMetadata);
  const auto& prototype = compiled.GetBody().js_task_prototype;

  ASSERT_TRUE(prototype);

  auto code = Trim(prototype->code);

  CheckCode("basic.code.expected.js", code);
}

TEST(PipelineCompilerTest, HierarchicalInBindings) {
  using ChildrenCollection = models::InBindingChildren;
  const models::Stage kLogicTemplate{
      "template_stage",  // name
      false,             // optional
      {
          // in_bindings
          {
              {models::DataDomain::kResource},  // domain
              {"surge_zone.level_0",            // query
               {{}}},                           // children
          },
      },
      {{}},  // conditions
      {{}},  // out_bindings
      std::nullopt,
      "",  // code
  };

  const auto CreateLogicStage =
      [&kLogicTemplate](ChildrenCollection&& hierarchy) {
        static size_t stage_idx = 0;
        auto ret = kLogicTemplate;
        ret.name = "stage" + std::to_string(++stage_idx);
        ret.in_bindings[0].children = std::move(hierarchy);
        return ret;
      };

  models::Pipeline pipeline{"id1"};
  pipeline.name = "pipeline1";
  pipeline.stages = {kFetchSurgeZone};

  pipeline.stages.push_back({});
  // Capture in non-leaf
  pipeline.stages.back() = CreateLogicStage({
      {"level_1_a"},
      {"level_1_b{forbidden}",
       {{
           {"level_2"},
       }}},
  });
  EXPECT_THROW(Compile(pipeline, kBlockingResourcesMetadata),
               js_pipeline::CompileError);

  pipeline.stages.back() = CreateLogicStage({
      {"level_1_a"},
      {"level_1_b{middle_capture}.not_allowed"},
  });
  EXPECT_THROW(Compile(pipeline, kBlockingResourcesMetadata),
               js_pipeline::CompileError);

  pipeline.stages.back() = CreateLogicStage({
      {"level_1_a"},
      {"level_1_b.*{key:value}",
       {{
           {"nested"},
       }}},
  });
  EXPECT_THROW(Compile(pipeline, kBlockingResourcesMetadata),
               js_pipeline::CompileError);

  pipeline.stages.back() = CreateLogicStage({
      {"level_1_a{same}"},
      {"level_1_b",
       {{
           {"nested{same}"},
       }}},
  });
  EXPECT_THROW(Compile(pipeline, kBlockingResourcesMetadata),
               js_pipeline::CompileError);

  pipeline.stages.pop_back();

  // simple case
  pipeline.stages.push_back(CreateLogicStage({
      {"level_1_a"},
      {"level_1_b",
       {{
           {"level_2_a"},
           {"level_2_b"},
       }}},
      {"level_1_c"},
  }));

  // iterations case
  pipeline.stages.push_back(CreateLogicStage({
      {"level_1_a"},
      {"level_1_b.*{idx:}",
       {{
           {"nested_1.*{key:value}"},
           {"simple_nested{aliased}"},
       }}},
  }));

  // old behaviour backward compatibility
  pipeline.stages.push_back(models::Stage{
      "old_behaviour",  // name
      false,            // optional
      {{
          {models::DataDomain::kResource},        // domain
          {"surge_zone{szone}.level_0{renamed}",  // query
           std::nullopt},                         // children
      }},
      {{}},  // conditions
      {{}},  // out_bindings
      std::nullopt,
      "",  // code
  });

  const auto compiled = Compile(pipeline, kBlockingResourcesMetadata);
  const auto& prototype = compiled.GetBody().js_task_prototype;

  ASSERT_TRUE(prototype);

  const auto code = Trim(prototype->code);
  CheckCode("hierarchical_in_bindings.code.expected.js", code);
}

TEST(PipelineCompilerTest, BasicNonBlockingFetch) {
  auto fetch_stage = kFetchSurgeZone;
  fetch_stage.optional = true;

  models::Pipeline pipeline = MakePipeline(
      "id1", "pipeline1",
      {fetch_stage,
       models::Stage{
           /*name=*/"stage1",
           /*optional=*/false,
           /*in_bindings=*/
           {
               {
                   {models::DataDomain::kResource},
                   {"surge_experiment.rules.*{class_name:rule}", {{}}},
               },
               {
                   {models::DataDomain::kResource},
                   {"surge_zone.base_class", {{}}},
               },
           },
           /*conditions=*/
           {{}},
           /*out_bindings=*/
           {{}},
           std::nullopt,
           /*code=*/kUserCode1,
       }});

  auto compiled = Compile(pipeline, kNonBlockingResourcesMetadata);
  const auto& prototype = compiled.GetBody().js_task_prototype;

  ASSERT_TRUE(prototype);

  auto code = Trim(prototype->code);
  CheckCode("basic_non_blocking_fetch.expected.js", code);
}

TEST(PipelineCompilerTest, ArrayPush) {
  models::Pipeline pipeline = MakePipeline(
      "id1", "pipeline1",
      {kFetchSurgeZone,
       models::Stage{
           /*name=*/"stage1",
           /*optional=*/false,
           /*in_bindings=*/
           {
               {
                   {models::DataDomain::kResource},
                   {"surge_experiment.rules.*{class_name:rule}", {}},
               },
               {
                   {models::DataDomain::kResource},
                   {"surge_zone.base_class", {}},
               },
           },
           /*conditions=*/
           {},
           /*out_bindings=*/
           {
               {{
                   {},
                   "classes[?(@.name==base_class)]",
                   {},
                   "base_class_info",
               }},
           },
           std::nullopt,
           /*code=*/kUserCode1,
       }});

  auto compiled = Compile(pipeline, kBlockingResourcesMetadata);
  const auto& prototype = compiled.GetBody().js_task_prototype;

  ASSERT_TRUE(prototype);

  auto code = Trim(prototype->code);

  CheckCode("array_push.code.expected.js", code);
}

TEST(PipelineCompilerTest, CapturedPropertyUseInCapture) {
  models::Pipeline pipeline = MakePipeline(
      "id1", "pipeline1",
      {kFetchSurgeZone,
       models::Stage{
           /*name=*/"stage1",
           /*optional=*/false,
           /*in_bindings=*/
           {
               {
                   {models::DataDomain::kResource},
                   {"surge_zone.base_class", {{}}},
               },
               {
                   {models::DataDomain::kResource},
                   {"surge_experiment.rules[base_class]{base_class_rule}",
                    {{}}},
               },
           },
           /*conditions=*/
           {{}},
           /*out_bindings=*/
           {{}},
           std::nullopt,
           /*code=*/kUserCode1,
       }});

  auto compiled = Compile(pipeline, kBlockingResourcesMetadata);
  const auto& prototype = compiled.GetBody().js_task_prototype;

  ASSERT_TRUE(prototype);

  auto code = Trim(prototype->code);

  CheckCode("captured_property_use_in_capture.code.expected.js", code);
}

TEST(PipelineCompilerTest, OutBindings) {
  models::Pipeline pipeline = MakePipeline(
      "id1", "pipeline1",
      {kFetchSurgeZone,
       models::Stage{
           /*name=*/"stage1",
           /*optional=*/false,
           /*in_bindings=*/
           {
               {
                   {models::DataDomain::kResource},
                   {"surge_experiment.rules.*{class_name:rule}", {{}}},
               },
               {
                   {models::DataDomain::kResource},
                   {"surge_zone.base_class", {{}}},
               },
           },
           /*conditions=*/
           {},
           /*out_bindings=*/
           {{
               {
                   {{{
                         {},
                         "value_raw",
                         {},
                         "value_raw",
                     },
                     {
                         {},
                         "f_derivative",
                         {},
                         "f_derivative",
                     }}},
                   "classes[?(@.name==base_class)]",
               },
               {
                   {},
                   "classes[base_class].ps",
                   {},
                   "ps",
               },
           }},
           std::nullopt,
           /*code=*/kUserCode2,
       }});

  auto compiled = Compile(pipeline, kBlockingResourcesMetadata);
  const auto& prototype = compiled.GetBody().js_task_prototype;

  ASSERT_TRUE(prototype);

  auto code = Trim(prototype->code);

  CheckCode("out_bindings.code.expected.js", code);
}

TEST(PipelineCompilerTest, OutBindingOperation) {
  models::Pipeline pipeline = MakePipeline(
      "id1", "pipeline1",
      {kFetchSurgeZone,
       models::Stage{
           /*name=*/"stage1",
           /*optional=*/false,
           /*in_bindings=*/
           {
               {
                   {models::DataDomain::kResource},
                   {"surge_experiment.rules.*{class_name:rule}", {{}}},
               },
               {
                   {models::DataDomain::kResource},
                   {"surge_zone.base_class", {{}}},
               },
           },
           /*conditions=*/
           {},
           /*out_bindings=*/
           {{
               {
                   {{{
                         {},
                         {},
                         handlers::libraries::js_pipeline::
                             StaticAccessOutOperation{"value_raw"},
                         "value_raw",
                     },
                     {
                         {},
                         {},
                         handlers::libraries::js_pipeline::
                             StaticAccessOutOperation{"f_derivative"},
                         "f_derivative",
                     }}},
                   "classes[?(@.name==base_class)]",
               },
               {
                   {},
                   {},
                   handlers::libraries::js_pipeline::StaticAccessOutOperation{
                       "classes[base_class].ps"},
                   "ps",
               },
           }},
           std::nullopt,
           /*code=*/kUserCode2,
       }});

  auto compiled = Compile(pipeline, kBlockingResourcesMetadata);
  const auto& prototype = compiled.GetBody().js_task_prototype;

  ASSERT_TRUE(prototype);

  auto code = Trim(prototype->code);

  CheckCode("out_bindings.code.expected.js", code);
}

TEST(PipelineCompilerTest, Conditions) {
  models::Pipeline pipeline = MakePipeline(
      "id1", "pipeline1",
      {kFetchSurgeZone,
       models::Stage{
           /*name=*/"stage1",
           /*optional=*/false,
           /*in_bindings=*/
           {
               {
                   {models::DataDomain::kResource},
                   {"surge_experiment.rules.*{class_name:rule}", {}},
               },
               {
                   {models::DataDomain::kResource},
                   {"surge_zone.base_class", {}},
               },
           },
           /*conditions=*/
           {models::ConditionExpression{
               models::ConditionExpressionType::kAnd,
               {{models::StageStatusCondition{/*stage_name=*/"balance_equation",
                                              /*allowed_statuses=*/
                                              {{
                                                  models::StageStatus::kPassed,
                                                  models::StageStatus::kOmitted,
                                              }}}},
                {models::StageStatusCondition{/*stage_name=*/"smoothing",
                                              /*allowed_statuses=*/
                                              {
                                                  models::StageStatus::kPassed,
                                              }}}},
           }},
           /*out_bindings=*/
           {{
               {
                   {},
                   "classes[?(@.name==base_class)].value_raw",
                   {},
                   "value_raw",
               },
               {
                   {},
                   "classes[base_class].ps",
                   {},
                   "ps",
               },
               {
                   {},
                   "classes[?(@.name==base_class)].f_derivative",
                   {},
                   "f_derivative",
               },
           }},
           std::nullopt,
           /*code=*/kUserCode2,
       }});

  EXPECT_THROW(Compile(pipeline, kBlockingResourcesMetadata),
               js_pipeline::CompileError);

  ::Get<models::Stage>(pipeline.stages[1]).optional = true;

  EXPECT_THROW(Compile(pipeline, kBlockingResourcesMetadata),
               js_pipeline::CompileError);

  ::Get<models::Stage>(pipeline.stages[1]).conditions = models::Conditions{
      {models::StageStatusCondition{/*stage_name=*/"fetch_surge_zone",
                                    /*allowed_statuses=*/
                                    {{
                                        models::StageStatus::kPassed,
                                        models::StageStatus::kOmitted,
                                    }}}}};

  auto compiled = Compile(pipeline, kBlockingResourcesMetadata);
  const auto& prototype = compiled.GetBody().js_task_prototype;

  ASSERT_TRUE(prototype);

  auto code = Trim(prototype->code);

  CheckCode("conditions.code.expected.js", code);
}

TEST(PipelineCompilerTest, PredicateConditions) {
  models::Pipeline pipeline =
      MakePipeline("id1", "pipeline1",
                   {kFetchSurgeZone,
                    models::Stage{/*name=*/"predicate_stage",
                                  /*optinoal=*/false,
                                  /*in_bindings=*/
                                  {{
                                      {models::DataDomain::kResource},
                                      {"surge_zone.base_class", {}},
                                  }},
                                  std::nullopt,
                                  std::nullopt,
                                  std::nullopt,
                                  /*code=*/"return true;",
                                  /*function=*/std::nullopt,
                                  /*args=*/{{{"argument"}}},
                                  /*default_value*/ {}},
                    models::Stage{
                        /*name=*/"call_predicate",
                        /*optional=*/true,
                        /*in_bindings=*/
                        {{
                            {models::DataDomain::kInput},
                            {"some_value", {}},
                        }},
                        /*conditions=*/
                        {models::ConditionExpression{
                            models::ConditionExpressionType::kNot,
                            {
                                models::PredicateCondition{
                                    /*predicate_name=*/"predicate_stage",
                                    /*args=*/{{}}},
                            }}},
                        /*out_bindings=*/
                        {{{
                            {},
                            "value_raw",
                            {},
                            "value_raw",
                        }}},
                        std::nullopt,
                        /*code=*/"return {value_raw: some_value + 1};",
                    }});

  // call predicate without args
  EXPECT_THROW(Compile(pipeline, kNonBlockingResourcesMetadata),
               js_pipeline::CompileError);

  auto& predicate = ::Get<models::PredicateCondition>(
      ::Get<models::ConditionExpression>(
          *::Get<models::Stage>(pipeline.stages[2]).conditions)
          .args.front());

  auto& predicate_condition_args = *predicate.args;

  predicate_condition_args.push_back(
      models::PredicateCallArg{"argument", "undefined_value"});
  // call predicate with wrong value as argument
  EXPECT_THROW(Compile(pipeline, kNonBlockingResourcesMetadata),
               js_pipeline::CompileError);

  predicate_condition_args.front() =
      models::PredicateCallArg{"argument", "some_value"};
  auto compiled = Compile(pipeline, kNonBlockingResourcesMetadata);
  const auto& prototype = compiled.GetBody().js_task_prototype;

  ASSERT_TRUE(prototype);

  auto code = Trim(prototype->code);

  CheckCode("predicate_condition.code.expected.js", code);
}

TEST(PipelineCompilerTest, PredicateStageStatus) {
  auto pipeline =
      MakePipeline("id1", "pipeline1",
                   {kFetchSurgeZone,
                    models::Stage{/*name=*/"predicate_stage",
                                  /*optional=*/false,
                                  /*in_bindings=*/
                                  {{
                                      {models::DataDomain::kResource},
                                      {"surge_zone.base_class", {{}}},
                                  }},
                                  std::nullopt,
                                  std::nullopt,
                                  std::nullopt,
                                  /*code=*/"return true;",
                                  /*function=*/std::nullopt,
                                  /*args=*/{{{"argument"}}},
                                  /*default_value*/ {}},
                    models::Stage{
                        /*name=*/"call_predicate",
                        /*optional=*/true,
                        /*in_bindings=*/
                        {{
                            {models::DataDomain::kInput},
                            {"some_value", {}},
                        }},
                        /*conditions=*/
                        {models::Conditions{models::StageStatusCondition{
                            /*stage_name=*/"predicate_stage",
                            /*allowed_statuses=*/
                            {{
                                models::StageStatus::kPassed,
                                models::StageStatus::kOmitted,
                            }},
                        }}},
                        /*out_bindings=*/
                        {{{
                            {},
                            "value_raw",
                            {},
                            "value_raw",
                        }}},
                        std::nullopt,
                        /*code=*/"return {value_raw: some_value + 1};",
                    }});

  // stage status condition depending on predicate status
  EXPECT_THROW(Compile(pipeline, kNonBlockingResourcesMetadata),
               js_pipeline::CompileError);
}

TEST(PipelineCompilerTest, PredicateComplexConditions) {
  using models::ConditionExpression;
  using ExprType = models::ConditionExpressionType;

  const models::Stage predicate_1 = {
      "predicate_1",                     // name
      false,                             // optional
      {},                                // in_bindings
      std::nullopt,                      // conditions
      std::nullopt,                      // out_bindings
      std::nullopt,                      // resources
      "return {};",                      // code
      std::nullopt,                      // function
      {{{"arg1"}, {"arg2"}, {"arg3"}}},  // args
      {},                                // default_value
  };
  const models::Stage predicate_2 = {
      "predicate_2",                     // name
      false,                             // optional
      {},                                // in_bindings
      std::nullopt,                      // conditions
      std::nullopt,                      // out_bindings
      std::nullopt,                      // resources
      "return {};",                      // code
      std::nullopt,                      // function
      {{{"arg4"}, {"arg5"}, {"arg6"}}},  // args
      {},                                // default_value
  };
  const models::Stage predicate_3 = {
      "predicate_3",  // name
      false,          // optional
      {},             // in_bindings
      std::nullopt,   // conditions
      std::nullopt,   // out_bindings
      std::nullopt,   // resources
      "return {};",   // code
      std::nullopt,   // function
      {{}},           // args
      {},             // default_value
  };

  const auto dup_with_name = [](const auto& obj, std::string name) {
    auto copy = obj;
    copy.name = name;
    return copy;
  };
  const auto predicate_5 = dup_with_name(predicate_3, "predicate_5");
  const auto predicate_6 = dup_with_name(predicate_3, "predicate_6");

  models::QueryObject top_query = {
      {models::StaticAccessOperation{"query"},
       models::StaticAccessOperation{"step"},
       models::IterationOperation{models::IterationOperationType::kIteration,
                                  "val1"}}};

  const models::PredicateCondition cond_1{
      /*name=*/"predicate_1",
      /*args=*/{{{"arg1", "val1"}, {"arg2", "val2"}, {"arg3", "val3"}}}};

  const models::PredicateCondition cond_2{
      /*name=*/"predicate_2",
      /*args=*/{{{"arg4", "val4"}, {"arg5", "val5"}, {"arg6", "val6"}}}};
  const models::PredicateCondition cond_3{/*name=*/"predicate_3",
                                          /*args=*/{{}}};
  const models::StageStatusCondition cond_4{
      /*stage_name*/ kFetchSurgeZone.name,
      /*allowed_statuses=*/
      {
          models::StageStatus::kPassed,
      },
  };
  const models::Stage logic_1{
      "logic_1",  // name
      true,       // optional
      // in_bindings
      {{{models::DataDomain::kInput},
        {
            top_query,
            {{{"nested",
               {{{"two{val2}"},
                 {"three{val3}"},
                 {"deep.*{val5:}",
                  {{{"even",
                     {{{"four{val4}"},
                       {"six{val6}"},
                       {"more.deep.*{very:important}"}}}}}}}}}}}},
        }}},
      {ConditionExpression{ExprType::kAnd,
                           {
                               cond_1,
                               cond_2,
                               cond_3,
                               cond_4,
                           }}},
      {{}},          // out_bindings
      std::nullopt,  // resources
      "return {}",   // code
  };

  const models::PredicateCondition cond_5{"predicate_5", {{}}};
  const models::PredicateCondition cond_6{"predicate_6", {{}}};
  const models::Stage logic_2{
      "logic_2",  // name
      true,       // optional
      // in_bindings
      {},
      {ConditionExpression{
          ExprType::kOr,
          {cond_5,
           ConditionExpression{
               ExprType::kAnd,
               {cond_6, ConditionExpression{ExprType::kNot, {cond_3}}}},
           cond_3,
           ConditionExpression{
               ExprType::kOr,
               {cond_4, ConditionExpression{ExprType ::kNot, {cond_6}}}}}}},
      {{}},          // out_bindings
      std::nullopt,  // resources
      "return {}",   // code
  };

  const auto pipeline =
      MakePipeline("id1", "pipeline",
                   {predicate_1, predicate_2, predicate_3, predicate_5,
                    predicate_6, kFetchSurgeZone, logic_1, logic_2});

  const auto compiled = Compile(pipeline, kNonBlockingResourcesMetadata);
  const auto& prototype = compiled.GetBody().js_task_prototype;

  ASSERT_TRUE(prototype);

  auto code = Trim(prototype->code);

  CheckCode("complex_conditions.expected.js", code);
}

TEST(PipelineCompilerTest, ResourceAliases) {
  const ResourceMetadataMap resource_meta{{"resource", {false}}};
  const models::Stage resource{
      "stage1",                // name
      false,                   // is_optional
      {},                      // in_bindings
      {},                      // conditions
      std::nullopt,            // out_bindings
      {{{"resource", "r0"}}},  // resources
      "",                      // code
  };
  const models::Stage resource1{
      "stage2",                // name
      false,                   // is_optional
      {},                      // in_bindings
      {},                      // conditions
      std::nullopt,            // out_bindings
      {{{"resource", "r1"}}},  // resources
      "",                      // code
  };
  const models::Stage resource2{
      "stage3",                                          // name
      false,                                             // is_optional
      {},                                                // in_bindings
      {},                                                // conditions
      std::nullopt,                                      // out_bindings
      {{{"resource", "r2"}, {"resource", "resource"}}},  // resources
      "",                                                // code
  };
  const models::Stage sum{
      "stage4",                                               // name
      false,                                                  // is_optional
      {{{models::DataDomain::kResource}, {"resource", {}}}},  // in_bindings
      {},                                                     // conditions
      {{{{}, "result", {}, "result"}}},                       // out_bindings
      std::nullopt,                                           // resources
      "result = resource + resource + resource",              // code
  };

  {
    auto pipeline = MakePipeline(
        "id1", "pipeline1", {resource, resource, resource2, sum}  //
    );

    EXPECT_THROW(Compile(pipeline, resource_meta), js_pipeline::CompileError);
  }

  {
    auto pipeline = MakePipeline(
        "id1", "pipeline1", {resource, resource1, resource2, sum}  //
    );
    auto compiled = Compile(pipeline, resource_meta);

    const auto& prototype = compiled.GetBody().js_task_prototype;

    ASSERT_TRUE(prototype);

    auto code = Trim(prototype->code);
    CheckCode("resource_aliases.expected.js", code);
  }
}

TEST(PipelineCompilerTest, PrefetchedResources) {
  using fetching::schema::ConsumerRegistry;
  const ResourceMetadataMap resource_meta{{"preloaded_resource", {false}}};

  auto& registry = ConsumerRegistry<PrefetchConsumerTag>::Get();
  registry.RegisterResource("preloaded_resource", "preloaded_field", nullptr,
                            nullptr);

  const models::Stage usage_stage{
      "usage_stage",  // name
      false,          // is_optional
      {               // in_bindings
       {
           {models::DataDomain::kResource},
           {"preloaded_field{res_alias}", {}},
       }},
      {{}},  // out_bindings
      {{}},  // conditions
      std::nullopt,
      "",  // code
  };

  auto pipeline = MakePipeline("id1", "pipeline1", {usage_stage});
  EXPECT_THROW(Compile(pipeline, resource_meta), js_pipeline::CompileError);

  pipeline.consumer = PrefetchConsumerTag::kName;

  const auto compiled = Compile(pipeline, resource_meta);

  const auto& prototype = compiled.GetBody().js_task_prototype;

  ASSERT_TRUE(prototype);

  const auto code = Trim(prototype->code);

  CheckCode("prefetched_resources.expected.js", code);
}

TEST(PipelineCompilerTest, CompileTestsBasic) {
  models::Pipeline pipeline = MakePipeline(
      "id1", "pipeline1",
      {kFetchSurgeZone,
       models::Stage{
           /*name=*/"stage5",
           /*optional=*/false,
           /*in_bindings=*/
           {
               {
                   {models::DataDomain::kResource},
                   {"surge_experiment.rules.*{class_name:rule}", {{}}},
               },
           },
           /*conditions=*/{{}},
           /*out_bindings=*/{{}},
           std::nullopt,
           /*source_code=*/kUserCode1}});
  models::PipelineTestRequest test_request;
  test_request.resources_mocks.extra["surge_experiment"].extra["mock1"] = {
      "// surge_experiment mock body"};
  test_request.output_checks.extra["check_1"] =
      handlers::libraries::js_pipeline::CombinedOutputCheck{};
  models::PipelineTest test{
      /*id=*/"0",
      /*name=*/"atest",
      /*scope*/ handlers::libraries::js_pipeline::PipelineTestScope::kGlobal};
  test.output_checks.emplace();
  test.output_checks->extra["check_2"] =
      handlers::libraries::js_pipeline::ImperativeOutputCheck{
          "assert(output instanceof Object, 'Is not an object!');"};
  models::PipelineTestCase testcase;
  testcase.name = "testcase1";
  testcase.resource_mocks.extra["surge_experiment"] = "mock1";
  testcase.output_checks = {"check_1", "check_2"};

  test.testcases.push_back(std::move(testcase));
  test_request.tests.push_back(std::move(test));

  auto compiled =
      Compile(pipeline, kBlockingResourcesMetadata, true, &test_request);

  const auto& prototype = compiled.GetBody().js_task_prototype;
  ASSERT_TRUE(prototype);
  auto code = Trim(prototype->code);

  CheckCode("basic.test.expected.js", code);
}

TEST(PipelineCompilerTest, GlobalScope) {
  models::Pipeline pipeline = MakePipeline(
      "id1", "pipeline1",
      {kFetchSurgeZone,
       models::Stage{
           /*name=*/"stage1",
           /*optional=*/false,
           /*in_bindings=*/
           {
               {
                   {models::DataDomain::kResource},
                   {"surge_experiment.rules.*{class_name:rule}", {{}}},
               },
               {
                   {models::DataDomain::kResource},
                   {"surge_zone.base_class", {{}}},
               },
               {
                   {models::DataDomain::kResource},
                   {"surge_zone.some_array[0]{some_item0}", {{}}},
               },
               {
                   {models::DataDomain::kResource},
                   {"surge_zone.some_array[11]{some_item11}", {{}}},
               },
           },
           /*conditions=*/{{}},
           /*out_bindings=*/{{}},
           std::nullopt,
           /*source_code=*/kUserCode1}});

  pipeline.global_scope = {/*source_code=*/"function foo() { return 'bar'; }"};

  auto compiled = Compile(pipeline, kBlockingResourcesMetadata);

  const auto& prototype = compiled.GetBody().js_task_prototype;
  ASSERT_TRUE(prototype);
  auto code = Trim(prototype->code);

  CheckCode("global_scope.code.expected.js", code);
}

}  // namespace js_pipeline::compilation
