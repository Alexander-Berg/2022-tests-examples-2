#include <userver/utest/utest.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/utils/mock_now.hpp>

#include <stdlib.h>
#include <system_error>

#include <yt-logger/messages/legacy_timestamp/message.hpp>
#include <yt-logger/messages/sample/message.hpp>
#include <yt-logger/messages/sample_json/message.hpp>

namespace {

const std::string kMockTime = "2001-02-03T04:05:06.789012Z";
const std::string kMockTimeLocalLegacy = "2001-02-03T07:05:06.789012Z";
const std::string kMockTimeLocalWithTz = "2001-02-03T09:05:06.789012+05:00";

const auto kMockTimePoint =
    utils::datetime::Stringtime(kMockTime, utils::datetime::kDefaultTimezone,
                                utils::datetime::kTaximeterFormat);

class EkbLocalTzTest : public ::testing::Test {
 public:
  void SetUp() override {
    char* curr_env = ::getenv(kEnvName);
    if (curr_env) old_localtime_ = curr_env;
    if (::setenv(kEnvName, kTimezone, /*overwrite=*/1) == -1) {
      const int errval = errno;
      throw std::system_error(errval, std::system_category());
    }
  }

  void TearDown() override {
    int ret = -1;
    if (old_localtime_.empty()) {
      ret = ::unsetenv(kEnvName);
    } else {
      ret = ::setenv(kEnvName, old_localtime_.c_str(), /*overwrite=*/1);
    }
    if (ret == -1) {
      const int errval = errno;
      throw std::system_error(errval, std::system_category());
    }
  }

 private:
  static constexpr const char* kEnvName = "LOCALTIME";
  static constexpr const char* kTimezone = "Asia/Yekaterinburg";

  std::string old_localtime_;
};

class YtLogger : public EkbLocalTzTest {};

}  // namespace

TEST_F(YtLogger, LegacyTimestamp) {
  yt_logger::messages::legacy_timestamp msg;

  msg.a_b = 1;

  utils::datetime::MockNowSet(kMockTimePoint);
  EXPECT_EQ(
      msg.SerializeToTskv(),
      "tskv\talt_timestamp=" + kMockTimeLocalLegacy + "\ta-b=1\tbody=\tmeta=");
}

TEST_F(YtLogger, Tskv) {
  yt_logger::messages::sample msg;

  msg.a_b = 1;

  utils::datetime::MockNowSet(kMockTimePoint);
  EXPECT_EQ(msg.SerializeToTskv(), "tskv\ttimestamp=" + kMockTimeLocalWithTz +
                                       "\ta-b=1\tbody=\tmeta=");
}

TEST_F(YtLogger, Json) {
  yt_logger::messages::sample_json msg;

  msg.position =
      geometry::PositionAsObject{1.0 * geometry::lat, 2.0 * geometry::lon};

  auto json =
      formats::json::FromString("{\"timestamp\": \"" + kMockTimeLocalLegacy +
                                "\", \"position\": "
                                "{ \"lat\": 1.0, \"lon\": 2.0}}");

  utils::datetime::MockNowSet(kMockTimePoint);
  auto log_json = msg.SerializeToJson();

  EXPECT_EQ(log_json.GetSize(), json.GetSize());

  EXPECT_EQ(log_json["timestamp"].As<std::string>(), kMockTimeLocalWithTz);
  EXPECT_DOUBLE_EQ(log_json["position"]["lat"].As<double>(),
                   json["position"]["lat"].As<double>());
  EXPECT_DOUBLE_EQ(log_json["position"]["lon"].As<double>(),
                   json["position"]["lon"].As<double>());
}
