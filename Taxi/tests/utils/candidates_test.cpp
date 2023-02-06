#include <chrono>

#include <userver/utest/utest.hpp>

#include <defs/internal/candidates.hpp>
#include <utils/candidates.hpp>

namespace alt_offer_discount::utils {

namespace {

using Candidate = defs::internal::candidates::Candidate;
using Seconds = std::chrono::seconds;

Candidate GetCandidate(int total_time,
                       std::optional<int> left_time = std::nullopt) {
  Candidate candidate;
  candidate.route_info.time = std::chrono::seconds(total_time);
  if (left_time) {
    candidate.chain_info.emplace();
    candidate.chain_info->left_time = std::chrono::seconds(*left_time);
  }
  return candidate;
}

}  // namespace

TEST(LessByPerformerBoardingTime, TwoChains) {
  EXPECT_EQ(LessByPerformerBoardingTime(GetCandidate(3, 2), GetCandidate(3, 1)),
            true);
  EXPECT_EQ(LessByPerformerBoardingTime(GetCandidate(3, 1), GetCandidate(3, 2)),
            false);
  EXPECT_EQ(LessByPerformerBoardingTime(GetCandidate(3, 2), GetCandidate(3, 2)),
            false);
  EXPECT_EQ(LessByPerformerBoardingTime(GetCandidate(2, 2), GetCandidate(2, 1)),
            true);
  EXPECT_EQ(LessByPerformerBoardingTime(GetCandidate(2, 1), GetCandidate(2, 2)),
            false);
  EXPECT_EQ(LessByPerformerBoardingTime(GetCandidate(2, 2), GetCandidate(2, 2)),
            false);
}

TEST(LessByPerformerBoardingTime, OneChain) {
  EXPECT_EQ(LessByPerformerBoardingTime(GetCandidate(2, 1), GetCandidate(2)),
            true);
  EXPECT_EQ(LessByPerformerBoardingTime(GetCandidate(2), GetCandidate(2, 1)),
            false);
  EXPECT_EQ(LessByPerformerBoardingTime(GetCandidate(6, 2), GetCandidate(5)),
            true);
  EXPECT_EQ(LessByPerformerBoardingTime(GetCandidate(6, 2), GetCandidate(4)),
            false);
}

TEST(LessByPerformerBoardingTime, TwoFree) {
  EXPECT_EQ(LessByPerformerBoardingTime(GetCandidate(1), GetCandidate(2)),
            true);
  EXPECT_EQ(LessByPerformerBoardingTime(GetCandidate(2), GetCandidate(2)),
            false);
}

TEST(LessByPerformerBoardingTime, Deviation) {
  EXPECT_EQ(LessByPerformerBoardingTime(GetCandidate(10, 14),
                                        GetCandidate(2, 1), Seconds(4)),
            true);
  EXPECT_EQ(LessByPerformerBoardingTime(GetCandidate(10, 5), GetCandidate(6, 1),
                                        Seconds(4)),
            false);
  EXPECT_EQ(LessByPerformerBoardingTime(GetCandidate(10, 15),
                                        GetCandidate(16, 2), Seconds(4)),
            false);
}

TEST(GetPerformerBoardingTime, ChainPerformerDeviationExist) {
  EXPECT_EQ(GetPerformerBoardingTime(GetCandidate(10, 4), Seconds(3)).count(),
            6);
  EXPECT_EQ(GetPerformerBoardingTime(GetCandidate(10, 13), Seconds(3)).count(),
            0);
  EXPECT_EQ(GetPerformerBoardingTime(GetCandidate(10, 14), Seconds(3)).count(),
            14);
  EXPECT_EQ(GetPerformerBoardingTime(GetCandidate(10, 10)).count(), 0);
  EXPECT_EQ(GetPerformerBoardingTime(GetCandidate(10, 9)).count(), 1);
}

TEST(GetPerformerBoardingTime, ChainPerformerNoDeviation) {
  EXPECT_EQ(GetPerformerBoardingTime(GetCandidate(10, 4)).count(), 6);
  EXPECT_EQ(GetPerformerBoardingTime(GetCandidate(10, 11)).count(), 11);
  EXPECT_EQ(GetPerformerBoardingTime(GetCandidate(10, 10)).count(), 0);
}

TEST(GetPerformerBoardingTime, FreePerformer) {
  EXPECT_EQ(GetPerformerBoardingTime(GetCandidate(10)).count(), 10);
}

}  // namespace alt_offer_discount::utils
