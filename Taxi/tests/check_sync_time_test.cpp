#include <userver/utest/utest.hpp>

#include <utils/sync/check_sync_time.hpp>

namespace eats_report_storage::utils::sync {

TEST(CheckTimeInSyncInterval,
     function_shoult_return_true_if_last_sync_time_is_null) {
  const std::string now = "2001-02-02T04:05:06.789012Z";
  const auto now_time_point = ::utils::datetime::Stringtime(now);
  ASSERT_EQ(CheckTimeInSyncInterval(now_time_point, {}, "00:00", "01:00",
                                    std::chrono::hours(1)),
            true);
}

TEST(CheckTimeInSyncInterval,
     function_shoult_return_false_if_now_not_in_interval) {
  const std::string now = "2001-02-02T22:59:06.789012Z";
  const auto now_time_point = ::utils::datetime::Stringtime(now);
  ASSERT_EQ(CheckTimeInSyncInterval(now_time_point, now_time_point, "23:00",
                                    "01:00", std::chrono::hours(1)),
            false);
}

TEST(
    CheckTimeInSyncInterval,
    function_shoult_return_false_if_passed_time_from_last_sync_less_min_sync_interval) {
  const std::string now = "2001-02-02T23:59:06.789012Z";
  const auto now_time_point = ::utils::datetime::Stringtime(now);
  const std::string last_sync = "2001-02-02T22:59:06.789012Z";
  const auto last_sync_time_point = ::utils::datetime::Stringtime(last_sync);
  ASSERT_EQ(CheckTimeInSyncInterval(now_time_point, last_sync_time_point,
                                    "23:00", "01:00", std::chrono::hours(1)),
            false);
}

TEST(CheckTimeInSyncInterval,
     function_shoult_return_true_if_now_in_sync_interval) {
  const std::string now = "2001-02-02T00:59:06.789012Z";
  const auto now_time_point = ::utils::datetime::Stringtime(now);
  const std::string last_sync = "2001-02-01T22:58:06.789012Z";
  const auto last_sync_time_point = ::utils::datetime::Stringtime(last_sync);
  ASSERT_EQ(CheckTimeInSyncInterval(now_time_point, last_sync_time_point,
                                    "23:00", "01:00", std::chrono::hours(1)),
            true);
}

TEST(CheckTimeInSyncInterval,
     function_shoult_throw_exception_if_invalid_format_interval_time) {
  const std::string now = "2001-02-02T00:59:06.789012Z";
  const auto now_time_point = ::utils::datetime::Stringtime(now);
  const std::string last_sync = "2001-02-01T22:58:06.789012Z";
  const auto last_sync_time_point = ::utils::datetime::Stringtime(last_sync);
  ASSERT_THROW(
      CheckTimeInSyncInterval(now_time_point, last_sync_time_point, "00:00:01",
                              "00:00", std::chrono::hours(1)),
      std::runtime_error);
}

}  // namespace eats_report_storage::utils::sync
