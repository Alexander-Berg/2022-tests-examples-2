#include <models/experiments.hpp>
#include <utils/known_apps.hpp>

#include <gtest/gtest.h>

#include <string>
#include <vector>

struct TestUserData {
  mongo::BSONObj exp_doc;
  mongo::BSONObj user_doc;
  bool yandex_staff;
  bool taxi_staff;
  bool user_vip;
  bool expected_result;
};

// clang-format off
const std::vector<TestUserData> user_tests {
  {
      BSON(
          "name" << "test_user_agent" <<
                 "user_phone_id_last_digits" << BSON_ARRAY("1" << "2") <<
                 "user_id_last_digits" << BSON_ARRAY("5" << "7") <<
                 "platforms" << BSON_ARRAY("iphone") <<
                 "excluded_app_version" << "1.2.3"
      ),
      BSON(
          "_id" << "1234567890abcdefghijkl0987654337" <<
                "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032") <<
                "application" << "iphone" <<
                "application_version" << "1.2.3"
      ),
      false,
      false,
      false,
      false
  },
  {
      BSON(
          "name" << "test_user_agent" <<
                 "user_phone_id_last_digits" << BSON_ARRAY("1" << "2") <<
                 "user_id_last_digits" << BSON_ARRAY("5" << "7") <<
                 "platforms" << BSON_ARRAY("iphone") <<
                 "excluded_app_version" << "1.2.3"
      ),
      BSON(
          "_id" << "1234567890abcdefghijkl0987654337" <<
                "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032") <<
                "application" << "iphone" <<
                "application_version" << "1.2.4"
      ),
      false,
      false,
      false,
      true
  },
  {
      BSON(
          "name" << "test_user_agent" <<
                 "user_phone_id_last_digits" << BSON_ARRAY("1" << "2") <<
                 "user_id_last_digits" << BSON_ARRAY("5" << "7") <<
                 "platforms" << BSON_ARRAY("iphone")
      ),
      BSON(
          "_id" << "1234567890abcdefghijkl0987654337" <<
                "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032") <<
                "application" << "iphone" <<
                "application_version" << "1.2.4"
      ),
      false,
      false,
      false,
      true
  },
  {
          BSON(
                  "name" << "test_yauber_user_agent" <<
                         "user_phone_id_last_digits" << BSON_ARRAY("1" << "2") <<
                         "user_id_last_digits" << BSON_ARRAY("5" << "7") <<
                         "platforms" << BSON_ARRAY("uber_iphone")
          ),
          BSON(
                  "_id" << "1234567890abcdefghijkl0987654337" <<
                        "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032") <<
                        "application" << "uber_iphone" <<
                        "application_version" << "1.2.4"
          ),
          false,
          false,
          false,
          true
  },

  {
          BSON(
                  "name" << "test_yauber_user_agent" <<
                         "user_phone_id_last_digits" << BSON_ARRAY("1" << "2") <<
                         "user_id_last_digits" << BSON_ARRAY("5" << "7") <<
                         "platforms" << BSON_ARRAY("web" << "uber_android")
          ),
          BSON(
                  "_id" << "1234567890abcdefghijkl0987654327" <<
                        "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0031") <<
                        "application" << "uber_android" <<
                        "application_version" << "5.7.4"
          ),
          false,
          false,
          false,
          true
  },

  {
          BSON(
                  "name" << "test_yango_user_agent" <<
                         "user_phone_id_last_digits" << BSON_ARRAY("1" << "2") <<
                         "user_id_last_digits" << BSON_ARRAY("5" << "7") <<
                         "platforms" << BSON_ARRAY("yango_iphone")
          ),
          BSON(
                  "_id" << "1234567890abcdefghijkl0987654337" <<
                        "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032") <<
                        "application" << "yango_iphone" <<
                        "application_version" << "1.2.4"
          ),
          false,
          false,
          false,
          true
  },
  {
          BSON(
                  "name" << "test_yango_user_agent" <<
                         "user_phone_id_last_digits" << BSON_ARRAY("1" << "2") <<
                         "user_id_last_digits" << BSON_ARRAY("5" << "7") <<
                         "platforms" << BSON_ARRAY("web" << "yango_android")
          ),
          BSON(
                  "_id" << "1234567890abcdefghijkl0987654327" <<
                        "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0031") <<
                        "application" << "yango_android" <<
                        "application_version" << "5.7.4"
          ),
          false,
          false,
          false,
          true
  },

  {
    BSON(
      "name" << "test_xp" <<
      "user_phone_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "user_id_last_digits" << BSON_ARRAY("5" << "7") <<
      "platforms" << BSON_ARRAY("web" << "android")
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654327" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0031") <<
      "gcm_token" << "gcm_token_data"
    ),
    false,
    false,
    false,
    true
  },
  {
    BSON(
      "name" << "test_xp" <<
      "user_id_last_digits" << BSON_ARRAY("5" << "321")
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654321" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c003e")
    ),
    false,
    false,
    false,
    true
  },
  {
    BSON(
      "name" << "test_xp" <<
      "user_phone_id_last_digits" << BSON_ARRAY("5" << "e")
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl098765432e" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0035")
    ),
    false,
    false,
    false,
    true
  },
  {
    BSON(
      "name" << "test_xp"
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654321" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c003e") <<
      "gcm_token" << "gcm_token_data"
    ),
    false,
    false,
    false,
    true
  },
  {
    BSON(
      "name" << "test_yandex_staff_ok" <<
      "yandex_staff" << true <<
      "staff_group" << "yandex"
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654321" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c003e") <<
      "gcm_token" << "gcm_token_data"
    ),
    true,
    false,
    false,
    true
  },
  {
    BSON(
      "name" << "test_yandex_staff_fail" <<
      "yandex_staff" << true <<
      "staff_group" << "yandex"
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654321" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0035") <<
      "gcm_token" << "gcm_token_data"
    ),
    false,
    false,
    false,
    false
  },
  {
    BSON(
      "name" << "test_user_agent" <<
      "user_phone_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "user_id_last_digits" << BSON_ARRAY("5" << "7") <<
      "platforms" << BSON_ARRAY("iphone")
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654337" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032") <<
      "application" << "iphone"
    ),
    false,
    false,
    false,
    true
  },
  {
    BSON(
      "name" << "test_apns_token" <<
      "user_phone_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "user_id_last_digits" << BSON_ARRAY("5" << "7") <<
      "platforms" << BSON_ARRAY("iphone")
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654337" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032") <<
      "apns_token" << "apns_token_data"
    ),
    false,
    false,
    false,
    true
  },
  {
    BSON(
      "name" << "test_apns_token_user_agent" <<
      "user_phone_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "user_id_last_digits" << BSON_ARRAY("5" << "7") <<
      "platforms" << BSON_ARRAY("iphone")
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654337" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032") <<
      "apns_token" << "apns_token_data" <<
      "application" << "iphone"
    ),
    false,
    false,
    false,
    true
  },
  {
    BSON(
      "name" << "test_apns_token_user_agent" <<
      "user_phone_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "user_id_last_digits" << BSON_ARRAY("5" << "7") <<
      "platforms" << BSON_ARRAY("iphone")
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654337" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032")
    ),
    false,
    false,
    false,
    false
  },
  {
    BSON(
      "name" << "test_apns_token_user_agent" <<
      "user_phone_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "user_id_last_digits" << BSON_ARRAY("5" << "7") <<
      "platforms" << BSON_ARRAY("iphone")
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654337" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032") <<
      "apns_token" << "apns_token_data" <<
      "application" << "iphone"
    ),
    false,
    false,
    false,
    true
  },
  {
    BSON(
      "name" << "test_all_vips" <<
      "salt" << "0a704431d84747f2b2e2b346a6c3cbfa" <<
      "vip_percent" << BSON("from" <<  0 << "to" << 100)
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654337" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032")
    ),
    false,
    false,
    true,
    true
  },
  {
    BSON(
      "name" << "test_vip_percent_fail" <<
      "salt" << "0a704431d84747f2b2e2b346a6c3cbfa" <<
      "vip_percent" << BSON("from" <<  0 << "to" << 50)
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654337" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032")
    ),
    false,
    false,
    true,
    false
  },
  {
    BSON(
      "name" << "test_vip_or_staff" <<
      "salt" << "0a704431d84747f2b2e2b346a6c3cbfa" <<
      "vip_percent" << BSON("from" <<  50 << "to" << 100) <<
      "staff_percent" << BSON("from" <<  50 << "to" << 100) <<
      "taxi_staff" << true
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654337" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032")
    ),
    false,
    true,
    false,
    true
  },
  {
    BSON(
      "name" << "test_phone_id_or_yandex_percent" <<
      "salt" << "bf20947d46fd40f4bac312498c367e70" <<
      "phone_id_percent" << BSON("from" <<  0 << "to" << 50) <<
      "staff_percent" << BSON("from" <<  0 << "to" << 50) <<
      "yandex_staff" << true
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654337" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032")
    ),
    true,
    false,
    false,
    true
  },
  {
    BSON(
      "name" << "test_phone_id_or_yandex_percent" <<
      "salt" << "bf20947d46fd40f4bac312498c367e70" <<
      "phone_id_percent" << BSON("from" <<  0 << "to" << 50) <<
      "staff_percent" << BSON("from" <<  0 << "to" << 50) <<
      "yandex_staff" << true
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654337" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032")
    ),
    false,
    false,
    true,
    true
  },
  {
    BSON(
      "name" << "test_phone_id_or_yandex_percent_fail" <<
      "salt" << "bf20947d46fd40f4bac312498c367e70" <<
      "phone_id_percent" << BSON("from" <<  50 << "to" << 100) <<
      "staff_percent" << BSON("from" <<  0 << "to" << 50) <<
      "yandex_staff" << true
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654337" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032")
    ),
    false,
    false,
    false,
    false
  },
  {
    BSON(
      "name" << "test_active_experiment" <<
      "salt" << "bf20947d46fd40f4bac312498c367e70" <<
      "active" << true
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654337" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032")
    ),
    false,
    false,
    false,
    true
  },
  {
    BSON(
      "name" << "test_inactive_experiment" <<
      "salt" << "bf20947d46fd40f4bac312498c367e70" <<
      "active" << false
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654337" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032")
    ),
    false,
    false,
    false,
    false
  },
  {
    BSON(
      "name" << "test_yandex_without_percent" <<
      "salt" << "bf20947d46fd40f4bac312498c367e70" <<
      "active" << true
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654337" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032") <<
      "yandex_staff" << true
    ),
    true,
    false,
    false,
    true

  },
  {
    BSON(
      "name" << "test_taxi_without_percent" <<
      "salt" << "bf20947d46fd40f4bac312498c367e70"
    ),
    BSON(
      "_id" << "1234567890abcdefghijkl0987654337" <<
      "phone_id" << mongo::OID("539ea1ede7e5b1f5397c0032") <<
      "taxi_staff" << true
    ),
    false,
    true,
    false,
    true

  }
};
// clang-format on

class UserExperiments : public ::testing::TestWithParam<TestUserData> {};

TEST_P(UserExperiments, Parametrized) {
  const auto& params = GetParam();
  common::UserExperiment experiment(params.exp_doc);
  models::orders::User user;
  user.Deserialize(params.user_doc);

  std::string app = common::UserExperiment::GetPlatform(user);

  GTEST_ASSERT_EQ(
      params.expected_result,
      experiment.Check(user.id, user.phone_id.toString(), app,
                       user.application_version, params.yandex_staff,
                       params.taxi_staff, params.user_vip));
}

INSTANTIATE_TEST_CASE_P(ExperimentsTest, UserExperiments,
                        ::testing::ValuesIn(user_tests), );

using Order = models::orders::Order;
using Phone = models::Phone;

struct TestOrderData {
  mongo::BSONObj experiment;
  Order order;
  Phone phone;
  bool user_vip;
  bool expected_result;
};

// clang-format off
std::vector<TestOrderData> order_tests {
  {
    BSON(
      "name" << "test_xp" <<
      "order_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "cities" << BSON_ARRAY("msk") <<
      "user_phone_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "platforms" << BSON_ARRAY("web" << "android")
    ),
    []() {
      Order o;
      o.id = "04dea1ede7e5b1f5397c0031";
      o.user_phone_id = mongo::OID("539ea1ede7e5b1f5397c0032");
      o.statistics.application = models::applications::Web;
      o.city = "msk";
      return o;
    }(),
    [](){
      Phone p;
      p.phone_id = mongo::OID("539ea1ede7e5b1f5397c0032");
      p.yandex_staff = true;
      return p;
    }(),
    false,
    true
  },
  {
    BSON(
      "name" << "test_xp" <<
      "order_id_last_digits" << BSON_ARRAY("1" << "2") <<
      "cities" << BSON_ARRAY("msk")
    ),
    [](){
      Order o;
      o.id = "04dea1ede7e5b1f5397c0031";
      o.user_phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      return o;
    }(),
    [](){
      Phone p;
      p.phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      return p;
    }(),
    false,
    false
  },
  {
    BSON(
      "name" << "test_xp" <<
      "user_phone_id_restrictions" << "all"
    ),
    [](){
      Order o;
      o.id = "04dea1ede7e5b1f5397c0031";
      return o;
    }(),
    [](){
      Phone p;
      return p;
    }(),
    false,
    true
  },
  {
    BSON(
      "name" << "test_yandex_staff_ok" <<
      "yandex_staff" << true <<
      "staff_group" << "yandex"
    ),
    [](){
      Order o;
      o.id = "04dea1ede7e5b1f5397c0031";
      o.user_phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      return o;
    }(),
    [](){
      Phone p;
      p.phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      p.yandex_staff = true;
      return p;
    }(),
    false,
    true
  },
  {
    BSON(
      "name" << "test_yandex_staff_fail" <<
      "yandex_staff" << true <<
      "staff_group" << "yandex"
    ),
    [](){
      Order o;
      o.id = "04dea1ede7e5b1f5397c0031";
      o.user_phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      return o;
    }(),
    [](){
      Phone p;
      p.phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      p.yandex_staff = false;
      return p;
    }(),
    false,
    false
  },
  {
    BSON(
      "name" << "test_phone_id_percent" <<
      "salt" << "bf20947d46fd40f4bac312498c367e70" <<
      "phone_id_percent" << BSON("from" <<  50 << "to" << 100)
    ),
    [](){
      Order o;
      o.id = "04dea1ede7e5b1f5397c0031";
      o.user_phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      return o;
    }(),
    [](){
      Phone p;
      p.phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      p.yandex_staff = false;
      return p;
    }(),
    false,
    true
  },
  {
    BSON(
      "name" << "test_phone_id_percent_fail" <<
      "salt" << "bf20947d46fd40f4bac312498c367e70" <<
      "phone_id_percent" << BSON("from" <<  0 << "to" << 50)
    ),
    [](){
      Order o;
      o.id = "04dea1ede7e5b1f5397c0031";
      o.user_phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      return o;
    }(),
    [](){
      Phone p;
      p.phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      p.yandex_staff = false;
      return p;
    }(),
    false,
    false
  },
  {
    BSON(
      "name" << "test_vip" <<
      "salt" << "bf20947d46fd40f4bac312498c367e70" <<
      "vip_percent" << BSON("from" <<  50 << "to" << 100)
    ),
    [](){
    Order o;
    o.id = "04dea1ede7e5b1f5397c0031";
    o.user_phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
    return o;
    }(),
    [](){
      Phone p;
      p.phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      p.yandex_staff = false;
      return p;
    }(),
    true,
    true
  },
  {
    BSON(
      "name" << "test_vip_or_phone_id_percent" <<
      "salt" << "bf20947d46fd40f4bac312498c367e70" <<
      "vip_percent" << BSON("from" <<  50 << "to" << 100) <<
      "phone_id_percent" << BSON("from" <<  0 << "to" << 50)
    ),
    [](){
    Order o;
        o.id = "04dea1ede7e5b1f5397c0031";
        o.user_phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
        return o;
      }(),
      [](){
        Phone p;
        p.phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
        p.yandex_staff = false;
        return p;
      }(),
      true,
      true
  },
  {
    BSON(
      "name" << "test_vip_or_taxi_percent" <<
      "salt" << "bf20947d46fd40f4bac312498c367e70" <<
      "vip_percent" << BSON("from" <<  0 << "to" << 50) <<
      "staff_percent" << BSON("from" <<  50 << "to" << 100) <<
      "staff_group" << "taxi"
    ),
    [](){
      Order o;
      o.id = "04dea1ede7e5b1f5397c0031";
      o.user_phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      return o;
    }(),
    [](){
      Phone p;
      p.phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      p.taxi_staff = true;
      return p;
    }(),
    true,
    false
  },
  {
    BSON(
      "name" << "test_vip_or_taxi_percent_fail" <<
      "salt" << "bf20947d46fd40f4bac312498c367e70" <<
      "vip_percent" << BSON("from" <<  0 << "to" << 50) <<
      "staff_percent" << BSON("from" <<  0 << "to" << 50) <<
      "staff_group" << "taxi"
    ),
    [](){
      Order o;
      o.id = "04dea1ede7e5b1f5397c0031";
      o.user_phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      return o;
    }(),
    [](){
      Phone p;
      p.phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      p.taxi_staff = true;
      return p;
    }(),
    true,
    false
  },
  {
    BSON(
      "name" << "test_active_experiment" <<
      "salt" << "bf20947d46fd40f4bac312498c367e70" <<
      "active" << true
    ),
    [](){
      Order o;
      o.id = "04dea1ede7e5b1f5397c0031";
      o.user_phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      return o;
    }(),
    [](){
      Phone p;
      p.phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      p.taxi_staff = true;
      return p;
    }(),
    true,
    true
  },
  {
    BSON(
      "name" << "test_inactive_experiment" <<
      "salt" << "bf20947d46fd40f4bac312498c367e70" <<
      "active" << false
    ),
    [](){
      Order o;
      o.id = "04dea1ede7e5b1f5397c0031";
      o.user_phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      return o;
    }(),
    [](){
      Phone p;
      p.phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      p.taxi_staff = true;
      return p;
    }(),
    true,
    false
  },
  {
    BSON(
      "name" << "test_yandex_without_percent" <<
       "salt" << "bf20947d46fd40f4bac312498c367e70" <<
       "yandex_staff" << true
    ),
    [](){
    Order o;
    o.id = "04dea1ede7e5b1f5397c0031";
    o.user_phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
    return o;
    }(),
    [](){
    Phone p;
    p.phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
    p.yandex_staff = true;
    return p;
    }(),
    false,
    true
  },
  {
    BSON(
      "name" << "test_taxi_without_percent" <<
      "salt" << "bf20947d46fd40f4bac312498c367e70" <<
      "taxi_staff" << true
    ),
    [](){
      Order o;
      o.id = "04dea1ede7e5b1f5397c0031";
      o.user_phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      return o;
    }(),
    [](){
      Phone p;
      p.phone_id = mongo::OID("539ea1ede7e5b1f5397c0031");
      p.taxi_staff = true;
      return p;
    }(),
    false,
    true
  },
};
// clang-format on

class OrderExperiments : public ::testing::TestWithParam<TestOrderData> {};

TEST_P(OrderExperiments, Parametrized) {
  const auto& params = GetParam();
  common::OrderExperiment experiment(params.experiment);
  EXPECT_EQ(params.expected_result,
            experiment.Check(params.order, params.phone,
                             params.order.user_phone_id.toString(),
                             params.user_vip, {}));
}

INSTANTIATE_TEST_CASE_P(ExperimentsTest, OrderExperiments,
                        ::testing::ValuesIn(order_tests), );
