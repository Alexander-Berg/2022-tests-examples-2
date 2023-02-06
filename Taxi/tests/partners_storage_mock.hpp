#pragma once

#include <gmock/gmock.h>
#include <models/partners_storage.hpp>
#include <userver/utest/utest.hpp>

namespace testing {

using PartnerId = ::eats_partners::types::partner::Id;
namespace partner = ::eats_partners::types::partner;
namespace token = ::eats_partners::types::action_tokens;
using ::eats_partners::models::partners_storage::detail::IStorageImpl;

namespace search = ::eats_partners::types::search_request;

struct PartnersStorageMock : public IStorageImpl {
  MOCK_METHOD(std::optional<partner::InfoStorage>, GetPartnerInfo,
              (PartnerId partner_id, bool with_blocked), (const, override));
  MOCK_METHOD(std::optional<partner::InfoStorage>, GetPartnerInfo,
              (eats_partners::types::email::PersonalEmailId personal_email_id,
               bool with_blocked),
              (const, override));
  MOCK_METHOD(std::vector<partner::InfoStorage>, FindPartners,
              (search::Params params, search::PaginateData paginate,
               bool with_blocked),
              (const, override));
  MOCK_METHOD(token::ActionToken, GenerateToken, (PartnerId partner_id),
              (const, override));
  MOCK_METHOD(bool, BlockPartner, (PartnerId partner_id), (const, override));
  MOCK_METHOD(bool, UnblockPartner, (PartnerId partner_id), (const, override));
  MOCK_METHOD(std::optional<PartnerId>, CreatePartner,
              (const partner::CreatePartnerInfo& partner), (const, override));
  MOCK_METHOD(std::vector<int>, GetRoleIds,
              (const std::vector<std::string>& roles), (const, override));
  MOCK_METHOD(int64_t, CleanExpiredTokens,
              (storages::postgres::TimePointTz expired_at), (const, override));
  MOCK_METHOD(bool, IsTokenForResetPasswordValid,
              (PartnerId partner_id, partner::Token token,
               storages::postgres::TimePointTz expired_at),
              (const, override));
  MOCK_METHOD(std::optional<partner::InfoStorage>, UpdatePartner,
              (const partner::UpdatePartnerInfo& partner_info),
              (const, override));
  MOCK_METHOD(bool, UpdateFirstLogin, (PartnerId partner_id),
              (const, override));
  MOCK_METHOD(std::vector<partner::Info>, FindPartnersByPlace,
              (int64_t place_id, search::PaginateData paginate,
               bool with_blocked),
              (const override));
};

}  // namespace testing

namespace eats_partners::types::role {
inline bool operator==(const Role& lhs, const Role& rhs) {
  return std::tie(lhs.id, lhs.slug, lhs.title) ==
         std::tie(rhs.id, rhs.slug, rhs.title);
}
}  // namespace eats_partners::types::role

namespace eats_partners::types::partner {
inline bool operator==(const Info& lhs, const Info& rhs) {
  return std::tie(lhs.id, lhs.email, lhs.is_blocked, lhs.blocked_at, lhs.places,
                  lhs.is_fast_food, lhs.timezone, lhs.country_code, lhs.roles,
                  lhs.partner_uuid, lhs.personal_email_id) ==
         std::tie(rhs.id, rhs.email, rhs.is_blocked, rhs.blocked_at, rhs.places,
                  rhs.is_fast_food, rhs.timezone, rhs.country_code, rhs.roles,
                  rhs.partner_uuid, rhs.personal_email_id);
}

inline bool operator==(const UpdatePartnerInfo& lhs,
                       const UpdatePartnerInfo& rhs) {
  return std::tie(lhs.id, lhs.email, lhs.is_fast_food, lhs.password, lhs.places,
                  lhs.timezone, lhs.country_code, lhs.roles,
                  lhs.personal_email_id) ==
         std::tie(rhs.id, rhs.email, rhs.is_fast_food, rhs.password, rhs.places,
                  rhs.timezone, rhs.country_code, rhs.roles,
                  rhs.personal_email_id);
}

inline bool operator==(const CreatePartnerInfo& lhs,
                       const CreatePartnerInfo& rhs) {
  return std::tie(lhs.id, lhs.email, lhs.is_fast_food, lhs.password, lhs.places,
                  lhs.timezone, lhs.country_code, lhs.roles,
                  lhs.personal_email_id) ==
         std::tie(rhs.id, rhs.email, rhs.is_fast_food, rhs.password, rhs.places,
                  rhs.timezone, rhs.country_code, rhs.roles,
                  rhs.personal_email_id);
}

}  // namespace eats_partners::types::partner

namespace eats_partners::types::search_request {

inline bool operator==(const PaginateData& lhs, const PaginateData& rhs) {
  return std::tie(lhs.limit, lhs.cursor) == std::tie(rhs.limit, lhs.cursor);
}

inline bool operator==(const RangeType& lhs, const RangeType& rhs) {
  return std::tie(lhs.from, lhs.to) == std::tie(rhs.from, lhs.to);
}

inline bool operator==(const Params& lhs, const Params& rhs) {
  return std::tie(lhs.id, lhs.email, lhs.personal_email_id, lhs.places,
                  lhs.first_login_range, lhs.is_fast_food) ==
         std::tie(rhs.id, rhs.email, rhs.personal_email_id, rhs.places,
                  rhs.first_login_range, rhs.is_fast_food);
}

inline void PrintTo(const Params& item, std::ostream* os) {
  using std::chrono::system_clock;
  *os << "[" << item.id->GetUnderlying() << ", " << item.email.value() << "]";
}
}  // namespace eats_partners::types::search_request

namespace eats_partners::types::action_tokens {

inline bool operator==(const ActionToken& lhs, const ActionToken& rhs) {
  return std::tie(lhs.partner_id, lhs.token) ==
         std::tie(rhs.partner_id, rhs.token);
}

}  // namespace eats_partners::types::action_tokens
