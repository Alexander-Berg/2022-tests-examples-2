#include "bonus.hpp"

#include "fetch_bonus.hpp"

namespace lookup_ordering::assessors::test {

Result Bonus::Process(const models::Candidate&,
                      models::CandidateContext& context) const {
  return Result{ReadyCode::kOk, FetchBonus::Get(context)};
}

BonusFactory::BonusFactory() : Factory(info::kTestBonus) {}

std::unique_ptr<Assessor> BonusFactory::Create([
    [maybe_unused]] const formats::json::Value& params) const {
  return std::make_unique<Bonus>(info());
}

}  // namespace lookup_ordering::assessors::test
