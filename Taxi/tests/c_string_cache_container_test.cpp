#include <metrics-storage/caches/c_string_cache_container.hpp>
#include <userver/utest/utest.hpp>

namespace {
using namespace metrics_storage::caches;

std::string GetRandomString() {
  std::string val;
  for (int i = 0; i < 24; i++) {
    val.push_back('0' + rand() % 10);
  }
  val.shrink_to_fit();
  return val;
}

std::vector<std::string> GetValues(size_t count) {
  std::vector<std::string> values;
  for (size_t i = 0; i < count; i++) values.push_back(GetRandomString());
  return values;
}

void InsetValues(CStringCacheContainer* cache,
                 const std::vector<std::string>& values) {
  for (size_t i = 0; i < values.size(); i++) {
    cache->insert({i, values[i]});
  }
}

void CheckValues(CStringCacheContainer* cache,
                 const std::vector<std::string>& values) {
  for (size_t i = 0; i < values.size(); i++) {
    auto id = cache->GetId(values[i]);
    auto value = cache->GetValue(i);
    EXPECT_TRUE(id);
    EXPECT_TRUE(value);
    EXPECT_EQ(*id, i);
    EXPECT_EQ(*value, values[i]);
  }
}
}  // namespace

namespace custom::caches {

TEST(CStringCacheContainer, fill) {
  auto values = GetValues(1000);

  CStringCacheContainer* cache = new CStringCacheContainer();

  InsetValues(cache, values);
  InsetValues(cache, values);  // insert existing values to check if it is ok

  CheckValues(cache, values);

  delete cache;
}

TEST(CStringCacheContainer, copy) {
  auto values = GetValues(1000);

  CStringCacheContainer* cache = new CStringCacheContainer();
  InsetValues(cache, values);

  CStringCacheContainer cache_copy_constr = *cache;
  CStringCacheContainer cache_copy_assign;
  cache_copy_assign = *cache;

  delete cache;

  CheckValues(&cache_copy_constr, values);
  CheckValues(&cache_copy_assign, values);
}

TEST(CStringCacheContainer, move) {
  auto values = GetValues(1000);

  CStringCacheContainer* cache = new CStringCacheContainer();
  CStringCacheContainer* cache_2 = new CStringCacheContainer();
  InsetValues(cache, values);
  InsetValues(cache_2, values);

  CStringCacheContainer cache_move_constr = std::move(*cache);
  CStringCacheContainer cache_move_assign;
  cache_move_assign = std::move(*cache_2);

  delete cache;
  delete cache_2;

  CheckValues(&cache_move_constr, values);
  CheckValues(&cache_move_assign, values);
}

TEST(CStringCacheContainer, get_not_existing) {
  CStringCacheContainer* cache = new CStringCacheContainer();

  auto id = cache->GetId(GetRandomString());
  auto value = cache->GetValue(10);
  EXPECT_TRUE(id == std::nullopt);
  EXPECT_TRUE(value == std::nullopt);

  delete cache;
}

}  // namespace custom::caches
