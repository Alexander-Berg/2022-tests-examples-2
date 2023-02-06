#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include "candidate.hpp"
#include "lookup_result.hpp"

using lookup::models::Candidate;
using lookup::models::LookupResult;
using lookup::models::LookupResultCode;

namespace {
LookupResult CreateLookupResult(const LookupResultCode code,
                                const std::string& message) {
  return LookupResult{code, message};
}

LookupResult CreateLookupResult(Candidate candidate) {
  return LookupResult(std::move(candidate));
}

Candidate CreateCandidate() {
  Candidate candidate{};
  candidate.uuid = "driver_id_1";
  return candidate;
}

void TestBehavior() {
  const std::vector<LookupResultCode> codes = {
      LookupResultCode::CandidateFound,
      LookupResultCode::NewSearchRequired,
      LookupResultCode::CandidateNotFound,
      LookupResultCode::Delayed,
      LookupResultCode::Conflict,
      LookupResultCode::Created,
      LookupResultCode::Updated,
      LookupResultCode::UnderSupply,
      LookupResultCode::Retained,
      LookupResultCode::BadClass,
      LookupResultCode::Staled,
      LookupResultCode::ServerError,
      LookupResultCode::TimeoutError,
      LookupResultCode::OtherError,
  };
  ASSERT_EQ(codes.size(),
            static_cast<size_t>(LookupResultCode::OtherError) + 1);

  const auto candidate = CreateCandidate();

  for (const auto code : codes) {
    switch (code) {
      case LookupResultCode::CandidateFound: {
        EXPECT_NO_THROW(CreateLookupResult(candidate));
        const auto result = CreateLookupResult(candidate);
        ASSERT_EQ(result.GetCode(), code);
        EXPECT_NO_THROW(result.GetCandidate());
        EXPECT_EQ(result.GetCandidate().uuid, candidate.uuid);
        EXPECT_THROW(result.GetMessage(), std::runtime_error);

        EXPECT_THROW(CreateLookupResult(code, "message"), std::runtime_error);
      } break;
      case LookupResultCode::NewSearchRequired:
      case LookupResultCode::CandidateNotFound:
      case LookupResultCode::Delayed:
      case LookupResultCode::Conflict:
      case LookupResultCode::Created:
      case LookupResultCode::Updated:
      case LookupResultCode::UnderSupply:
      case LookupResultCode::Retained:
      case LookupResultCode::BadClass:
      case LookupResultCode::Staled:
      case LookupResultCode::ServerError:
      case LookupResultCode::TimeoutError:
      case LookupResultCode::OtherError: {
        const std::string message =
            "code=" + std::to_string(static_cast<size_t>(code));
        EXPECT_NO_THROW(CreateLookupResult(code, message));
        const auto result = CreateLookupResult(code, message);
        EXPECT_EQ(result.GetCode(), code);
        EXPECT_THROW(result.GetCandidate(), std::runtime_error);
        EXPECT_NO_THROW(result.GetMessage());
        EXPECT_EQ(result.GetMessage(), message);
      } break;
    }
  }
}

}  // namespace

UTEST(LookupResult, Behavior) { TestBehavior(); }
