#include <gtest/gtest.h>
#include <common/test_config.hpp>
#include <ios>
#include <sstream>

#include <config/config.hpp>
#include <orderkit/check_fraud.hpp>
#include <utils/known_apps.hpp>

namespace {
config::Config GetConfig(int time, const std::string& city = "moscow") {
  config::DocsMap docs_map = config::DocsMapForTest();
  docs_map.Override("FRAUD_COOKIE_CREATED", time);
  docs_map.Override("NOT_FRAUD_CITIES", BSON_ARRAY(city));
  return config::Config(docs_map);
}
std::string PrepareUidCookie(int timestamp) {
  std::stringstream ss;
  // some random base string
  ss << "123456789";
  ss.width(10);
  ss.fill('0');
  ss << timestamp;
  return ss.str();
}
std::string PrepareFuidCookie(int timestamp) {
  std::stringstream ss;
  ss.width(8);
  ss.fill('0');
  ss << std::hex << timestamp;
  ss << "somerandomstring";
  return ss.str();
}
}  // namespace

TEST(CheckFraud, PrepareUidCookie) {
  ASSERT_EQ(std::string("1234567890000000001"), PrepareUidCookie(1));
  ASSERT_EQ(std::string("1234567891499118319"), PrepareUidCookie(1499118319));
}

TEST(CheckFraud, PrepareFuidCookie) {
  ASSERT_EQ(std::string("00000001somerandomstring"), PrepareFuidCookie(1));
  ASSERT_EQ(std::string("595abaefsomerandomstring"),
            PrepareFuidCookie(1499118319));
}

TEST(CheckFraud, NotDetected) {
  using namespace orderkit;
  using namespace orderkit::checkfraud;

  LogExtra log_extra;

  models::orders::Order order;
  order.statistics.application = models::applications::Web;
  order.city = "yerevan";

  config::Config config = GetConfig(10);

  int uid_seconds = utils::datetime::Timestamp() - 20;
  int fuid_seconds = uid_seconds;
  std::string uid_cookie = PrepareUidCookie(uid_seconds);
  std::string fuid_cookie = PrepareFuidCookie(fuid_seconds);

  Input input{config, order, uid_cookie, fuid_cookie};

  ASSERT_FALSE(IsFraudDetected(input, log_extra));
}

TEST(CheckFraud, ValidApp) {
  using namespace orderkit;
  using namespace orderkit::checkfraud;

  LogExtra log_extra;

  models::orders::Order order;
  order.statistics.application = models::applications::Android;
  order.city = "yerevan";

  config::Config config = GetConfig(30);

  std::string uid_cookie = "some_invalid_cookie";
  std::string fuid_cookie = "some_invalid_cookie";

  Input input{config, order, uid_cookie, fuid_cookie};

  ASSERT_FALSE(IsFraudDetected(input, log_extra));
}

TEST(CheckFraud, NotFraudCity) {
  using namespace orderkit;
  using namespace orderkit::checkfraud;

  LogExtra log_extra;

  models::orders::Order order;
  order.statistics.application = models::applications::Web;
  order.city = "moscow";

  config::Config config = GetConfig(30);

  std::string uid_cookie = "some_invalid_cookie";
  std::string fuid_cookie = "some_invalid_cookie";

  Input input{config, order, uid_cookie, fuid_cookie};

  ASSERT_FALSE(IsFraudDetected(input, log_extra));
}

TEST(CheckFraud, NoUidCookie) {
  using namespace orderkit;
  using namespace orderkit::checkfraud;

  LogExtra log_extra;

  models::orders::Order order;
  order.statistics.application = models::applications::Web;
  order.city = "yerevan";

  config::Config config = GetConfig(10);

  int fuid_seconds = utils::datetime::Timestamp() - 20;
  std::string fuid_cookie = PrepareFuidCookie(fuid_seconds);

  Input input{config, order, "", fuid_cookie};

  ASSERT_FALSE(IsFraudDetected(input, log_extra));
}

TEST(CheckFraud, NoFuidCookie) {
  using namespace orderkit;
  using namespace orderkit::checkfraud;

  LogExtra log_extra;

  models::orders::Order order;
  order.statistics.application = models::applications::Web;
  order.city = "yerevan";

  config::Config config = GetConfig(10);

  int uid_seconds = utils::datetime::Timestamp() - 20;
  std::string uid_cookie = PrepareUidCookie(uid_seconds);

  Input input{config, order, uid_cookie, ""};

  ASSERT_FALSE(IsFraudDetected(input, log_extra));
}

TEST(CheckFraud, Detected) {
  using namespace orderkit;
  using namespace orderkit::checkfraud;

  LogExtra log_extra;

  models::orders::Order order;
  order.statistics.application = models::applications::Web;
  order.city = "yerevan";

  config::Config config = GetConfig(30);

  int uid_seconds = utils::datetime::Timestamp() - 20;
  int fuid_seconds = uid_seconds;
  std::string uid_cookie = PrepareUidCookie(uid_seconds);
  std::string fuid_cookie = PrepareFuidCookie(fuid_seconds);

  Input input{config, order, uid_cookie, fuid_cookie};

  ASSERT_TRUE(IsFraudDetected(input, log_extra));
}

TEST(CheckFraud, InvalidUidCookie) {
  using namespace orderkit;
  using namespace orderkit::checkfraud;

  LogExtra log_extra;

  models::orders::Order order;
  order.statistics.application = models::applications::Web;
  order.city = "yerevan";

  config::Config config = GetConfig(10);

  int fuid_seconds = utils::datetime::Timestamp() - 20;
  std::string uid_cookie = "invalid";
  std::string fuid_cookie = PrepareFuidCookie(fuid_seconds);

  Input input{config, order, uid_cookie, fuid_cookie};

  ASSERT_TRUE(IsFraudDetected(input, log_extra));
}

TEST(CheckFraud, InvalidUidCookie2) {
  using namespace orderkit;
  using namespace orderkit::checkfraud;

  LogExtra log_extra;

  models::orders::Order order;
  order.statistics.application = models::applications::Web;
  order.city = "yerevan";

  config::Config config = GetConfig(10);

  int fuid_seconds = utils::datetime::Timestamp() - 20;
  std::string uid_cookie = "long_and_invalid_cannot_be_converted_to_int";
  std::string fuid_cookie = PrepareFuidCookie(fuid_seconds);

  Input input{config, order, uid_cookie, fuid_cookie};

  ASSERT_TRUE(IsFraudDetected(input, log_extra));
}

TEST(CheckFraud, InvalidFuidCookie) {
  using namespace orderkit;
  using namespace orderkit::checkfraud;

  LogExtra log_extra;

  models::orders::Order order;
  order.statistics.application = models::applications::Web;
  order.city = "yerevan";

  config::Config config = GetConfig(10);

  int uid_seconds = utils::datetime::Timestamp() - 20;
  std::string uid_cookie = PrepareUidCookie(uid_seconds);
  std::string fuid_cookie = "short";

  Input input{config, order, uid_cookie, fuid_cookie};

  ASSERT_TRUE(IsFraudDetected(input, log_extra));
}

TEST(CheckFraud, InvalidFuidCookie2) {
  using namespace orderkit;
  using namespace orderkit::checkfraud;

  LogExtra log_extra;

  models::orders::Order order;
  order.statistics.application = models::applications::Web;
  order.city = "yerevan";

  config::Config config = GetConfig(10);

  int uid_seconds = utils::datetime::Timestamp() - 20;
  std::string uid_cookie = PrepareUidCookie(uid_seconds);
  std::string fuid_cookie = "long_but_still_invalid";

  Input input{config, order, uid_cookie, fuid_cookie};

  ASSERT_TRUE(IsFraudDetected(input, log_extra));
}
