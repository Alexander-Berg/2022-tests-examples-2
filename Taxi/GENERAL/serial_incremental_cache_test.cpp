#include <gtest/gtest.h>

#include <functional>

#include <userver/utest/utest.hpp>

#include <caches/tag_names_cache.hpp>

namespace {

template <typename Cache>
void TestBasic(std::function<typename Cache::DbEntry(int)> db_entry_gen,
               std::function<typename Cache::Value(int)> value_gen,
               std::function<typename Cache::Id(int)> id_gen) {
  using DbEntry = typename Cache::DbEntry;
  using Value = typename Cache::Value;
  using Id = typename Cache::Id;
  using Version = typename Cache::Version;
  std::vector<DbEntry> db_entries;
  std::vector<Value> values;
  for (int i = 0; i < 40; i++) {
    db_entries.push_back(db_entry_gen(i));
    values.push_back(value_gen(i));
  }

  Cache cache0{10};
  // insert only in incremental
  for (int i = 0; i < 20; i++) {
    cache0.insert({Id{i}, db_entries[i]});
  }
  ASSERT_EQ(cache0.GetVersion(), Version{19});
  auto check = [&values, &id_gen](const Cache& cache, int n) {
    for (int i = 0; i < n; i++) {
      ASSERT_EQ(*cache.FindById(id_gen(i)), values[i]);
      ASSERT_EQ(cache.FindByValue(values[i])->GetUnderlying(), i);
    }
  };

  // check find in incremental
  check(cache0, 20);

  Cache cache1{cache0};
  // check find in core
  check(cache1, 20);

  ASSERT_EQ(cache0.GetVersion(), cache1.GetVersion());
  ASSERT_EQ(cache0.size(), cache1.size());

  for (int i = 20; i < 40; i++) {
    cache1.insert({Id{i}, db_entries[i]});
  }

  // check insertion of incremental to core doesn't wipe previous entries
  Cache cache2{cache1};
  check(cache2, 40);
}
template <typename Cache>
void TestOverwriting(std::function<typename Cache::DbEntry(int)> db_entry_gen,
                     std::function<typename Cache::Value(int)> value_gen,
                     std::function<typename Cache::Id(int)> id_gen) {
  using DbEntry = typename Cache::DbEntry;
  using Value = typename Cache::Value;
  using Id = typename Cache::Id;
  using Version = typename Cache::Version;
  std::vector<DbEntry> db_entries;
  std::vector<Value> values;
  for (int i = 0; i < 4; i++) {
    db_entries.push_back(db_entry_gen(i));
    values.push_back(value_gen(i));
  }

  Cache cache{2};
  for (int i = 0; i < 2; i++) {
    cache.insert({Id{i}, db_entries[i]});
  }

  // insert already inserted into incremental
  cache.insert({Id{0}, db_entries[1]});
  // check that nothing changed
  ASSERT_EQ(*cache.FindById(id_gen(0)), values[0]);
  ASSERT_EQ(cache.FindByValue(values[0])->GetUnderlying(), 0);
  ASSERT_EQ(cache.GetVersion(), Version{1});

  for (int i = 2; i < 4; i++) {
    cache.insert({Id{i}, db_entries[i]});
  }
  Cache cache2{cache};
  // same, but about core part
  cache2.insert({Id{1}, db_entries[0]});
  ASSERT_EQ(*cache2.FindById(id_gen(1)), values[1]);
  ASSERT_EQ(cache2.FindByValue(values[0])->GetUnderlying(), 0);
  ASSERT_EQ(cache2.GetVersion(), Version{3});
}
}  // namespace

using TagNameSerials =
    caches::SerialIncrementalCache<caches::tag_names::Traits>;

UTEST(TestTagNameSerials, Basic) {
  TestBasic<TagNameSerials>(
      [](int i) {
        return caches::tag_names::DbEntry{models::TagNameId{i},
                                          std::to_string(i)};
      },
      [](int i) { return models::TagName{std::to_string(i)}; },
      [](int i) { return models::TagNameId{i}; });
}

UTEST(TestTagNameSerials, Overwriting) {
  TestOverwriting<TagNameSerials>(
      [](int i) {
        return caches::tag_names::DbEntry{models::TagNameId{i},
                                          std::to_string(i)};
      },
      [](int i) { return models::TagName{std::to_string(i)}; },
      [](int i) { return models::TagNameId{i}; });
}

UTEST(TestTagNameSerials, FindAbsent) {
  TagNameSerials cache{2};
  ASSERT_EQ(cache.FindById(models::TagNameId{0}), std::nullopt);
  ASSERT_EQ(cache.FindByValue(models::TagName{"abacaba"}), std::nullopt);
}
