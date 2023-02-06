#include <userver/utest/utest.hpp>

#include <utils/orders.hpp>

void CompareGetAppVersion(const std::string& user_agent) {
  const auto& version = tips::orders::GetAppVersion(user_agent);
  ASSERT_EQ(version, std::nullopt);
}

void CompareGetAppVersion(
    const std::string& user_agent,
    const ua_parser::ApplicationVersion& expected_version) {
  const auto& version = tips::orders::GetAppVersion(user_agent);
  ASSERT_TRUE(version.has_value());
  const ua_parser::ApplicationVersion& returned_version = version.value();
  ASSERT_EQ(returned_version.GetVerMajor(), expected_version.GetVerMajor());
  ASSERT_EQ(returned_version.GetVerMinor(), expected_version.GetVerMinor());
  ASSERT_EQ(returned_version.GetVerBuild(), expected_version.GetVerBuild());
}

TEST(TestGetAppVersion, valid_android) {
  CompareGetAppVersion(
      "yandex-taxi/3.144.0.1012580 Android/10 (OnePlus; ONEPLUS A6000)",
      {3, 144, 0});
}

TEST(TestGetAppVersion, valid_iphone) {
  CompareGetAppVersion(
      "ru.yandex.ytaxi/550.8.0.66566 (iPhone; iPhone12,5; iOS 13.5.1; Darwin)",
      {550, 8, 0});
}

TEST(TestGetAppVersion, empty_ua) { CompareGetAppVersion(""); }

TEST(TestGetAppVersion, too_short_version) {
  CompareGetAppVersion("yandex-taxi/3.144 Android/10 (OnePlus; ONEPLUS A6000)");
}

TEST(TestGetAppVersion, exact_version) {
  CompareGetAppVersion(
      "yandex-taxi/3.144.0 Android/10 (OnePlus; ONEPLUS A6000)", {3, 144, 0});
}

TEST(TestGetAppVersion, not_number) {
  CompareGetAppVersion("yandex-taxi/3.a.0 Android/10 (OnePlus; ONEPLUS A6000)");
}

TEST(TestGetAppVersion, not_number_in_last) {
  CompareGetAppVersion(
      "yandex-taxi/3.144.a Android/10 (OnePlus; ONEPLUS A6000)");
}

TEST(TestGetAppVersion, out_of_range) {
  CompareGetAppVersion("yandex-taxi/3.144.12345678901234567890");
}

TEST(TestGetAppVersion, multiple_slash_in_version) {
  CompareGetAppVersion(
      "pull-742/ru.yandex.ytaxi/3.91.8035 (iPhone; iPhone8,1; iOS 12.2; "
      "Darwin)",
      {3, 91, 8035});
}
