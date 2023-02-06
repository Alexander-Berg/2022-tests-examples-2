#include <gtest/gtest.h>

#include <models/time_series.hpp>
#include <radio/blocks/utils/buffer_sample.hpp>
#include <radio/circuit.hpp>
#include <radio/spec/connector.hpp>

namespace hejmdal::radio {

namespace {

formats::json::Value simple_schema = [] {
  std::string schema_str{
      "{\n"
      "  \"blocks\": [],\n"
      "  \"entry_points\": [\n"
      "    {\n"
      "      \"id\": \"entry_data\",\n"
      "      \"type\": \"data_entry_point\"\n"
      "    }\n"
      "  ],\n"
      "  \"out_points\": [\n"
      "    {\n"
      "      \"id\": \"out_data\",\n"
      "      \"type\": \"data_out_point\",\n"
      "      \"debug\": [\"data\"]\n"
      "    }\n"
      "  ],\n"
      "  \"name\": \"test_schema\","
      "  \"wires\": [\n"
      "    {\n"
      "      \"from\": \"entry_data\",\n"
      "      \"to\": \"out_data\",\n"
      "      \"type\": \"data\"\n"
      "    }\n"
      "  ]\n"
      "}"};
  return formats::json::FromString(schema_str);
}();

}

TEST(TestConnector, MainTest) {
  CircuitsContainer circuits;

  circuits["circuit_1"] = Circuit::Build("circuit_1", simple_schema);
  circuits["circuit_2"] = Circuit::Build("circuit_2", simple_schema);
  auto buffers = circuits["circuit_2"]->CreateDebugBuffers(10);
  ASSERT_EQ(buffers.size(), 1u);
  auto& out_buffer = buffers.front();

  spec::Connector connector{"circuit_1", "out_data", "circuit_2", "entry_data",
                            spec::Connector::kData};
  connector.Connect(circuits);

  auto now = time::Now();

  circuits["circuit_1"]->GetEntryPoint("entry_data").DataIn(now, 6.66);
  auto ts_map = out_buffer->ExtractTimeSeries();
  ASSERT_EQ(ts_map.size(), 1u);
  auto& ts = ts_map.at("out_data_data");
  ASSERT_EQ(ts.size(), 1u);
  for (const auto& time_val : ts) {
    ASSERT_EQ(time_val.GetTime(), now);
    ASSERT_EQ(time_val.GetValue(), 6.66);
  }
}

TEST(TestConnector, TestConnectCircuitToItself) {
  ASSERT_THROW(spec::Connector("circuit_1", "out", "circuit_1", "in",
                               spec::Connector::kState),
               except::Error);
}

}  // namespace hejmdal::radio
