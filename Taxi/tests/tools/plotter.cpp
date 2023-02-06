#include "plotter.hpp"

#include "testutils.hpp"

namespace hejmdal::testutils {

void Plotter::Plot(const std::vector<models::TimeSeriesView>& views,
                   const std::string& name) const {
  auto tmp_files = testutils::ViewsToFiles(views, name);
  files_.insert(files_.end(), tmp_files.begin(), tmp_files.end());
}

void Plotter::Plot(const models::TimeSeriesView& view,
                   const std::string& name) const {
  Plot(std::vector<models::TimeSeriesView>{view}, name);
}

void Plotter::Plot(const std::initializer_list<models::SensorValue>& values,
                   const std::string& name) const {
  Plot(models::TimeSeriesView(values), name);
}

void Plotter::Plot(
    const std::map<std::string, models::TimeSeries>& ts_map) const {
  for (const auto& [name, series] : ts_map) {
    Plot(models::TimeSeriesView(series), name);
  }
}

Plotter::~Plotter() {
  testutils::Plot(files_);
  testutils::RemoveFiles(files_);
}

}  // namespace hejmdal::testutils
