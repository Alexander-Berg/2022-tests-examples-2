#include "fetch_bonus.hpp"

namespace lookup_ordering::assessors::test {

const std::string FetchBonus::kContextKey = "test/bonus_value";

Result FetchBonus::Process(const models::Candidate&,
                           models::CandidateContext& context) const {
  Set(context, std::chrono::seconds(100));
  return {};
}

FetchBonusFactory::FetchBonusFactory() : Factory(info::kTestFetchBonus) {}

std::unique_ptr<Assessor> FetchBonusFactory::Create([
    [maybe_unused]] const formats::json::Value& params) const {
  return std::make_unique<FetchBonus>(info());
}

}  // namespace lookup_ordering::assessors::test
