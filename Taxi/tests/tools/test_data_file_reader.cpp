#include "test_data_file_reader.hpp"

#include <models/sensor_value.hpp>
#include <userver/formats/json/serialize.hpp>

#include <models/time_series_view.hpp>
#include <utils/except.hpp>
#include <utils/time.hpp>

namespace hejmdal::testutils {

template <typename TDuration>
static models::TimeSeriesView ParseTimeseries(
    const formats::json::Value& timestamps,
    const formats::json::Value& values) {
  if (timestamps.GetSize() != values.GetSize()) {
    throw except::Error("timestamps and values has different size");
  }
  size_t size = timestamps.GetSize();
  std::vector<models::SensorValue> sensorValues;

  for (size_t i = 0; i < size; ++i) {
    if (values[i].IsNull()) continue;
    sensorValues.emplace_back(time::From<TDuration>(timestamps[i].As<long>()),
                              values[i].As<double>());
  }

  return models::TimeSeriesView(std::move(sensorValues));
}

static EntryPointData ParseEntryPointData(const formats::json::Value& json) {
  EntryPointData result;
  if (json.HasMember("timeseries")) {
    // Solomon
    const formats::json::Value& timeseries = json["timeseries"];
    result.entry_point_id = timeseries["labels"]["sensor"].As<std::string>();

    result.timeseries = ParseTimeseries<time::Milliseconds>(
        timeseries["timestamps"], timeseries["values"]);
  } else if (json.HasMember("timeline")) {
    // Yasm
    const auto& timeline = json["timeline"];
    for (const auto& values : json["values"]) {
      result.entry_point_id = values["id"].As<std::string>();
      result.timeseries =
          ParseTimeseries<time::Seconds>(timeline, values["data"]);
    }
  }
  return result;
}

TestDataFileReader::TestDataFileReader(const std::string& file_path)
    : file_path_(file_path) {}

TestCircuitData TestDataFileReader::GetTestCircuitData() const {
  formats::json::Value json = formats::json::blocking::FromFile(file_path_);
  TestCircuitData result;
  if (json.HasMember("vector")) {
    for (const auto& timeseries : json["vector"]) {
      auto entry_data = ParseEntryPointData(timeseries);
      result.data[entry_data.entry_point_id] = entry_data.timeseries;
    }
  } else {
    auto entry_data = ParseEntryPointData(json);
    result.data[entry_data.entry_point_id] = entry_data.timeseries;
  }
  result.alerts = GetAlerts();
  return result;
}

std::vector<models::TimeSeriesView> TestDataFileReader::GetTimeSeries() const {
  formats::json::Value json = formats::json::blocking::FromFile(file_path_);
  std::vector<models::TimeSeriesView> results;
  if (json.HasMember("vector")) {
    for (const auto& data : json["vector"]) {
      const auto& timeseries = data["timeseries"];
      results.push_back(ParseTimeseries<time::Milliseconds>(
          timeseries["timestamps"], timeseries["values"]));
    }
  } else if (json.HasMember("timeseries")) {
    const auto& timeseries = json["timeseries"];
    results.push_back(ParseTimeseries<time::Milliseconds>(
        timeseries["timestamps"], timeseries["values"]));
  } else if (json.HasMember("timeline")) {
    const auto& timeline = json["timeline"];
    for (const auto& values : json["values"]) {
      results.push_back(
          ParseTimeseries<time::Seconds>(timeline, values["data"]));
    }
  }
  return results;
}

std::vector<Alert> TestDataFileReader::GetAlerts() const {
  std::vector<Alert> result;
  auto json = formats::json::blocking::FromFile(file_path_);
  if (json.HasMember("alerts")) {
    for (const auto& alert_json : json["alerts"]) {
      result.push_back(ParseAlert(alert_json));
    }
  }
  return result;
}

}  // namespace hejmdal::testutils
