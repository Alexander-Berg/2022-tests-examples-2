#pragma once

#include <cache/base.hpp>
#include <mongo/pool.hpp>
#include "models/reaction_tests.hpp"

namespace caches {
class ReactionTests : public PartiallyBase<models::ReactionTestsIndex> {
 public:
  static constexpr const char* kName = "ReactionTestsCache";

  ReactionTests(const utils::mongo::PoolPtr& connection_pool);

  DataPtr UpdatePartially(TimePoint now, TimePoint from,
                          const utils::AsyncStatus& status, TimeStorage& ts,
                          LogExtra& log_extra) const final;

 private:
  static constexpr std::chrono::minutes kUpdateInterval{1};
  static constexpr std::chrono::minutes kCleanUpdateInterval{30};
  static constexpr std::chrono::seconds kLastUpdateCorrection{10};

  const utils::mongo::PoolPtr connection_pool_;
};

}  // namespace caches
