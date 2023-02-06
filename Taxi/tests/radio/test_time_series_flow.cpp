#include <gtest/gtest.h>

#include <userver/formats/json.hpp>
#include <userver/formats/serialize/common_containers.hpp>

#include <radio/blocks/utils/sample_buffers.hpp>
#include <radio/circuit.hpp>
#include <radio/selectors/time_series_selector.hpp>
#include <radio/time_series_flow.hpp>

namespace hejmdal::radio {

namespace {

class MockTsGetter : public selectors::TimeSeriesGetter {
 public:
  MockTsGetter(const models::TimeSeries& ts) : ts_(ts) {}

  const models::TimeSeriesView& GetTimeSeries() const override { return ts_; }
  time::TimePoint GetReceivedAt() const override { return time::TimePoint{}; }

 private:
  models::TimeSeriesView ts_;
};

formats::json::Value CreateSchema() {
  formats::json::ValueBuilder json;
  json["out_points"] =
      formats::json::ValueBuilder(formats::common::Type::kArray);
  json["entry_points"] =
      formats::json::ValueBuilder(formats::common::Type::kArray);
  json["wires"] = formats::json::ValueBuilder(formats::common::Type::kArray);
  json["blocks"] = formats::json::ValueBuilder(formats::common::Type::kArray);
  json["name"] = "test circuit";

  formats::json::ValueBuilder entry;
  entry["id"] = "test_entry";
  entry["type"] = "data_entry_point";
  entry["debug"] = std::vector<std::string>{"data"};
  json["entry_points"].PushBack(std::move(entry));

  formats::json::ValueBuilder out;
  out["id"] = "test_out";
  out["type"] = "data_out_point";
  json["out_points"].PushBack(std::move(out));

  formats::json::ValueBuilder wire;
  wire["from"] = "test_entry";
  wire["to"] = "test_out";
  wire["type"] = "data";
  json["wires"].PushBack(std::move(wire));

  return json.ExtractValue();
}

auto min = time::Minutes{1};
auto sec = time::Seconds{1};

}  // namespace

TEST(TestTimeSeriesFlow, MainTest) {
  auto now = time::Now();

  auto schema = CreateSchema();

  auto circuit = Circuit::Build("test_circuit", schema);
  auto debug_buffers = circuit->CreateDebugBuffers(20);
  EXPECT_EQ(debug_buffers.size(), 1u);

  auto entry = circuit->GetEntryPoint("test_entry");

  std::vector<PreparedFlow> prepared_flows;
  {
    models::TimeSeries ts;
    ts.Push(models::SensorValue(now + 0 * min, 0.));
    ts.Push(models::SensorValue(now + 1 * min, 1.));
    ts.Push(models::SensorValue(now + 3 * min, 3.));
    ts.Push(models::SensorValue(now + 4 * min, 4.));
    prepared_flows.emplace_back(
        PreparedFlow{std::make_unique<MockTsGetter>(ts), entry});
  }
  {
    models::TimeSeries ts;
    ts.Push(models::SensorValue(now + 1 * min, 1.));
    ts.Push(models::SensorValue(now + 2 * min, 2.));
    ts.Push(models::SensorValue(now + 4 * min, 4.));
    ts.Push(models::SensorValue(now + 6 * min, 6.));
    ts.Push(models::SensorValue(now + 7 * min, 7.));
    prepared_flows.emplace_back(
        PreparedFlow{std::make_unique<MockTsGetter>(ts), entry});
  }
  {
    models::TimeSeries ts;
    ts.Push(models::SensorValue(now + 90 * sec, 1.5));
    ts.Push(models::SensorValue(now + 150 * sec, 2.5));
    ts.Push(models::SensorValue(now + 180 * sec, 3.0));
    ts.Push(models::SensorValue(now + 210 * sec, 3.5));
    ts.Push(models::SensorValue(now + 246 * sec, 4.1));
    prepared_flows.emplace_back(
        PreparedFlow{std::make_unique<MockTsGetter>(ts), entry});
  }
  {
    models::TimeSeries ts;
    prepared_flows.emplace_back(
        PreparedFlow{std::make_unique<MockTsGetter>(ts), entry});
  }

  PreparedFlowGroup group(std::move(prepared_flows), nullptr, {});
  group.TransmitData();

  auto ts_map = debug_buffers.front()->ExtractTimeSeries();
  EXPECT_EQ(ts_map.size(), 1u);
  auto& ts = ts_map.at("test_entry_data");
  std::optional<models::SensorValue> prev;
  for (const auto& val : ts) {
    if (!prev.has_value()) {
      prev = val;
    } else {
      EXPECT_TRUE(val.GetValue() >= prev->GetValue());
      EXPECT_TRUE(val.GetTime() >= prev->GetTime());
    }
  }
}

}  // namespace hejmdal::radio
