#include <gtest/gtest.h>

#include <radio/blocks/aggregation/state_aggregator_by_conditions.hpp>
#include <radio/blocks/aggregation/worst_state_aggregator.hpp>
#include "../tools/testutils.hpp"
#include "radio/blocks/commutation/entry_points.hpp"
#include "radio/blocks/commutation/output_consumer.hpp"
#include "radio/blocks/utils/buffers.hpp"
#include "radio/circuit.hpp"

namespace hejmdal::radio::blocks {

namespace {

static const std::string kSchemaStr = R"=(
{
  "name": "test_schema",
  "blocks": [
    {
      "id": "aggregator",
      "type": "state_aggregator_by_conditions",
      "aggregation_key": "cpu_key",
      "add_not_ok_to_meta": true,
      "skip_no_data": false,
      "condition": {
        "is_one_of": ["Warning", "Critical"]
      },
      "target_status": "Warning",
      "meta_fields_to_merge": ["host_name", "domain"]
    }
  ],
  "entry_points": [
    {
      "id": "entry_state",
      "type": "state_connection_point",
      "meta_override_keys": [
      "circuit_id",
      "juggler_service_name"
      ]
    }
  ],
  "out_points": [
    {
      "id": "out_state",
      "type": "state_out_point"
    }
  ],
  "wires": [
    {
      "from": "entry_state",
      "to": "aggregator",
      "type": "state"
    },
    {
      "from": "aggregator",
      "to": "out_state",
      "type": "state"
    }
]
}
)=";

static const std::string kCpuBuilder = R"=(
{
  "id": "cpu_aggregator",
  "aggregator_type": "worst_state_aggregator",
  "aggregation_key": "host_name",
  "add_not_ok_to_meta": true,
  "save_not_ok_to_db": true,
  "skip_no_data": false,
  "additional_meta": {
    "check_type": "cpu"
  }
}
)=";

static const std::string kTimingsBuilder = R"=(
{
  "id": "timings_aggregator",
  "aggregator_type": "worst_state_aggregator",
  "aggregation_key": "timings_type",
  "add_not_ok_to_meta": true,
  "save_not_ok_to_db": true,
  "skip_no_data": false,
  "additional_meta": {
    "check_type": "timings"
  }
}
)=";

static const std::string kCpuTimingsBuilder = R"=(
{
  "id": "cpu_timings_aggregator",
  "aggregator_type": "state_aggregator_by_conditions",
  "aggregation_key": "check_type",
  "add_not_ok_to_meta": true,
  "save_not_ok_to_db": true,
  "skip_no_data": false,
  "condition": {
    "is_one_of": ["Warning", "Critical"]
  },
  "target_status": "Warning",
  "meta_fields_to_merge": [
    "host_name",
    "timings_type",
    "aggregation"
  ]
}
)=";

static const std::string kExpectedMeta = R"=(
{
  "host_name": "host_1",
  "aggregation": {
    "cpu_aggregator": {
      "aggregator_type": "worst_state_aggregator",
      "aggregation_key": "host_name",
      "not_ok": [
        {
          "host_name": "host_2",
          "state": "Critical"
        },
        {
          "host_name": "host_3",
          "state": "Warning"
        }
      ]
    },
    "timings_aggregator": {
      "aggregator_type": "worst_state_aggregator",
      "aggregation_key": "timings_type",
      "not_ok": [
        {
          "timings_type": "timing_1",
          "state": "NoData"
        },
        {
          "timings_type": "timing_2",
          "state": "Warning"
        },
        {
          "timings_type": "timing_3",
          "state": "Critical"
        }
      ]
    },
    "cpu_timings_aggregator": {
      "aggregator_type": "state_aggregator_by_conditions",
      "aggregation_key": "check_type",
      "not_ok": [
        {
          "check_type": "cpu",
          "state": "Critical"
        },
        {
          "check_type": "timings",
          "state": "Critical"
        }
      ]
    }
  },
  "timings_type": "timing_1"
}
)=";

}  // namespace

TEST(TestAggregatorByConditions, TestCircuitBuild) {
  auto circuit_ptr = Circuit::Build("test_state_aggregator",
                                    formats::json::FromString(kSchemaStr));
  EXPECT_TRUE(circuit_ptr != nullptr);
}

TEST(TestAggregatorByConditions, TestTwoLevelAggregation) {
  auto cpu_ag = std::make_shared<WorstStateAggregatorByMetaKey>(
      formats::json::FromString(kCpuBuilder));
  auto timings_ag = std::make_shared<WorstStateAggregatorByMetaKey>(
      formats::json::FromString(kTimingsBuilder));
  auto cpu_timings_ag = std::make_shared<StateAggregatorByConditions>(
      formats::json::FromString(kCpuTimingsBuilder));

  auto cpu_entry = std::make_shared<StateEntryPoint>("");
  cpu_entry->OnStateOut(cpu_ag);
  cpu_ag->OnStateOut(cpu_timings_ag);
  auto timings_entry = std::make_shared<StateEntryPoint>("");
  timings_entry->OnStateOut(timings_ag);
  timings_ag->OnStateOut(cpu_timings_ag);
  auto out = std::make_shared<StateBuffer>("");
  cpu_timings_ag->OnStateOut(out);

  cpu_entry->StateIn(Meta(formats::json::MakeObject("host_name", "host_1")),
                     time::Now(), State::kOk);
  cpu_entry->StateIn(Meta(formats::json::MakeObject("host_name", "host_2")),
                     time::Now(), State::kCritical);
  cpu_entry->StateIn(Meta(formats::json::MakeObject("host_name", "host_3")),
                     time::Now(), State::kWarn);

  timings_entry->StateIn(
      Meta(formats::json::MakeObject("timings_type", "timing_1")), time::Now(),
      State::kNoData);
  timings_entry->StateIn(
      Meta(formats::json::MakeObject("timings_type", "timing_2")), time::Now(),
      State::kWarn);
  timings_entry->StateIn(
      Meta(formats::json::MakeObject("timings_type", "timing_3")), time::Now(),
      State::kCritical);

  EXPECT_EQ(out->LastState(), State::kWarn);
  const auto& meta = out->LastMeta();
  auto meta_data = meta.Get(MetaDataKind::kCircuitStateData);

  EXPECT_EQ(formats::json::FromString(kExpectedMeta), meta_data);
}

}  // namespace hejmdal::radio::blocks
