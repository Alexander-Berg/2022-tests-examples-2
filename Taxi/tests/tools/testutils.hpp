#pragma once

#include <optional>

#include <testing/source_path.hpp>
#include <userver/formats/json/value.hpp>

#include <models/time_series.hpp>
#include <models/time_series_view.hpp>
#include <radio/blocks/commutation/output_consumer.hpp>
#include <radio/blocks/utils/buffer_sample.hpp>
#include <radio/blocks/utils/sample_buffers.hpp>
#include <radio/circuit.hpp>

namespace hejmdal::testutils {

constexpr bool kIsRelease = true;

inline const std::string kStasticDir =
    ::utils::CurrentSourcePath("tests/static");
inline const std::string kTestToolsDir =
    ::utils::CurrentSourcePath("test-tools");
inline const std::string kCircuitsDir =
    ::utils::CurrentSourcePath("src/radio/circuits");

class TestOutputConsumer : public radio::blocks::OutputConsumer {
 public:
  TestOutputConsumer()
      : radio::blocks::OutputConsumer("test_buffer"), buffer(1000, "tb") {
    OnStateOut(&buffer);
  }

  formats::json::Value Serialize() const override { return buffer.Serialize(); }
  const std::string& GetType() const override { return buffer.GetType(); }

  void StateIn(const radio::blocks::Meta& meta, const time::TimePoint& tp,
               const radio::blocks::State& state) override {
    PushStateOut(meta, tp, state);
  }

  radio::blocks::StateBufferSample buffer;
};

struct Alert {
  enum Type { kNone, kStrict, kPossible };
  time::TimeRange range;
  radio::blocks::State::Value status;
  Type type = kNone;
};

Alert ParseAlert(const formats::json::Value& json);
std::string ToString(Alert::Type type);

struct EntryPointData {
  std::string entry_point_id;
  models::TimeSeriesView timeseries;
};
struct TestCircuitData {
  std::map<std::string, models::TimeSeriesView> data;
  std::vector<Alert> alerts;
};

void CheckAlerts(const std::vector<Alert>& required_alerts,
                 const std::vector<Alert>& local_alerts);

models::TimeSeriesView BuildView(std::vector<double> points);
models::TimeSeriesView BuildView(std::vector<double>::const_iterator begin,
                                 std::vector<double>::const_iterator end);

std::vector<double> ViewToVector(const models::TimeSeriesView& view);

void Plot(const std::vector<std::string>& files);

std::vector<std::string> ViewsToFiles(
    const std::vector<models::TimeSeriesView>& views, const std::string& name,
    const std::string& dir = "/tmp");

void RemoveFiles(const std::vector<std::string>& files);

void Print(const std::vector<double>& vector);

void Print(const models::TimeSeriesView& view);

std::chrono::system_clock::time_point MockTime(std::time_t value);

std::vector<models::TimeData<double>> LoadJsonTS(
    const formats::json::Value& json);

radio::CircuitPtr BuildCircuit(const std::string& filename);

}  // namespace hejmdal::testutils
