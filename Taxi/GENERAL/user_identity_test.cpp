#include <userver/utest/utest.hpp>

#include <models/user_identity.hpp>

using fleet_financial_statements::models::UserId;
using fleet_financial_statements::models::UserIdentity;
using fleet_financial_statements::models::UserIdentityCvt;
using fleet_financial_statements::models::UserKind;

TEST(UserIdentityTest, Construct) {
  EXPECT_EQ(UserIdentity(), UserIdentity(UserKind::kService, UserId()));

  EXPECT_EQ(UserIdentity(server::auth::UserProvider::kYandex,
                         server::auth::UserId(0)),
            UserIdentity(UserKind::kDefault, UserId("0")));
  EXPECT_EQ(UserIdentity(server::auth::UserProvider::kYandex,
                         server::auth::UserId(18446744073709551615ULL)),
            UserIdentity(UserKind::kDefault, UserId("18446744073709551615")));

  EXPECT_EQ(UserIdentity(server::auth::UserProvider::kYandexTeam,
                         server::auth::UserId(0)),
            UserIdentity(UserKind::kSupport, UserId("0")));
  EXPECT_EQ(UserIdentity(server::auth::UserProvider::kYandexTeam,
                         server::auth::UserId(18446744073709551615ULL)),
            UserIdentity(UserKind::kSupport, UserId("18446744073709551615")));

  EXPECT_THROW(UserIdentity(UserKind::kService, UserId("100")),
               std::invalid_argument);

  EXPECT_THROW(UserIdentity(UserKind::kDefault, UserId("")),
               std::invalid_argument);
  EXPECT_THROW(UserIdentity(UserKind::kDefault, UserId("ABC")),
               std::invalid_argument);

  EXPECT_THROW(UserIdentity(UserKind::kSupport, UserId("")),
               std::invalid_argument);
  EXPECT_THROW(UserIdentity(UserKind::kSupport, UserId("ABC")),
               std::invalid_argument);
}

TEST(UserIdentityTest, CppToPg) {
  UserIdentityCvt cvt;

  EXPECT_EQ(cvt(UserIdentity()), "X");
  EXPECT_EQ(cvt(UserIdentity(UserKind::kDefault, UserId{"100"})), "Y100");
  EXPECT_EQ(cvt(UserIdentity(UserKind::kSupport, UserId{"100"})), "T100");
}

TEST(UserIdentityTest, PgToCpp) {
  UserIdentityCvt cvt;

  EXPECT_EQ(cvt("X"), UserIdentity());
  EXPECT_EQ(cvt("Y100"), UserIdentity(UserKind::kDefault, UserId{"100"}));
  EXPECT_EQ(cvt("T100"), UserIdentity(UserKind::kSupport, UserId{"100"}));

  EXPECT_THROW(cvt("X100"), storages::postgres::InvalidInputFormat);
  EXPECT_THROW(cvt("Y"), storages::postgres::InvalidInputFormat);
  EXPECT_THROW(cvt("T"), storages::postgres::InvalidInputFormat);
}
