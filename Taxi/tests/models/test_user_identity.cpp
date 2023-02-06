#include <gtest/gtest.h>

#include "models/user_identity.hpp"

#include <string>

#include <userver/formats/json/serialize.hpp>

namespace models::user_identity {
namespace {
const std::string kTestId = "test_id";
const std::string kTestPhoneId = "test_phone_id";
const std::string kTestYandexUid1 = "test_yandex_uid1";
const std::string kTestYandexUid2 = "test_yandex_uid2";

const std::string kIdentityJson =
    R"({"user_id": ")" + kTestId + R"(", "phone_id": ")" + kTestPhoneId +
    R"(", "yandex_uid": ")" + kTestYandexUid1 +
    R"(", "bound_yandex_uids": [")" + kTestYandexUid2 +
    R"("], "taxi_staff": true, "yandex_staff": true, "flags": )"
    R"({"has_ya_plus":true, "is_phonish":true,"is_portal":true}})";
}  // namespace

TEST(TestUserIdentity, Parse) {
  const auto id_json = formats::json::FromString(kIdentityJson);
  const auto user_identity = id_json.As<UserIdentity>();
  EXPECT_EQ(user_identity.user_id, kTestId);
  EXPECT_EQ(user_identity.phone_id, kTestPhoneId);
  EXPECT_EQ(user_identity.bound_yandex_uids.size(), 1);
  EXPECT_EQ(*user_identity.yandex_uid, kTestYandexUid1);
  EXPECT_EQ(user_identity.bound_yandex_uids.front(), kTestYandexUid2);
  EXPECT_EQ(user_identity.taxi_staff, true);
  EXPECT_EQ(user_identity.yandex_staff, true);
  EXPECT_EQ(user_identity.flags.is_phonish, true);
  EXPECT_EQ(user_identity.flags.is_portal, true);
  EXPECT_EQ(user_identity.flags.has_ya_plus, true);
}

TEST(TestUserIdentity, ParseAndBack) {
  const auto id_json = formats::json::FromString(kIdentityJson);
  const auto user_identity = id_json.As<UserIdentity>();
  EXPECT_EQ(user_identity.ToJson(), id_json);
}

}  // namespace models::user_identity
