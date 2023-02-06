#pragma once

#include <experiments3/models/impl/cache_manager_base.hpp>

namespace experiments3::models {

class CacheManager final: public CacheManagerBase {
 public:
  // Good methods
  using CacheManagerBase::GetValue;
  // Bulk get methods
  using CacheManagerBase::GetConfigsData;
  using CacheManagerBase::GetConfigsMappedData;
  using CacheManagerBase::GetExperimentsData;
  using CacheManagerBase::GetExperimentsMappedData;
};

}  // namespace experiments3::models
