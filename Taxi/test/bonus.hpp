#pragma once

#include <lookup-ordering/assessor_info/bonus.hpp>
#include <lookup-ordering/assessors/assessor.hpp>
#include <lookup-ordering/assessors/factory.hpp>

namespace lookup_ordering::assessors::test {

class Bonus : public Assessor {
 public:
  using Assessor::Assessor;

  Result Process(const models::Candidate&,
                 models::CandidateContext&) const override;
};

class BonusFactory : public Factory {
 public:
  BonusFactory();

  std::unique_ptr<Assessor> Create(const formats::json::Value&) const override;
};

}  // namespace lookup_ordering::assessors::test
