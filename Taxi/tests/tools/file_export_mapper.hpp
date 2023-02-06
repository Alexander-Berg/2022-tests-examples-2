#include <string>

#include <models/time_series_view.hpp>

namespace hejmdal::mappers {

class FileExportMapper {
 public:
  explicit FileExportMapper(std::string file_name, std::string plot_name);

  void Apply(const models::TimeSeriesView& input) const;

 private:
  const std::string file_name_;
  const std::string plot_name_;
};

}  // namespace hejmdal::mappers
