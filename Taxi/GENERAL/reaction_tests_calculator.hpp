#pragma once

#include <components/mongo_collections.hpp>
#include <models/api_over_data/driver_info.hpp>
#include <models/driver_experiments.hpp>
#include <models/park_dbids.hpp>
#include <models/reaction_tests.hpp>
#include <models/status_history.hpp>
#include <workers/base_allow_parallel.hpp>
#include "caches/drivers_cache.hpp"
#include "caches/parks_cache.hpp"
#include "caches/unique_drivers_cache.hpp"

namespace workers {

class ReactionTestsCalculator
    : public BaseAllowParallel,
      public components::NamedComponentMixIn<ReactionTestsCalculator> {
 public:
  using BaseAllowParallel::BaseAllowParallel;
  static constexpr const char* const name = "reaction-tests-calculator";

  void onLoad() override;
  void onUnload() override;

  void Run(const utils::AsyncStatus& status, ::handlers::Context& context,
           TimeStorage& ts) const override;

 private:
  static const uint32_t kPeriodMs = 300000;
  static const uint32_t kLockTimeoutMs = 300000;
  static const uint32_t kLockProlongMs = 2000;

  components::MongoCollections::CPtr collections_;
  const utils::DataProvider<models::Parks>* parks_cache_ = nullptr;
  const utils::DataProvider<experiments::DriverExperiments>*
      driver_experiments_ = nullptr;
  const utils::DataProvider<models::Drivers>* drivers_cache_ = nullptr;
  const utils::DataProvider<models::UniqueDrivers>* unique_drivers_cache_ =
      nullptr;
  const utils::DataProvider<models::StatusHistoryIndex>* status_history_cache_ =
      nullptr;
  const utils::DataProvider<api_over_data::models::labor::DriverInfo>*
      driver_info_ = nullptr;
};

}  // namespace workers
