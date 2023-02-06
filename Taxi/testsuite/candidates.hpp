#pragma once

#include <dispatch/planner.hpp>

namespace united_dispatch::waybill {

/// (testsuite only) Proposition builder for candidates functionality testing
class TestsuiteCandidatesPlanner : public Planner {
 public:
  bool FilterWaybill(const WaybillProposal& waybill,
                     const handlers::Dependencies& dependencies) const override;

  Output Run(const Input& input, const Environment& environment,
             const handlers::Dependencies& dependencies) const override;

  PlannerType GetPlannerType() const override {
    return PlannerType::kTestsuiteCandidates;
  }
};

}  // namespace united_dispatch::waybill
