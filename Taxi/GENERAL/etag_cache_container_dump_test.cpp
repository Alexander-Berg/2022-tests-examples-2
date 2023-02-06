#include "etag_cache_container.hpp"

#include <vector>

#include <userver/utest/utest.hpp>

#include <userver/dump/test_helpers.hpp>

using dump::TestWriteReadCycle;

using namespace models::etag_data;
using namespace std::chrono;

TEST(CacheDumpEtagCacheContainer, EtagSequence) {
  const auto now = utils::datetime::Now();
  TestWriteReadCycle(EtagSequence{false, {}});
  TestWriteReadCycle(EtagSequence{true, {{0ll, now}}});
  TestWriteReadCycle(EtagSequence{
      true, {{0ll, now}, {16ll, now + seconds{2}}, {4ll, now + minutes{6}}}});
}

TEST(CacheDumpEtagCacheContainer, EtagCacheContainer) {
  const auto now = utils::datetime::Now();
  std::vector<EtagDbEntry> etag_entries = {
      {0, 1, true, now},
      {0, 33, false, now + seconds{3}},
      {1, 2, false, now + seconds{1}},
      {44, 4, true, now + seconds{2}},
      {44, 3, false, now},
      {44, 55, false, now + minutes{1}},
  };

  EtagCacheContainer<models::etag_data::DataType::kOfferedModes> cache;
  for (auto&& entry : etag_entries) {
    cache.insert_or_assign(entry.driver_id_id, std::move(entry));
    TestWriteReadCycle(cache);
  }
}
