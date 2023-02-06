#pragma once

#include <map>
#include <string>
#include <vector>

#include <models/time_series_view.hpp>

namespace hejmdal::testutils {

class Plotter {
 public:
  void Plot(const std::vector<models::TimeSeriesView>& views,
            const std::string& name) const;

  void Plot(const models::TimeSeriesView& view, const std::string& name) const;

  void Plot(const std::initializer_list<models::SensorValue>& values,
            const std::string& name) const;

  void Plot(const std::map<std::string, models::TimeSeries>& vs_map) const;

  ~Plotter();

 private:
  mutable std::vector<std::string> files_ = {};
};

}  // namespace hejmdal::testutils
