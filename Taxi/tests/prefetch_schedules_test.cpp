#include <gtest/gtest.h>

#include <chrono>

#include "common.hpp"

#include <logic/prefetch_schedules.hpp>

namespace {

struct TestParams {
  std::chrono::minutes to_midnight;
  std::chrono::minutes save_user_requests_before_midnight_minutes;
  std::chrono::minutes prefetech_stored_requests_before_midnight_minutes;

  bool expected;
};

struct NeedStoreUserRequestFixtureParametrized
    : public BaseTestWithParam<TestParams> {};

}  // namespace

TEST_P(NeedStoreUserRequestFixtureParametrized, Test) {
  const auto& p = GetParam();
  ASSERT_EQ(logic::impl::NeedStoreUserRequest(
                p.to_midnight, p.save_user_requests_before_midnight_minutes,
                p.prefetech_stored_requests_before_midnight_minutes),
            p.expected);
}

using namespace std::chrono_literals;

INSTANTIATE_TEST_SUITE_P(
    NeedStoreUserRequestTestParametrized,
    NeedStoreUserRequestFixtureParametrized,
    ::testing::Values<TestParams>(TestParams{35min, 60min, 30min, true},
                                  TestParams{25min, 60min, 30min, false},
                                  TestParams{65min, 60min, 30min, false}));
