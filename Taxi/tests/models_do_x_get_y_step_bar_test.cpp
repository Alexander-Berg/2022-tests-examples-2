#include <gtest/gtest.h>

#include <string>

#include <boost/algorithm/string/join.hpp>
#include <boost/range/adaptor/transformed.hpp>

#include <models/do_x_get_y_step_bar.hpp>

namespace models {
std::ostream& operator<<(std::ostream& stream, const DoXGetYStepBar& step_bar) {
  return stream << ToString(step_bar);
}

std::ostream& operator<<(std::ostream& stream, const DoXGetYStep& step) {
  return stream << ToString(step);
}
}  // namespace models

namespace std {
std::ostream& operator<<(std::ostream& stream,
                         const std::optional<models::DoXGetYStep>& step) {
  return stream << (step ? ToString(*step) : "(none)");
}
}  // namespace std

struct TestMergeParams {
  models::DoXGetYStepBar step_bar1;
  models::DoXGetYStepBar step_bar2;
  models::DoXGetYStepBar expected_result;
};

class TestMerge : public testing::Test,
                  public testing::WithParamInterface<TestMergeParams> {};

TEST_P(TestMerge, Test) {
  const auto& p = GetParam();

  const auto result = models::MergeStepBars(p.step_bar1, p.step_bar2);
  ASSERT_EQ(p.expected_result, result);
}

INSTANTIATE_TEST_SUITE_P(
    DoXGetYStepBar, TestMerge,
    testing::Values(  //
        TestMergeParams{
            // step_bar1:
            models::DoXGetYStepBar({
                models::DoXGetYStep{5, 9, 50.0},
                models::DoXGetYStep{10, 11, 60.0},
                models::DoXGetYStep{12, 19, 70.0},
                models::DoXGetYStep{20, std::nullopt, 80.0},
            }),
            // step_bar2:
            models::DoXGetYStepBar({
                models::DoXGetYStep{6, 11, 200.0},
                models::DoXGetYStep{12, 14, 300.0},
                models::DoXGetYStep{15, std::nullopt, 350.0},
            }),
            // expected_result:
            models::DoXGetYStepBar({
                models::DoXGetYStep{5, 5, 50.0},
                models::DoXGetYStep{6, 9, 250.0},
                models::DoXGetYStep{10, 11, 260.0},
                models::DoXGetYStep{12, 14, 370.0},
                models::DoXGetYStep{15, 19, 420.0},
                models::DoXGetYStep{20, std::nullopt, 430.0},
            }),
        },
        TestMergeParams{
            // step_bar1:
            models::DoXGetYStepBar({
                models::DoXGetYStep{5, 9, 50.0},
                models::DoXGetYStep{10, std::nullopt, 60.0},
            }),
            // step_bar2:
            models::DoXGetYStepBar({
                models::DoXGetYStep{15, 19, 200.0},
                models::DoXGetYStep{20, std::nullopt, 300.0},
            }),
            // expected_result:
            models::DoXGetYStepBar({
                models::DoXGetYStep{5, 9, 50.0},
                models::DoXGetYStep{10, 14, 60.0},
                models::DoXGetYStep{15, 19, 260.0},
                models::DoXGetYStep{20, std::nullopt, 360.0},
            }),
        },
        TestMergeParams{
            // step_bar1:
            models::DoXGetYStepBar({
                models::DoXGetYStep{5, 9, 50.0},
            }),
            // step_bar2:
            models::DoXGetYStepBar({
                models::DoXGetYStep{10, std::nullopt, 100.0},
            }),
            // expected_result:
            models::DoXGetYStepBar({
                models::DoXGetYStep{5, 9, 50.0},
                models::DoXGetYStep{10, std::nullopt, 100.0},
            }),
        },
        TestMergeParams{
            // step_bar1:
            models::DoXGetYStepBar({}),
            // step_bar2:
            models::DoXGetYStepBar({}),
            // expected_result:
            models::DoXGetYStepBar({}),
        },
        TestMergeParams{
            // step_bar1:
            models::DoXGetYStepBar({}),
            // step_bar2:
            models::DoXGetYStepBar({
                models::DoXGetYStep{10, std::nullopt, 100.0},
            }),
            // expected_result:
            models::DoXGetYStepBar({
                models::DoXGetYStep{10, std::nullopt, 100.0},
            }),
        },
        TestMergeParams{
            // step_bar1:
            models::DoXGetYStepBar({
                models::DoXGetYStep{5, 9, 50.0},
            }),
            // step_bar2:
            models::DoXGetYStepBar({
                models::DoXGetYStep{15, 19, 100.0},
            }),
            // expected_result:
            models::DoXGetYStepBar({
                models::DoXGetYStep{5, 9, 50.0},
                models::DoXGetYStep{15, 19, 100.0},
            }),
        },
        TestMergeParams{
            // step_bar1:
            models::DoXGetYStepBar({
                models::DoXGetYStep{5, 9, 50.0},
            }),
            // step_bar2:
            models::DoXGetYStepBar({
                models::DoXGetYStep{6, 8, 100.0},
            }),
            // expected_result:
            models::DoXGetYStepBar({
                models::DoXGetYStep{5, 5, 50.0},
                models::DoXGetYStep{6, 8, 150.0},
                models::DoXGetYStep{9, 9, 50.0},
            }),
        }));

TEST(DoXGetYStepBar, TestGetStepByNumberOfRides) {
  const auto step_bar = models::DoXGetYStepBar({
      models::DoXGetYStep{5, 5, 50.0},
      models::DoXGetYStep{6, 9, 250.0},
      models::DoXGetYStep{10, 11, 260.0},
      models::DoXGetYStep{12, 14, 370.0},
      models::DoXGetYStep{15, 19, 420.0},
      models::DoXGetYStep{20, std::nullopt, 430.0},
  });

  ASSERT_EQ(models::GetStepByNumberOfRides(step_bar, 10),
            (models::DoXGetYStep{10, 11, 260.0}));
  ASSERT_EQ(models::GetStepByNumberOfRides(step_bar, 11),
            (models::DoXGetYStep{10, 11, 260.0}));
  ASSERT_EQ(models::GetStepByNumberOfRides(step_bar, 25),
            (models::DoXGetYStep{20, std::nullopt, 430.0}));
  ASSERT_EQ(models::GetStepByNumberOfRides(step_bar, 1), std::nullopt);

  const auto empty_step_bar = models::DoXGetYStepBar({});
  ASSERT_EQ(models::GetStepByNumberOfRides(empty_step_bar, 10), std::nullopt);
}
