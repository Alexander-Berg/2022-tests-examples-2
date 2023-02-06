#include "fetch_penalty.hpp"

namespace lookup_ordering::assessors::test {

const std::string FetchPenalty::kContextKey = "test/penalty_value";

Result FetchPenalty::Process(const models::Candidate&,
                             models::CandidateContext& context) const {
  // value name is "penalty_value" and we store non-negative number of seconds
  Set(context, std::chrono::seconds(50));
  return {};
}

FetchPenaltyFactory::FetchPenaltyFactory() : Factory(info::kTestFetchPenalty) {}

std::unique_ptr<Assessor> FetchPenaltyFactory::Create([
    [maybe_unused]] const formats::json::Value& params) const {
  return std::make_unique<FetchPenalty>(info());
}

}  // namespace lookup_ordering::assessors::test
