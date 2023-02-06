#include <tests/utils.hpp>

#include <userver/logging/level.hpp>
#include <userver/logging/logger.hpp>

#include <experiments3/models/cache_manager_impl.hpp>
#include <experiments3/models/clients_cache_impl.hpp>
#include <experiments3/models/match_metrics_storage.hpp>

namespace experiments3::impl::test_utils {

void CacheManagerHelper::UpdateCacheFromFile(
    experiments3::models::CacheManagerBase& cache_manager,
    const std::string& consumer, std::string_view file_name,
    experiments3::models::ExperimentType type) {
  cache_manager->PrepareCache(consumer, type, "",
                              {{},
                               {},
                               std::make_shared<models::MatchMetricsStorage>(),
                               ::logging::DefaultLogger(),
                               false,  // is_matching_logs_enabled
                               ::logging::Level::kInfo,
                               engine::current_task::GetTaskProcessor()});
  auto updates =
      formats::json::blocking::FromFile(files_dir_ + file_name.data());
  auto root_name = ExperimentTypeToString(type) + "s";
  for (const auto& update : updates[root_name]) {
    cache_manager->UpdateEntry(consumer, type, update,
                               models::kMockFilesManager);
  }
}

void CacheManagerHelper::UpdateCacheFromJson(
    experiments3::models::CacheManagerBase& cache_manager,
    const std::string& consumer, experiments3::models::ExperimentType type,
    const formats::json::Value& value) {
  cache_manager->PrepareCache(consumer, type, "",
                              {{},
                               {},
                               std::make_shared<models::MatchMetricsStorage>(),
                               ::logging::DefaultLogger(),
                               false,  // is_matching_logs_enabled
                               ::logging::Level::kInfo,
                               engine::current_task::GetTaskProcessor()});

  cache_manager->UpdateEntry(consumer, type, value, models::kMockFilesManager);
}

void CacheManagerHelper::ClearStorage(
    experiments3::models::CacheManagerBase& cache_manager) {
  cache_manager->Clear();
}

}  // namespace experiments3::impl::test_utils
