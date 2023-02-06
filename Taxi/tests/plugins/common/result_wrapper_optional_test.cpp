#include <plugins/common/serializable.hpp>

#include <gtest/gtest.h>

namespace {

namespace plugins = routestats::plugins::common;

const std::string kField1Value = "field_1_value";
const std::string kField2Value = "field_2_value";

struct TestResult {
  std::string field_1;
  std::string field_2;
};

}  // namespace

TEST(TestResultWrapperOpt, Uninitialized) {
  std::optional<TestResult> result;
  plugins::ResultWrapper<std::optional<TestResult>> wrapper(result);
  wrapper.Set("field_1", &TestResult::field_1, kField1Value);
  ASSERT_TRUE(result);
  ASSERT_EQ(result->field_1, kField1Value);
  wrapper.Set("field_2", &TestResult::field_2, kField2Value);
  ASSERT_TRUE(result);
  ASSERT_EQ(result->field_2, kField2Value);
}

TEST(TestResultWrapperOpt, Initialized) {
  TestResult test_result;
  test_result.field_1 = kField1Value;
  std::optional<TestResult> result(std::move(test_result));
  plugins::ResultWrapper<std::optional<TestResult>> wrapper(result);
  wrapper.Set("field_2", &TestResult::field_2, kField2Value);
  ASSERT_TRUE(result);
  ASSERT_EQ(result->field_2, kField2Value);
  ASSERT_EQ(result->field_1, kField1Value);
}
