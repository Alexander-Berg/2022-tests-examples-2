#include <gtest/gtest.h>

#include <chrono>
#include <limits>
#include <vector>

#include <helpers/ema.hpp>

#include <userver/utils/datetime.hpp>

using namespace grocery_dispatch::helpers;

static const std::chrono::system_clock::time_point base_time =
    ::utils::datetime::Stringtime("2020-08-01T22:00:00Z", "UTC");
static const std::chrono::system_clock::time_point alter_time =
    ::utils::datetime::Stringtime("2020-08-01T22:10:00Z", "UTC");

// Проверяем, что сглаживание не накапливает ошибку и с хорошей точностью
// сходится к константе.
TEST(SmoothedEta, ErrorCompensationStep) {
  constexpr std::size_t base_ticks = 10;
  constexpr std::size_t step_ticks = 10;
  constexpr double smooth_factor = 0.35;

  std::vector<std::chrono::system_clock::time_point> input(
      base_ticks + step_ticks, base_time);

  for (std::size_t i = base_ticks; i < input.size(); ++i) {
    input[i] = alter_time;
  }

  auto smoothed_time = base_time;
  double relative_delta = std::numeric_limits<double>::max();

  for (std::size_t i = 0; i < input.size(); ++i) {
    smoothed_time = EvalSmoothedEta(smoothed_time, input[i], smooth_factor, 1);

    if (i > base_ticks) {
      auto delta = alter_time - smoothed_time;
      auto next_relative_delta = static_cast<double>(delta.count()) /
                                 alter_time.time_since_epoch().count();
      EXPECT_LT(next_relative_delta, relative_delta);
      relative_delta = next_relative_delta;
    }
  }

  EXPECT_NEAR(0, relative_delta, 1e-8);

  auto delta_seconds = std::chrono::duration_cast<std::chrono::seconds>(
                           relative_delta * alter_time.time_since_epoch())
                           .count();
  ASSERT_LT(delta_seconds, 10);
}

TEST(SmoothedEta, ErrorCompensationImpulse) {
  constexpr std::size_t base_ticks = 20;
  constexpr std::size_t spike_idx = 9;
  constexpr double smooth_factor = 0.35;

  std::vector<std::chrono::system_clock::time_point> input(base_ticks,
                                                           base_time);

  input[spike_idx] = alter_time;

  auto smoothed_time = base_time;
  double relative_delta = std::numeric_limits<double>::max();

  for (std::size_t i = 0; i < input.size(); ++i) {
    smoothed_time = EvalSmoothedEta(smoothed_time, input[i], smooth_factor, 1);

    if (i > spike_idx) {
      auto delta = smoothed_time - base_time;
      auto next_relative_delta = static_cast<double>(delta.count()) /
                                 base_time.time_since_epoch().count();
      EXPECT_LT(next_relative_delta, relative_delta);
      relative_delta = next_relative_delta;
    }
  }

  EXPECT_NEAR(0, relative_delta, 1e-8);

  auto delta_seconds = std::chrono::duration_cast<std::chrono::seconds>(
                           relative_delta * base_time.time_since_epoch())
                           .count();
  ASSERT_LT(delta_seconds, 3);
}
