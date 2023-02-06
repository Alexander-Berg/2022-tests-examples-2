#include <gtest/gtest.h>

#include "testutils.hpp"

#include <iostream>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/parse/common_containers.hpp>
#include <userver/fs/blocking/write.hpp>
#include <userver/logging/log.hpp>

#include "file_export_mapper.hpp"

namespace hejmdal::testutils {

static Alert::Type ParseAlertType(const std::string& type) {
  if (type == "strict") {
    return Alert::kStrict;
  } else if (type == "possible") {
    return Alert::kPossible;
  }
  throw except::Error("Unknown alert type: {}", type);
}

Alert ParseAlert(const formats::json::Value& json) {
  return Alert{
      time::TimeRange(time::From<time::Milliseconds>(json["start"].As<long>()),
                      time::From<time::Milliseconds>(json["end"].As<long>())),
      radio::blocks::State::FromString(json["status"].As<std::string>())
          .GetStateValue(),
      ParseAlertType(json["type"].As<std::string>())};
}

std::string ToString(Alert::Type type) {
  switch (type) {
    case Alert::Type::kNone:
      return "";
    case Alert::Type::kStrict:
      return "strict";
    case Alert::Type::kPossible:
      return "possible";
  }
}

void CheckAlerts(const std::vector<Alert>& required_alerts,
                 const std::vector<Alert>& local_alerts) {
  // Check if every local alert has match with required alerts
  for (const auto& local_alert : local_alerts) {
    bool checked = false;
    for (const auto& required_alert : required_alerts) {
      if (required_alert.range.Contains(local_alert.range) &&
          required_alert.status == local_alert.status) {
        checked = true;
        break;
      }
    }
    EXPECT_EQ(checked, true);
  }
  // Check if every strictly required alert has match with some local alert
  for (const auto& reuqired_alert : required_alerts) {
    if (reuqired_alert.type == Alert::kPossible) continue;
    bool checked = false;
    for (const auto& local_alert : local_alerts) {
      if (local_alert.range.IntersectsWith(reuqired_alert.range) &&
          reuqired_alert.status == local_alert.status) {
        checked = true;
        break;
      }
    }
    EXPECT_EQ(checked, true);
  }
}

models::TimeSeriesView BuildView(std::vector<double> points) {
  return BuildView(points.begin(), points.end());
}

models::TimeSeriesView BuildView(std::vector<double>::const_iterator begin,
                                 std::vector<double>::const_iterator end) {
  time::TimePoint start_ts;
  models::TimeSeries values;
  std::size_t i = 0;
  for (auto iter = begin; iter != end; ++iter, ++i) {
    values.Push({start_ts + time::Minutes(i), *iter});
  }
  return models::TimeSeriesView{values};
}

std::vector<double> ViewToVector(const models::TimeSeriesView& view) {
  std::vector<double> res;
  for (const auto& val : view) {
    res.push_back(val.GetValue());
  }
  return res;
}

std::vector<std::string> ViewsToFiles(
    const std::vector<models::TimeSeriesView>& views, const std::string& name,
    const std::string& dir) {
  std::vector<std::string> filenames;
  std::size_t i = 0;
  for (auto& view : views) {
    filenames.emplace_back(dir + "/timeseries_" + name + "_" +
                           std::to_string(i++) + ".json");
    fs::blocking::RemoveSingleFile(filenames.back());

    mappers::FileExportMapper(filenames.back(), name).Apply(view);
  }
  return filenames;
}

void Plot(const std::vector<std::string>& files) {
  static const std::string py_plotter = kTestToolsDir + "/local_plotter.py";
  std::string command("python3 " + py_plotter);
  for (const auto& file : files) {
    command += " --file " + file;
  }
  auto sys_result = system(command.c_str());
  if (sys_result != 0) {
    LOG_WARNING() << "python3 plotter failed";
  }
}

void RemoveFiles(const std::vector<std::string>& files) {
  for (const auto& file : files) {
    fs::blocking::RemoveSingleFile(file);
  }
}

void Print(const std::vector<double>& vector) {
  for (const auto& elem : vector) {
    std::cout << std::to_string(elem) << ", ";
  }
  std::cout << std::endl;
}

void Print(const models::TimeSeriesView& view) {
  for (const auto& elem : view) {
    std::cout << std::to_string(elem.GetValue()) << ", ";
  }
  std::cout << std::endl;
}

std::chrono::system_clock::time_point MockTime(std::time_t value) {
  return std::chrono::system_clock::from_time_t(value);
}

std::vector<models::TimeData<double>> LoadJsonTS(
    const formats::json::Value& json) {
  std::vector<models::TimeData<double>> result;
  auto values = json["values"].As<std::vector<double>>();
  auto timestamps = json["timestamps"].As<std::vector<std::int64_t>>();
  for (size_t i = 0; i < values.size(); ++i) {
    result.push_back(models::TimeData<double>(
        time::TimePoint(time::Milliseconds(timestamps[i])), values[i]));
  }
  return result;
}

radio::CircuitPtr BuildCircuit(const std::string& filename) {
  formats::json::Value schema = formats::json::blocking::FromFile(
      testutils::kCircuitsDir + "/" + filename);
  return radio::Circuit::Build("id", schema);
}

}  // namespace hejmdal::testutils
