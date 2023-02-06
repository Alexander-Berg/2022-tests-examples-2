#include "penalty.hpp"

#include "fetch_penalty.hpp"

namespace lookup_ordering::assessors::test {

Result Penalty::Process(const models::Candidate&,
                        models::CandidateContext& context) const {
  // *NOTE* to set penalty in the Result::bonus we negate "penalty_value"
  return Result{ReadyCode::kOk, -FetchPenalty::Get(context)};
}

PenaltyFactory::PenaltyFactory() : Factory(info::kTestPenalty) {}

std::unique_ptr<Assessor> PenaltyFactory::Create([
    [maybe_unused]] const formats::json::Value& params) const {
  return std::make_unique<Penalty>(info());
}

}  // namespace lookup_ordering::assessors::test
