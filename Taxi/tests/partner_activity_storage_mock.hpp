#pragma once

#include <gmock/gmock.h>
#include <models/partner_activity_storage.hpp>
#include <userver/utest/utest.hpp>

namespace testing {

using PartnerId = ::eats_partners::types::partner::Id;
namespace partner = ::eats_partners::types::partner;
using ::eats_partners::models::partner_activity::detail::IStorageImpl;

struct PartnerActivityStorageMock : public IStorageImpl {
  MOCK_METHOD(partner::LastActivityAt, UpsertActivity, (PartnerId partner_id),
              (const, override));
  MOCK_METHOD(std::vector<partner::Activity>, GetActivity,
              (const std::vector<PartnerId>& partner_ids), (const, override));
  MOCK_METHOD(std::vector<partner::Activity>, GetActivityLimited,
              (const std::vector<PartnerId>& partner_ids,
               std::chrono::system_clock::time_point later_than),
              (const, override));
};

}  // namespace testing

namespace eats_partners::types::partner {
inline bool operator==(const Activity& lhs, const Activity& rhs) {
  using std::chrono::system_clock;
  return lhs.partner_id.GetUnderlying() == rhs.partner_id.GetUnderlying() &&
         system_clock::to_time_t(lhs.last_activity_at.GetUnderlying()) ==
             system_clock::to_time_t(rhs.last_activity_at.GetUnderlying());
}

inline void PrintTo(const Activity& item, std::ostream* os) {
  using std::chrono::system_clock;
  *os << "[" << item.partner_id.GetUnderlying() << ", "
      << system_clock::to_time_t(item.last_activity_at.GetUnderlying()) << "]";
}
}  // namespace eats_partners::types::partner
