#include <userver/utest/utest.hpp>

#include <models/partners_storage.hpp>
#include "partners_storage_mock.hpp"

namespace testing {

using ::eats_partners::models::partners_storage::Storage;

struct PartnerStorageTest : public Test {
  std::shared_ptr<PartnersStorageMock> storage_mock;
  Storage storage;

  const PartnerId partner_id{42};
  partner::Email email{"test@example.com"};

  PartnerStorageTest()
      : storage_mock(std::make_shared<PartnersStorageMock>()),
        storage(storage_mock) {}
};

TEST_F(PartnerStorageTest, should_call_GetPartnerInfoId) {
  EXPECT_CALL(*storage_mock, GetPartnerInfo(partner_id, true)).Times(1);
  storage.GetPartnerInfo(partner_id, true);
}

TEST_F(PartnerStorageTest, should_call_PasswordRequestReset) {
  using namespace eats_partners::types;
  auto p_id = partner::Id{1};
  auto personal_id = email::PersonalEmailId{"email_id"};
  auto partner = partner::Info{p_id,
                               email,
                               personal_id,
                               bool{false},
                               std::nullopt,
                               std::vector<int64_t>{1, 2, 3},
                               bool{true},
                               "Europe/Moscow",
                               "RU",
                               std::vector<role::Role>{},
                               "1b9d70ef-d667-4c9c-9b20-c61209ea6332"};
  EXPECT_CALL(*storage_mock, GenerateToken(p_id))
      .WillOnce(Return(token::ActionToken{p_id, "qaz"}));
  auto res = storage.PasswordRequestReset(partner, {"link", "token", "email"});
  ASSERT_EQ(res, "link?token=qaz&email=test%40example.com");
}

TEST_F(PartnerStorageTest, should_call_GenerateLink) {
  using namespace eats_partners::types;
  using namespace eats_partners::models::partners_storage;
  auto p_id = partner::Id{1};
  auto res = storage.GenerateLink(token::ActionToken{p_id, "qaz"},
                                  partner::Email{"qwe@qwe.com"},
                                  LinkData{"link", "token", "email"});
  ASSERT_EQ(res, "link?token=qaz&email=qwe%40qwe.com");
}

TEST_F(PartnerStorageTest, should_call_GenerateToken) {
  EXPECT_CALL(*storage_mock, GenerateToken(partner_id)).Times(1);
  storage.GenerateToken(partner_id);
}

TEST_F(PartnerStorageTest, should_call_FindPartners) {
  search::Params params{};
  search::PaginateData paginate{};
  EXPECT_CALL(*storage_mock, FindPartners(params, paginate, true)).Times(1);
  storage.FindPartners(std::move(params), std::move(paginate), true);
}

TEST_F(PartnerStorageTest, should_call_BlockPartner) {
  EXPECT_CALL(*storage_mock, BlockPartner(partner_id)).Times(1);
  storage.BlockPartner(partner_id);
}

TEST_F(PartnerStorageTest, true_PasswordReset) {
  auto partner_id = partner::Id{1};
  auto token = partner::Token{"000"};
  size_t cost = 12;
  size_t length_password = 6;
  using std::chrono_literals::operator""s;
  const auto expired_date = utils::datetime::Now() - 604800s;
  EXPECT_CALL(*storage_mock, IsTokenForResetPasswordValid(partner_id, token, _))
      .WillOnce(Return(true));
  auto password = storage.PasswordReset(partner_id, token, cost,
                                        length_password, expired_date);
  if (password) {
    ASSERT_EQ(password->first.size(), length_password);
  }
}

TEST_F(PartnerStorageTest, false_PasswordReset) {
  auto partner_id = partner::Id{1};
  auto token = partner::Token{"000"};
  size_t cost = 12;
  size_t length_password = 6;
  using std::chrono_literals::operator""s;
  const auto expired_date = utils::datetime::Now() - 604800s;
  EXPECT_CALL(*storage_mock, IsTokenForResetPasswordValid(
                                 partner_id, token,
                                 storages::postgres::TimePointTz{expired_date}))
      .WillOnce(Return(false));
  auto password = storage.PasswordReset(partner_id, token, cost,
                                        length_password, expired_date);
  ASSERT_FALSE(password.has_value());
}

TEST_F(PartnerStorageTest, should_call_CleanExpiredTokens) {
  auto date = utils::datetime::Now();
  EXPECT_CALL(*storage_mock,
              CleanExpiredTokens(storages::postgres::TimePointTz{date}))
      .Times(1);
  storage.CleanExpiredTokens(storages::postgres::TimePointTz{date});
}

}  // namespace testing
