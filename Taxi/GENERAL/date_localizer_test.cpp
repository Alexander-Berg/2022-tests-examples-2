#include "date_localizer.hpp"

#include <gtest/gtest.h>

#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

namespace utils::test {

const std::string kMockedNow{"2021-04-01T12:00:00+03:00"};
const std::string kMoscowTz{"Europe/Moscow"};

class DriverLocalizerMock : public driver_localizer::DriverLocalizerBase {
 public:
  DriverLocalizerMock() {}

  std::string GetWithFallback([[maybe_unused]] const std::string& key,
                              [[maybe_unused]] const std::string& fallback_key,
                              [[maybe_unused]] const l10n::ArgsList& args = {},
                              [[maybe_unused]] int count = 1) const override {
    throw std::logic_error{"Not implemented"};
  }

  std::string Get([[maybe_unused]] const std::string& key,
                  [[maybe_unused]] int count = 1) const override {
    return key;
  };

  std::string GetWithArgs([[maybe_unused]] const std::string& key,
                          [[maybe_unused]] const l10n::ArgsList& args,
                          [[maybe_unused]] int count = 1) const override {
    throw std::logic_error{"Not implemented"};
  };
};

TEST(DateLocalizer, OldDate) {
  static const auto mocked_time =
      ::utils::datetime::GuessStringtime(kMockedNow, kMoscowTz);
  ::utils::datetime::MockNowSet(mocked_time);

  DriverLocalizerMock localizer;
  auto time_point = mocked_time - std::chrono::hours{50};
  const auto localized_date =
      LocalizeDateWithTimezone(time_point, kMoscowTz, localizer);
  EXPECT_EQ(localized_date, "30 driver_localizer.month_3");
}

TEST(DateLocalizer, Yesterday) {
  static const auto mocked_time =
      ::utils::datetime::GuessStringtime(kMockedNow, kMoscowTz);
  ::utils::datetime::MockNowSet(mocked_time);

  DriverLocalizerMock localizer;
  auto time_point = mocked_time - std::chrono::hours{30};
  const auto localized_date =
      LocalizeDateWithTimezone(time_point, kMoscowTz, localizer);
  EXPECT_EQ(localized_date, "driver_localizer.yesterday");
}

TEST(DateLocalizer, Today) {
  static const auto mocked_time =
      ::utils::datetime::GuessStringtime(kMockedNow, kMoscowTz);
  ::utils::datetime::MockNowSet(mocked_time);

  DriverLocalizerMock localizer;
  auto time_point = mocked_time - std::chrono::hours{6};
  const auto localized_date =
      LocalizeDateWithTimezone(time_point, kMoscowTz, localizer);
  EXPECT_EQ(localized_date, "driver_localizer.today");
}
}  // namespace utils::test
