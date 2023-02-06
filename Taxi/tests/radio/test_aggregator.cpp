#include <gtest/gtest.h>

#include <radio/blocks/aggregation/aggregation_meta_formatter.hpp>
#include <radio/blocks/aggregation/best_state_aggregator.hpp>
#include <radio/blocks/aggregation/worst_state_aggregator.hpp>
#include "../tools/testutils.hpp"
#include "radio/blocks/commutation/connection_points.hpp"
#include "radio/blocks/commutation/entry_points.hpp"
#include "radio/blocks/commutation/output_consumer.hpp"
#include "radio/blocks/utils/buffers.hpp"
#include "radio/circuit.hpp"

namespace hejmdal::radio::blocks {

namespace {

formats::json::Value schema = [] {
  std::string schema_str{
      "{\n"
      "  \"name\": \"test_schema\","
      "  \"blocks\": ["
      "    {\n"
      "      \"id\": \"aggregator\",\n"
      "      \"type\": \"worst_state_aggregator\",\n"
      "      \"aggregation_key\": \"cpu_key\",\n"
      "      \"add_not_ok_to_meta\": true,\n"
      "      \"skip_no_data\": false,\n"
      "      \"save_not_ok_to_db\": true\n"
      "    }\n"
      "  ],\n"
      "  \"entry_points\": [\n"
      "    {\n"
      "      \"id\": \"entry_state\",\n"
      "      \"type\": \"state_connection_point\",\n"
      "      \"meta_override_keys\": [\n"
      "      \"circuit_id\",\n"
      "      \"juggler_service_name\"\n"
      "      ]\n"
      "    }\n"
      "  ],\n"
      "  \"out_points\": [\n"
      "    {\n"
      "      \"id\": \"out_state\",\n"
      "      \"type\": \"state_out_point\"\n"
      "    }\n"
      "  ],\n"
      "  \"wires\": [\n"
      "    {\n"
      "      \"from\": \"entry_state\",\n"
      "      \"to\": \"aggregator\",\n"
      "      \"type\": \"state\"\n"
      "    },\n"
      "    {\n"
      "      \"from\": \"aggregator\",\n"
      "      \"to\": \"out_state\",\n"
      "      \"type\": \"state\"\n"
      "    }\n"
      "  ]\n"
      "}"};
  return formats::json::FromString(schema_str);
}();

}

TEST(TestAggregator, TestCircuitBuild) {
  auto circuit_ptr = Circuit::Build("test_state_aggregator", schema);
  EXPECT_TRUE(circuit_ptr != nullptr);
}

TEST(TestAggregator, TestWorstStateAggregation) {
  formats::json::ValueBuilder builder;
  builder["id"] = "aggregator";
  builder["aggregator_type"] = "worst_state_aggregator";
  builder["aggregation_key"] = "host";
  builder["add_not_ok_to_meta"] = true;
  builder["skip_no_data"] = false;
  auto ag =
      std::make_shared<WorstStateAggregatorByMetaKey>(builder.ExtractValue());

  auto entry = std::make_shared<StateEntryPoint>("");
  entry->OnStateOut(ag);
  auto out = std::make_shared<StateBuffer>("");
  ag->OnStateOut(out);

  formats::json::ValueBuilder meta_builder;
  meta_builder["host"] = "host_1";
  entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(), State::kWarn);
  meta_builder["host"] = "host_2";
  entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(), State::kError);
  EXPECT_EQ(out->LastState(), State::kError);

  auto not_ok = out->LastMeta().Get("aggregation")["aggregator"]["not_ok"];
  EXPECT_TRUE(not_ok.IsArray());
  EXPECT_EQ(not_ok.GetSize(), 2);
  EXPECT_EQ(not_ok[0]["host"].As<std::string>(), "host_1");
  EXPECT_EQ(not_ok[1]["host"].As<std::string>(), "host_2");
}

TEST(TestAggregator, TestWorstStateAggregationWithObject) {
  formats::json::ValueBuilder builder;
  builder["id"] = "aggregator";
  builder["aggregator_type"] = "worst_state_aggregator";
  builder["aggregation_key"] = "domain";
  builder["bypass_keys"].PushBack("description_info");
  builder["add_not_ok_to_meta"] = true;
  builder["skip_no_data"] = false;
  auto ag =
      std::make_shared<WorstStateAggregatorByMetaKey>(builder.ExtractValue());

  auto entry = std::make_shared<StateEntryPoint>("");
  entry->OnStateOut(ag);
  auto out = std::make_shared<StateBuffer>("");
  ag->OnStateOut(out);

  formats::json::ValueBuilder meta_builder;
  meta_builder["domain"]["name"] = "domain_1";
  meta_builder["domain"]["dorblu_object"] = "dorblu_object_1";
  meta_builder["domain"]["description_info"]["priority"] = 10.0;
  meta_builder["domain"]["description_info"]["description"] = "desc 1";
  entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(), State::kWarn);
  meta_builder["domain"]["name"] = "domain_1";
  meta_builder["domain"]["dorblu_object"] = "dorblu_object_1";
  meta_builder["domain"]["description_info"]["priority"] = 20.0;
  meta_builder["domain"]["description_info"]["description"] = "desc 2";
  entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(), State::kWarn);
  meta_builder["domain"]["name"] = "domain_2";
  meta_builder["domain"]["dorblu_object"] = "dorblu_object_2";
  meta_builder["domain"]["description_info"]["priority"] = 30.0;
  meta_builder["domain"]["description_info"]["description"] = "desc 3";
  entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(), State::kError);
  EXPECT_EQ(out->LastState(), State::kError);

  auto not_ok = out->LastMeta().Get("aggregation")["aggregator"]["not_ok"];
  EXPECT_TRUE(not_ok.IsArray());
  EXPECT_EQ(not_ok.GetSize(), 2);
  EXPECT_EQ(not_ok[0]["domain"]["name"].As<std::string>(), "domain_1");
  EXPECT_EQ(not_ok[0]["domain"]["dorblu_object"].As<std::string>(),
            "dorblu_object_1");
  EXPECT_EQ(not_ok[0]["domain"]["description_info"]["priority"].As<double>(),
            20.0);
  EXPECT_EQ(
      not_ok[0]["domain"]["description_info"]["description"].As<std::string>(),
      "desc 2");
  EXPECT_EQ(not_ok[1]["domain"]["name"].As<std::string>(), "domain_2");
  EXPECT_EQ(not_ok[1]["domain"]["dorblu_object"].As<std::string>(),
            "dorblu_object_2");
  EXPECT_EQ(not_ok[1]["domain"]["description_info"]["priority"].As<double>(),
            30.0);
  EXPECT_EQ(
      not_ok[1]["domain"]["description_info"]["description"].As<std::string>(),
      "desc 3");
}

TEST(TestAggregator, TestBestStateAggregation) {
  formats::json::ValueBuilder builder;
  builder["id"] = "aggregator";
  builder["aggregator_type"] = "best_state_aggregator";
  builder["aggregation_key"] = "host";
  builder["add_not_ok_to_meta"] = false;
  builder["skip_no_data"] = true;
  auto ag =
      std::make_shared<BestStateAggregatorByMetaKey>(builder.ExtractValue());

  auto entry = std::make_shared<StateEntryPoint>("");
  entry->OnStateOut(ag);
  auto out = std::make_shared<StateBuffer>("");
  ag->OnStateOut(out);

  formats::json::ValueBuilder meta_builder;
  meta_builder["host"] = "host_1";
  entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(), State::kWarn);
  EXPECT_EQ(out->LastState(), State::kWarn);
  meta_builder["host"] = "host_2";
  entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(), State::kOk);
  meta_builder["host"] = "host_3";
  entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(),
                 State::kNoData);
  EXPECT_EQ(out->LastState(), State::kOk);
}

TEST(TestAggregator, TestBestStateAggregationMinimumKeys) {
  formats::json::ValueBuilder builder;
  builder["id"] = "aggregator";
  builder["aggregator_type"] = "best_state_aggregator";
  builder["aggregation_key"] = "host";
  builder["add_not_ok_to_meta"] = false;
  builder["skip_no_data"] = true;
  builder["minimum_keys_to_start"] = 2;
  auto ag =
      std::make_shared<BestStateAggregatorByMetaKey>(builder.ExtractValue());

  auto entry = std::make_shared<StateEntryPoint>("");
  entry->OnStateOut(ag);
  auto out = std::make_shared<StateBuffer>("");
  ag->OnStateOut(out);

  formats::json::ValueBuilder meta_builder;
  meta_builder["host"] = "host_1";
  entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(), State::kOk);
  EXPECT_EQ(out->LastState(), State::kNoData);
  entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(), State::kWarn);
  EXPECT_EQ(out->LastState(), State::kNoData);
  meta_builder["host"] = "host_2";
  entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(), State::kOk);
  EXPECT_EQ(out->LastState(), State::kOk);
  meta_builder["host"] = "host_3";
  entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(),
                 State::kNoData);
  EXPECT_EQ(out->LastState(), State::kOk);
}

TEST(TestAggregator, TestWorstStateAggregationMeta) {
  formats::json::ValueBuilder builder;
  builder["id"] = "test_aggregator";
  builder["aggregator_type"] = "worst_state_aggregator";
  builder["aggregation_key"] = "host";
  builder["add_not_ok_to_meta"] = true;
  builder["save_not_ok_to_db"] = true;
  builder["skip_no_data"] = false;
  auto ag =
      std::make_shared<WorstStateAggregatorByMetaKey>(builder.ExtractValue());

  auto entry = std::make_shared<StateEntryPoint>("");
  entry->OnStateOut(ag);
  auto out = std::make_shared<StateBuffer>("");
  ag->OnStateOut(out);

  formats::json::ValueBuilder meta_builder;
  meta_builder["host"] = "host_1";
  entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(), State::kOk);
  meta_builder["host"] = "host_2";
  entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(),
                 State::kCritical);
  meta_builder["host"] = "host_3";
  entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(), State::kWarn);
  EXPECT_EQ(out->LastState(), State::kCritical);
  const auto& meta = out->LastMeta();
  auto meta_data = meta.Get(MetaDataKind::kCircuitStateData);

  std::string expected_meta =
      "{\"host\":\"host_1\",\"aggregation\":{\"test_aggregator\":"
      "{\"aggregator_type\":\"worst_state_aggregator\",\"aggregation_key\":"
      "\"host\",\"not_ok\":[{\"host\":\"host_2\",\"state\":\"Critical\"},"
      "{\"host\":\"host_3\",\"state\":\"Warning\"}]}}}";
  EXPECT_EQ(expected_meta, formats::json::ToString(meta_data));
}

TEST(TestAggregator, TestTwoLevelAggregation) {
  formats::json::ValueBuilder builder;
  formats::json::ValueBuilder meta_builder;

  builder["id"] = "cpu_aggregator";
  builder["aggregator_type"] = "worst_state_aggregator";
  builder["aggregation_key"] = "host_name";
  builder["add_not_ok_to_meta"] = true;
  builder["save_not_ok_to_db"] = true;
  builder["skip_no_data"] = false;
  meta_builder["check_type"] = "cpu";
  builder["additional_meta"] = meta_builder.ExtractValue();
  auto cpu_ag =
      std::make_shared<WorstStateAggregatorByMetaKey>(builder.ExtractValue());

  builder["id"] = "timings_aggregator";
  builder["aggregator_type"] = "worst_state_aggregator";
  builder["aggregation_key"] = "timings_type";
  builder["add_not_ok_to_meta"] = true;
  builder["save_not_ok_to_db"] = true;
  builder["skip_no_data"] = false;
  meta_builder["check_type"] = "timings";
  builder["additional_meta"] = meta_builder.ExtractValue();
  auto timings_ag =
      std::make_shared<WorstStateAggregatorByMetaKey>(builder.ExtractValue());

  builder["id"] = "cpu_timings_aggregator";
  builder["aggregator_type"] = "best_state_aggregator";
  builder["aggregation_key"] = "check_type";
  builder["add_not_ok_to_meta"] = true;
  builder["save_not_ok_to_db"] = true;
  builder["skip_no_data"] = false;
  auto cpu_timings_ag =
      std::make_shared<BestStateAggregatorByMetaKey>(builder.ExtractValue());

  auto cpu_entry = std::make_shared<StateEntryPoint>("");
  cpu_entry->OnStateOut(cpu_ag);
  cpu_ag->OnStateOut(cpu_timings_ag);
  auto timings_entry = std::make_shared<StateEntryPoint>("");
  timings_entry->OnStateOut(timings_ag);
  timings_ag->OnStateOut(cpu_timings_ag);
  auto out = std::make_shared<StateBuffer>("");
  cpu_timings_ag->OnStateOut(out);

  {
    formats::json::ValueBuilder entry_meta_builder;
    meta_builder["host_name"] = "host_1";
    cpu_entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(),
                       State::kOk);
    meta_builder["host_name"] = "host_2";
    cpu_entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(),
                       State::kCritical);
    meta_builder["host_name"] = "host_3";
    cpu_entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(),
                       State::kWarn);
  }

  {
    formats::json::ValueBuilder entry_meta_builder;
    meta_builder["timings_type"] = "timing_1";
    timings_entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(),
                           State::kOk);
    meta_builder["timings_type"] = "timing_2";
    timings_entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(),
                           State::kError);
    meta_builder["timings_type"] = "timing_3";
    timings_entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(),
                           State::kWarn);
  }

  EXPECT_EQ(out->LastState(), State::kError);
  const auto& meta = out->LastMeta();
  auto meta_data = meta.Get(MetaDataKind::kCircuitStateData);

  std::string expected_meta =
      "{\"host_name\":\"host_1\",\"aggregation\":{\"cpu_aggregator\":{"
      "\"aggregator_type\":\"worst_state_aggregator\",\"aggregation_key\":"
      "\"host_name\",\"not_ok\":[{\"host_name\":\"host_2\",\"state\":"
      "\"Critical\"},{\"host_name\":\"host_3\",\"state\":\"Warning\"}]},"
      "\"timings_aggregator\":{\"aggregator_type\":\"worst_state_aggregator\","
      "\"aggregation_key\":\"timings_type\",\"not_ok\":[{\"timings_type\":"
      "\"timing_2\",\"state\":\"Error\"},{\"timings_type\":\"timing_3\","
      "\"state\":\"Warning\"}]},\"cpu_timings_aggregator\":{\"aggregator_"
      "type\":\"best_state_aggregator\",\"aggregation_key\":\"check_type\","
      "\"not_ok\":[{\"check_type\":\"cpu\",\"state\":\"Critical\"},{\"check_"
      "type\":\"timings\",\"state\":\"Error\"}]}}}";

  EXPECT_EQ(expected_meta, formats::json::ToString(meta_data));
}

TEST(TestAggregator, TestAggregationMetaFormatterString) {
  formats::json::ValueBuilder builder;
  builder["id"] = "meta_formatter";
  builder["aggregation_object_type"] = "string";
  builder["meta_keys"].PushBack("keys_1");
  builder["aggregator_id"] = "aggregator_id_1";
  auto ag = std::make_shared<AggregationMetaFormatter>(builder.ExtractValue());

  auto entry = std::make_shared<StateEntryPoint>("");
  entry->OnStateOut(ag);
  auto out = std::make_shared<StateBuffer>("");
  ag->OnStateOut(out);

  formats::json::ValueBuilder meta_builder;
  formats::json::ValueBuilder not_ok;
  meta_builder["aggregation"]["aggregator_id_1"]["aggregation_key"] = "host";
  not_ok["host"] = "host1";
  meta_builder["aggregation"]["aggregator_id_1"]["not_ok"].PushBack(
      not_ok.ExtractValue());
  not_ok["host"] = "host2";
  meta_builder["aggregation"]["aggregator_id_1"]["not_ok"].PushBack(
      not_ok.ExtractValue());
  not_ok["host"] = "host3";
  meta_builder["aggregation"]["aggregator_id_1"]["not_ok"].PushBack(
      not_ok.ExtractValue());
  entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(), State::kOk);
  EXPECT_TRUE(out->LastMeta().Has("keys_1"));
  EXPECT_TRUE(out->LastMeta().Get("keys_1").IsArray());
  EXPECT_EQ(out->LastMeta().Get("keys_1")[0].As<std::string>(), "host1");
  EXPECT_EQ(out->LastMeta().Get("keys_1")[1].As<std::string>(), "host2");
  EXPECT_EQ(out->LastMeta().Get("keys_1")[2].As<std::string>(), "host3");
}

TEST(TestAggregator, TestAggregationMetaFormatterObject) {
  formats::json::ValueBuilder builder;
  builder["id"] = "meta_formatter";
  builder["aggregation_object_type"] = "object";
  builder["meta_keys"].PushBack("domains_list");
  builder["meta_keys"].PushBack("dorblu_objects_list");
  builder["meta_keys"].PushBack("descriptions_list");
  builder["keys_in_aggregator_object"].PushBack("name");
  builder["keys_in_aggregator_object"].PushBack("dorblu_object");
  builder["keys_in_aggregator_object"].PushBack("description_info");
  builder["aggregator_id"] = "domains_aggregator";
  auto ag = std::make_shared<AggregationMetaFormatter>(builder.ExtractValue());

  auto entry = std::make_shared<StateEntryPoint>("");
  entry->OnStateOut(ag);
  auto out = std::make_shared<StateBuffer>("");
  ag->OnStateOut(out);

  formats::json::ValueBuilder meta_builder;
  formats::json::ValueBuilder not_ok;
  meta_builder["aggregation"]["domains_aggregator"]["aggregation_key"] =
      "domain";
  not_ok["domain"]["name"] = "domain_1";
  not_ok["domain"]["dorblu_object"] = "object_1";
  not_ok["domain"]["description_info"]["priority"] = 1.0;
  not_ok["domain"]["description_info"]["description"] = "desc 1";
  meta_builder["aggregation"]["domains_aggregator"]["not_ok"].PushBack(
      not_ok.ExtractValue());
  not_ok["domain"]["name"] = "domain_2";
  not_ok["domain"]["dorblu_object"] = "object_2";
  not_ok["domain"]["description_info"]["priority"] = 2.0;
  not_ok["domain"]["description_info"]["description"] = "desc 2";
  meta_builder["aggregation"]["domains_aggregator"]["not_ok"].PushBack(
      not_ok.ExtractValue());
  not_ok["domain"]["name"] = "domain_3";
  not_ok["domain"]["dorblu_object"] = "object_3";
  not_ok["domain"]["description_info"]["priority"] = 3.0;
  not_ok["domain"]["description_info"]["description"] = "desc 3";
  meta_builder["aggregation"]["domains_aggregator"]["not_ok"].PushBack(
      not_ok.ExtractValue());
  entry->StateIn(Meta(meta_builder.ExtractValue()), time::Now(), State::kOk);
  EXPECT_TRUE(out->LastMeta().Has("domains_list"));
  EXPECT_TRUE(out->LastMeta().Get("domains_list").IsArray());
  EXPECT_EQ(out->LastMeta().Get("domains_list")[0].As<std::string>(),
            "domain_1");
  EXPECT_EQ(out->LastMeta().Get("domains_list")[1].As<std::string>(),
            "domain_2");
  EXPECT_EQ(out->LastMeta().Get("domains_list")[2].As<std::string>(),
            "domain_3");
  EXPECT_TRUE(out->LastMeta().Has("dorblu_objects_list"));
  EXPECT_TRUE(out->LastMeta().Get("dorblu_objects_list").IsArray());
  EXPECT_EQ(out->LastMeta().Get("dorblu_objects_list")[0].As<std::string>(),
            "object_1");
  EXPECT_EQ(out->LastMeta().Get("dorblu_objects_list")[1].As<std::string>(),
            "object_2");
  EXPECT_EQ(out->LastMeta().Get("dorblu_objects_list")[2].As<std::string>(),
            "object_3");
  EXPECT_TRUE(out->LastMeta().Has("descriptions_list"));
  EXPECT_TRUE(out->LastMeta().Get("descriptions_list").IsArray());
  EXPECT_EQ(
      out->LastMeta().Get("descriptions_list")[0]["priority"].As<double>(),
      1.0);
  EXPECT_EQ(out->LastMeta()
                .Get("descriptions_list")[0]["description"]
                .As<std::string>(),
            "desc 1");
  EXPECT_EQ(
      out->LastMeta().Get("descriptions_list")[1]["priority"].As<double>(),
      2.0);
  EXPECT_EQ(out->LastMeta()
                .Get("descriptions_list")[1]["description"]
                .As<std::string>(),
            "desc 2");
  EXPECT_EQ(
      out->LastMeta().Get("descriptions_list")[2]["priority"].As<double>(),
      3.0);
  EXPECT_EQ(out->LastMeta()
                .Get("descriptions_list")[2]["description"]
                .As<std::string>(),
            "desc 3");
}

}  // namespace hejmdal::radio::blocks
