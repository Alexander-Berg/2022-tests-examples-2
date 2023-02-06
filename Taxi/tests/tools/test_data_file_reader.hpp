#pragma once

#include <utils/time.hpp>

#include "testutils.hpp"

namespace hejmdal::testutils {

class TestDataFileReader {
 public:
  explicit TestDataFileReader(const std::string& file_path);

  [[nodiscard]] TestCircuitData GetTestCircuitData() const;
  [[nodiscard]] std::vector<models::TimeSeriesView> GetTimeSeries() const;
  [[nodiscard]] std::vector<Alert> GetAlerts() const;

 private:
  std::string file_path_;
};

}  // namespace hejmdal::testutils
