#include <clients/eats-partners/client.hpp>
#include <clients/eats-partners/component.hpp>
#include <memory>
#include <userver/utest/utest.hpp>
#include <utils/partner_convertor.hpp>

namespace testing {

struct FormatPartnerTest : public Test {
  FormatPartnerTest() = default;

  static clients::eats_partners::StoredUser MakePartnerInfo(
      int role_id, const std::string& role_slug) {
    clients::eats_partners::StoredUser user;
    user.id = 1;
    user.email = "aaa@aaa.com";
    user.name = "bbb";
    user.places = {11, 12, 13};
    user.timezone = "msk";
    user.is_fast_food = true;
    user.roles = {{role_id, role_slug, "some role"}};
    user.country_code = "RU";
    user.partner_id = "2ed43ecd-815b-4ad9-add0-fb44a5de0ddd";
    return user;
  }
};

TEST_F(FormatPartnerTest, CheckConvertationRole1) {
  auto user = MakePartnerInfo(1, "ROLE_OPERATOR");
  auto formated =
      eats_restapp_support_chat::utils::FormatPartner(std::move(user));
  ASSERT_EQ(formated.role,
            eats_restapp_support_chat::models::PartnerRole::kRoleOperator);
  ASSERT_EQ(formated.email.GetUnderlying(), "aaa@aaa.com");
  ASSERT_EQ(formated.partner_id.GetUnderlying(), "1");
}

TEST_F(FormatPartnerTest, CheckConvertationRole2) {
  auto user = MakePartnerInfo(2, "ROLE_MANAGER");
  auto formated =
      eats_restapp_support_chat::utils::FormatPartner(std::move(user));
  ASSERT_EQ(formated.role,
            eats_restapp_support_chat::models::PartnerRole::kRoleManager);
  ASSERT_EQ(formated.email.GetUnderlying(), "aaa@aaa.com");
  ASSERT_EQ(formated.partner_id.GetUnderlying(), "1");
}
}  // namespace testing
