#pragma once

#include <chrono>

#include <lookup-ordering/assessor_info/fetch_penalty.hpp>
#include <lookup-ordering/assessors/factory.hpp>
#include <lookup-ordering/assessors/fetcher.hpp>

namespace lookup_ordering::assessors::test {

class FetchPenalty : public Assessor,
                     public Fetcher<FetchPenalty, std::chrono::seconds> {
 public:
  static const std::string kContextKey;

  using Assessor::Assessor;

  Result Process(const models::Candidate&,
                 models::CandidateContext&) const override;
};

class FetchPenaltyFactory : public Factory {
 public:
  FetchPenaltyFactory();

  std::unique_ptr<Assessor> Create(const formats::json::Value&) const override;
};
}  // namespace lookup_ordering::assessors::test
