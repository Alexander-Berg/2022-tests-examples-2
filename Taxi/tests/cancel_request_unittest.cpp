#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>

#include <cancel_request/order_proc.hpp>

namespace order_core::cancel::order_proc {

TEST(GetDriverProfileId, Ok) {
  Candidate candidate{};
  const std::unordered_map<std::string, std::string> ok_cases{
      {"ok0_ok1", "ok1"}, {"_ok1", "ok1"}, {"_", ""}, {"ok0_", ""}};

  for (const auto& ok_case : ok_cases) {
    candidate.driver_id = ok_case.first;
    ASSERT_EQ(candidate.GetDriverProfileId(), ok_case.second);
  }
}

TEST(GetDriverProfileId, Wrong) {
  Candidate candidate{};
  const std::unordered_set<std::string> wrong_cases{"", "wrong"};

  for (const auto& wrong_case : wrong_cases) {
    candidate.driver_id = wrong_case;
    ASSERT_THROW(candidate.GetDriverProfileId(), std::runtime_error);
  }
}
}  // namespace order_core::cancel::order_proc
