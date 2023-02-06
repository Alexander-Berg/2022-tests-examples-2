#include <userver/utest/utest.hpp>

#include <caches/driver_restrictions_cache.hpp>
#include <caches/models/entity_categories_container_base.hpp>

const pg_cache::detail::DriverRestrictionsRow row1{
    "park_id",
    "driver_id",
    {{"row1"}},
    std::chrono::system_clock::time_point{std::chrono::system_clock::now()},
    std::nullopt};
const pg_cache::detail::DriverRestrictionsRow row2{
    "park_id",
    "driver_id",
    {{"row2"}},
    std::chrono::system_clock::time_point{std::chrono::system_clock::now()} +
        std::chrono::hours(24),
    std::nullopt};

UTEST(EntityCacheNewWay, TestInsertSame) {
  const auto pk_copy = row1.GetPrimaryKey();
  auto pk = pk_copy;
  auto r = row1;
  pg_cache::detail::DriverRestrictionsContainer cache;
  cache.insert_or_assign(std::move(pk), std::move(r));

  EXPECT_EQ(cache.GetItemByPrimaryKey(pk_copy)->updated_at, row1.updated_at);

  pk = pk_copy;
  r = row2;
  cache.insert_or_assign(std::move(pk), std::move(r));
  EXPECT_EQ(cache.GetItemByPrimaryKey(pk_copy)->updated_at, row2.updated_at);

  pk = pk_copy;
  r = row1;
  cache.insert_or_assign(std::move(pk), std::move(r));
  EXPECT_EQ(cache.GetItemByPrimaryKey(pk_copy)->updated_at, row1.updated_at);
}
