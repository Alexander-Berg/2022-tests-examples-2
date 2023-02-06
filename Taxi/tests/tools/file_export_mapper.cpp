#include "file_export_mapper.hpp"

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/fs/blocking/write.hpp>

#include <models/sensor_value.hpp>
#include <models/time_series_view.hpp>
#include <utils/time.hpp>

namespace hejmdal::mappers {

FileExportMapper::FileExportMapper(std::string file_name, std::string plot_name)
    : file_name_(file_name), plot_name_(plot_name) {}

void FileExportMapper::Apply(const models::TimeSeriesView& input) const {
  formats::json::ValueBuilder timestamps{formats::common::Type::kArray};
  formats::json::ValueBuilder values{formats::common::Type::kArray};

  for (const models::SensorValue& data : input) {
    long millis = time::To<time::Milliseconds>(data.GetTime());
    double value = data.GetValue();

    timestamps.PushBack(millis);
    values.PushBack(value);
  }

  formats::json::ValueBuilder timeseries;
  timeseries["alias"] = plot_name_;
  formats::json::ValueBuilder labels;
  labels["sensor"] = plot_name_;
  timeseries["labels"] = std::move(labels);
  timeseries["timestamps"] = std::move(timestamps);
  timeseries["values"] = std::move(values);

  formats::json::ValueBuilder result;
  result["timeseries"] = std::move(timeseries);

  fs::blocking::RemoveSingleFile(file_name_);
  fs::blocking::RewriteFileContents(
      file_name_, formats::json::ToString(result.ExtractValue()));
}

};  // namespace hejmdal::mappers
