#include <string>
#include <string_view>

#include <experiments3/models/impl/cache_manager_base.hpp>
#include <experiments3/models/runtime_info_sender.hpp>

namespace experiments3::impl::test_utils {

class CacheManagerHelper {
 public:
  explicit CacheManagerHelper(std::string files_dir)
      : files_dir_(std::move(files_dir)) {}

  void UpdateCacheFromFile(
      experiments3::models::CacheManagerBase& cache_manager,
      const std::string& consumer, std::string_view file_name,
      experiments3::models::ExperimentType type);

  void UpdateCacheFromJson(
      experiments3::models::CacheManagerBase& cache_manager,
      const std::string& consumer, experiments3::models::ExperimentType type,
      const formats::json::Value& value);

  void ClearStorage(experiments3::models::CacheManagerBase& cache_manager);

 private:
  std::string files_dir_;
};

}  // namespace experiments3::impl::test_utils
