#include <metrics-storage/caches/incremental_cache.hpp>
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

void InsertValues(SerialIncrementalContainer* cache,
                  const std::vector<std::string>& values, size_t start = 0) {
  for (size_t i = 0; i < values.size(); i++) {
    cache->insert({i + start, values[i]});
  }
}

void CheckValues(SerialIncrementalContainer* cache,
                 const std::vector<std::string>& values, size_t start = 0) {
  for (size_t i = 0; i < values.size(); i++) {
    auto id = cache->GetId(values[i]);
    auto value = cache->GetValue(i + start);
    EXPECT_TRUE(id);
    EXPECT_TRUE(value);
    EXPECT_EQ(*id, i + start);
    EXPECT_EQ(*value, values[i]);
  }
}

}  // namespace

namespace metrics_storage::caches {

UTEST(SerialIncrementalContainer, fill) {
  auto values = GetValues(1000);

  SerialIncrementalContainer cache = SerialIncrementalContainer(100);

  InsertValues(&cache, values);

  SerialIncrementalContainer cache_2 = SerialIncrementalContainer(cache);

  auto values_2 = GetValues(200);

  InsertValues(&cache_2, values_2, 1000);

  SerialIncrementalContainer cache_3 = SerialIncrementalContainer(cache_2);

  auto values_3 = GetValues(50);

  InsertValues(&cache_3, values_3, 1200);

  CheckValues(&cache_3, values);
  CheckValues(&cache_3, values_2, 1000);
  CheckValues(&cache_3, values_3, 1200);

  auto sizes = cache_3.GetSizes();
  EXPECT_TRUE(sizes.size() == 3);
  EXPECT_TRUE(sizes[0] == 1000);
  EXPECT_TRUE(sizes[1] == 200);
  EXPECT_TRUE(sizes[2] == 50);
  EXPECT_TRUE(cache_3.GetSizesString() == "1000_200_50__1250");

  auto containers_1 = cache.GetContainers();
  auto containers_2 = cache_2.GetContainers();
  auto containers_3 = cache_3.GetContainers();

  EXPECT_TRUE(containers_1.size() == 1);
  EXPECT_TRUE(containers_2.size() == 2);
  EXPECT_TRUE(containers_3.size() == 3);

  EXPECT_TRUE(containers_1[0] == containers_2[0]);
  EXPECT_TRUE(containers_2[0] == containers_3[0]);
  EXPECT_TRUE(containers_2[1] == containers_3[1]);
}

UTEST(SerialIncrementalContainer, fill_2) {
  auto values = GetValues(1000);

  SerialIncrementalContainer cache = SerialIncrementalContainer(100);

  InsertValues(&cache, values);

  auto sizes = cache.GetSizes();
  EXPECT_TRUE(sizes.size() == 1);
  EXPECT_TRUE(sizes[0] == 1000);
  EXPECT_TRUE(cache.GetSizesString() == "1000__1000");

  SerialIncrementalContainer cache_2 = SerialIncrementalContainer(cache);

  auto sizes_2 = cache_2.GetSizes();
  EXPECT_TRUE(sizes_2.size() == 2);
  EXPECT_TRUE(sizes_2[0] == 1000);
  EXPECT_TRUE(sizes_2[1] == 0);
  EXPECT_TRUE(cache_2.GetSizesString() == "1000_0__1000");

  SerialIncrementalContainer cache_3 = SerialIncrementalContainer(cache);

  auto sizes_3 = cache_3.GetSizes();
  EXPECT_TRUE(sizes_3.size() == 2);
  EXPECT_TRUE(sizes_3[0] == 1000);
  EXPECT_TRUE(sizes_3[1] == 0);
  EXPECT_TRUE(cache_3.GetSizesString() == "1000_0__1000");
}

}  // namespace metrics_storage::caches
