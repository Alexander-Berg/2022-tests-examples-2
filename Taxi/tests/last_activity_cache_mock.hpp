#pragma once

#include <gmock/gmock.h>

#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>

#include <models/last_activity_cache.hpp>

namespace testing {

using PartnerId = ::eats_partners::types::partner::Id;
namespace partner = ::eats_partners::types::partner;
using ::eats_partners::models::last_activity::detail::ICacheImpl;
using ::eats_partners::types::last_activity::CacheItem;
using ::eats_partners::types::last_activity::CacheState;
using ::eats_partners::types::last_activity::FoundCacheItem;
using ::eats_partners::types::last_activity::OptCacheItem;

struct LastActivityCacheMock : public ICacheImpl {
  MOCK_METHOD(OptCacheItem, Get, (const PartnerId& partner_id), (override));
  MOCK_METHOD(void, Put, (const PartnerId& partner_id, CacheItem cached_item),
              (override));
  MOCK_METHOD(void, Invalidate, (), (override));
};

template <typename Duration>
FoundCacheItem MakeFoundItem(const CacheState state, const Duration delay,
                             const std::chrono::system_clock::time_point point =
                                 utils::datetime::Now()) {
  OptCacheItem item;
  const auto now = utils::datetime::Now();
  const partner::LastActivityAt act_at{point};
  switch (state) {
    case CacheState::kHit:
      item = CacheItem{act_at, now - (delay / 2)};
      break;
    case CacheState::kStale:
      item = CacheItem{act_at, now - (delay * 2)};
      break;
    default:
      item = std::nullopt;
      break;
  }
  return {state, item};
}

}  // namespace testing

namespace eats_partners::types::last_activity {
inline bool operator==(const CacheItem& lhs, const CacheItem& rhs) {
  using std::chrono::system_clock;
  return system_clock::to_time_t(lhs.last_activity_at.GetUnderlying()) ==
             system_clock::to_time_t(rhs.last_activity_at.GetUnderlying()) &&
         system_clock::to_time_t(lhs.cached_at) ==
             system_clock::to_time_t(rhs.cached_at);
}

inline void PrintTo(const CacheItem& item, std::ostream* os) {
  using std::chrono::system_clock;
  *os << "[" << system_clock::to_time_t(item.last_activity_at.GetUnderlying())
      << ", " << system_clock::to_time_t(item.cached_at) << "]";
}
}  // namespace eats_partners::types::last_activity
