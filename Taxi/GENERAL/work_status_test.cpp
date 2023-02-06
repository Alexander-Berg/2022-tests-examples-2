#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>
#include <filters/partners/work_status/work_status.hpp>
#include <userver/utest/utest.hpp>

namespace cf = candidates::filters;
const cf::FilterInfo kEmptyInfo;

using models::drivers::WorkStatus;

namespace {
struct TestCase {
  WorkStatus work_status;
  cf::Result expected_result;
};

class WorkStatusFilterTestCase : public ::testing::TestWithParam<TestCase> {};
}  // namespace

TEST_P(WorkStatusFilterTestCase, Filter) {
  const auto& test_case = GetParam();
  cf::Context context{};

  auto driver = std::make_shared<models::Driver>(models::Driver{});
  driver->work_status = test_case.work_status;
  cf::infrastructure::FetchDriver::Set(context, driver);

  cf::partners::WorkStatus filter(kEmptyInfo);
  EXPECT_EQ(filter.Process({}, context), test_case.expected_result);
}

INSTANTIATE_TEST_SUITE_P(
    WorkStatusFilterTest, WorkStatusFilterTestCase,
    ::testing::Values(TestCase{WorkStatus::kWorking, cf::Result::kAllow},
                      TestCase{WorkStatus::kNotWorking, cf::Result::kDisallow},
                      TestCase{WorkStatus::kFired, cf::Result::kDisallow},
                      TestCase{WorkStatus::kUnknown, cf::Result::kDisallow}));
