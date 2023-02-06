#include <userver/utest/utest.hpp>

#include <fmt/format.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/utils/mock_now.hpp>

#include <js/wrappers/json_load_wrapper.hpp>

#include <js-pipeline/compilation/conventions.hpp>
#include <js-pipeline/execution/json_value/history/view.hpp>
#include <js-pipeline/execution/json_value/transaction/view.hpp>
#include <js-pipeline/execution/json_value/value_base.hpp>
#include <js-pipeline/execution/json_value/view.hpp>
#include <js-pipeline/utils.hpp>

using js_pipeline::execution::json_value::ValueBase;
using js_pipeline::execution::json_value::ValuePtr;

TEST(JSValue, Path) {
  auto value1 = ValueBase::New(formats::json::FromString(R"(
    {
      "o1": {
        "a1": [
          {
            "o2": {},
            "v": 8
          }
        ]
      }
    }
  )"),
                               "value1");

  EXPECT_EQ("value1.o1.a1[0].o2",
            value1->AsJson()["o1"]["a1"][0u].Get("o2")->GetPath());

  auto value2 = ValueBase::New(formats::json::FromString(R"(
    {
      "o3": {
        "o4": {
          "a2": [1,2,3]
        }
      }
    }
  )"),
                               "value2");

  value1->AsJson()["o1"]["a1"].Set(1u, std::move(value2->AsJson().Get("o3")));

  EXPECT_EQ("value1.o1.a1[1].o4.a2[1]",
            value1->AsJson()["o1"]["a1"][1u]["o4"]["a2"].Get(1u)->GetPath());
}

TEST(JSValue, History) {
  using js_pipeline::compilation::conventions::kLogRegionUserCode;
  using js_pipeline::execution::JsonLogger;
  using js_pipeline::execution::ResourcesLoggingMode;

  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);

  auto value1 = ValueBase::New(formats::json::FromString(R"(
    {
      "o1": {
        "a1": [
          {
            "o2": {},
            "v": 0
          }
        ]
      }
    }
  )"),
                               "value1");
  JsonLogger logger(
      "test_id", "test_name",
      /*resources_logging_mode=*/ResourcesLoggingMode::kInstanceParams);

  logger.EnterScope("test_stage_1");
  logger.SetRegion(kLogRegionUserCode, {/*iteration_idx=*/0});

  logger.Log(js::LogLevel::kDebug, "test debug log");

  {
    value1->AsJson()["o1"]["a1"].Get(0u)->AsTransactional().StageSet("v", 1,
                                                                     &logger);
  }

  value1->AsTransactional().Commit(nullptr);

  logger.SetRegion(kLogRegionUserCode, {/*iteration_idx=*/1});

  logger.Log(js::LogLevel::kInfo, "test info log");
  {
    value1->AsJson()["o1"].Get("a1")->AsTransactional().StageSet(
        0u, formats::json::FromString(R"({"o2": {"v": 0}, "v": 2})"), &logger);
  }

  logger.LeaveScope();

  value1->AsTransactional().Commit(nullptr);

  logger.EnterScope("test_stage_2");
  logger.SetRegion(kLogRegionUserCode, {/*iteration_idx=*/0});

  logger.Log(js::LogLevel::kWarning, "test warning log");
  logger.Log(js::LogLevel::kError, "test error log");
  { value1->AsTransactional().StageSet("o1", ValueBase::kNull, &logger); }
  logger.LeaveScope();

  value1->AsTransactional().Commit(nullptr);

  {  // resources logging
    class NotJsonJsWrapper final : public js::wrappers::JsWrapper {
      v8::Local<v8::Value> AsJsValue() const override {
        return v8::Null(js::GetCurrentIsolate());
      }
    };

    logger.LogResources(
        /*request=*/
        {
            {"r1", formats::json::FromString(R"({"p1": 0})")},
            {"r2", formats::json::FromString(R"({"p1": 1})")},
        },
        /*instances=*/
        {
            {"r1",
             std::make_unique<js::wrappers::JsonLoadJsWrapper>(
                 formats::json::FromString(R"({"f1": [1, 2, 3], "f2": {}})"))},
            {"r2", std::make_unique<js::wrappers::JsonLoadJsWrapper>(
                       formats::json::FromString(
                           R"({"f11": [11, 21, 31], "f21": {}})"))},
            {"r3", std::make_unique<NotJsonJsWrapper>()},
        },
        /*resource_name_by_field=*/
        {
            {"r1", "r_id1"},
            {"r2", "r_id2"},
        });
  }

  EXPECT_EQ(
      formats::json::FromString(fmt::format(
          R"(
    {{
      "$pipeline_id": "test_id",
      "$pipeline_name": "test_name",
      "$logs": [],
      "$resources": {{
        "r1": {{
          "$resource_id": "r_id1",
          "$params": {{"p1": 0}},
          "$instance": {{
            "f1": [1, 2, 3],
            "f2": {{}}
          }}
        }},
        "r2": {{
          "$resource_id": "r_id2",
          "$params": {{"p1": 1}},
          "$instance": {{
            "f11": [11, 21, 31],
            "f21": {{}}
          }}
        }},
        "r3": {{
          "$resource_id": "<no resource name (error)>",
          "$params": "<no params (prefetched)>",
          "$instance": "<not JSON serializable>"
        }}
      }},
      "$meta": [
        {{
          "$stage": "test_stage_1",
          "$iteration": 0,
          "$logs": [
            {{
              "$timestamp": "{0}",
              "$level": "debug",
              "$message": "test debug log",
              "$region": "{1}"
            }}
          ]
        }},
        {{
          "$stage": "test_stage_1",
          "$iteration": 1,
          "$logs": [
            {{
              "$timestamp": "{0}",
              "$level": "info",
              "$message": "test info log",
              "$region": "{1}"
            }}
          ]
        }},
        {{
          "$stage": "test_stage_2",
          "$iteration": 0,
          "$logs": [
            {{
              "$timestamp": "{0}",
              "$level": "warning",
              "$message": "test warning log",
              "$region": "{1}"
            }},
            {{
              "$timestamp": "{0}",
              "$level": "error",
              "$message": "test error log",
              "$region": "{1}"
            }}
          ]
        }}
      ],
      "o1": {{
        "a1": [
          {{
            "o2": {{
              "v": {{
                "$history": [
                  {{
                    "$value": 0,
                    "$meta_idx": 1
                  }},
                  {{
                    "$value": null,
                    "$meta_idx": 2
                  }}
                ]
              }}
            }},
            "v": {{
              "$history": [
                {{
                  "$value": 0,
                  "$meta_idx": null
                }},
                {{
                  "$value": 1,
                  "$meta_idx": 0
                }},
                {{
                  "$value": 2,
                  "$meta_idx": 1
                }},
                {{
                  "$value": null,
                  "$meta_idx": 2
                }}
              ]
            }}
          }}
        ]
      }}
    }}
  )",
          utils::datetime::TimestampToString(utils::datetime::Timestamp(now)),
          kLogRegionUserCode)),
      value1->AsHistorical().ToDetailedJson(logger));
}
