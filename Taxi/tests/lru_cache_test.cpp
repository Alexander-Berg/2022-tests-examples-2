#include <gtest/gtest.h>

#include "api-over-data/models/bucket_locked_lru_model.hpp"

namespace {
mongo::BSONObj MakeTestDocument(const std::string& key,
                                const std::string& secondary_key_1,
                                const std::string& value,
                                const uint32_t seconds = 0,
                                const uint32_t increment = 0) {
  ::mongo::BSONObjBuilder builder;
  builder.append("key", key)
      .append("secondary_key_1", secondary_key_1)
      .append("value", value)
      .append("updated_ts", mongo::Timestamp_t{seconds, increment});
  return builder.obj();
}
}  // namespace

namespace am = api_over_data::models;

namespace api_over_data::models {

template <>
bool ShouldUpdate(const int&, const int&) {
  return true;
}

struct LRUTraitsTest {
  struct Element {
    std::string key;
    std::string secondary_key_1;
    std::string value;

    Element(const std::string& key, const std::string& secondary_key_1,
            const std::string& value)
        : key(key), secondary_key_1(secondary_key_1), value(value) {}
  };

  static constexpr const char* kProviderName = "provider";

  static constexpr const size_t kSecondaryIndicesCount = 1;
  static constexpr const size_t kBucketsCount = 5;
  static constexpr const auto kFields = {"field_1"};

  static std::shared_ptr<const Element> ParseDocument(
      const mongo::BSONObj& doc) {
    std::string key;
    utils::helpers::FetchMember(key, doc, "key");
    std::string secondary_key_1;
    utils::helpers::FetchMember(secondary_key_1, doc, "secondary_key_1");
    std::string value;
    utils::helpers::FetchMember(value, doc, "value");
    return std::make_shared<const Element>(key, secondary_key_1, value);
  }

  static std::string ComputePrimaryKey(const mongo::BSONObj& doc) {
    std::string key;
    utils::helpers::FetchMember(key, doc, "key");
    return key;
  }

  static std::array<std::string, kSecondaryIndicesCount> ComputeSecondaryKeys(
      const Element& model) {
    return {model.secondary_key_1};
  }

  static bool BuildPrimaryKeyQuery(const std::string&, mongo::BSONObjBuilder&) {
    return true;
  }
  template <int key_number>
  static bool BuildSecondaryKeyQuery(const std::string&,
                                     mongo::BSONObjBuilder&) {
    return true;
  }
};

}  // namespace api_over_data::models

namespace utils {
template <class Traits>
class BucketLockedLRUModelTestingHelper {
 public:
  explicit BucketLockedLRUModelTestingHelper(
      am::BucketLockedLRUModel<Traits>& model)
      : model_(model) {
    const utils::mongo::CollectionWrapper* collection_ptr = nullptr;
    model_.Init(*collection_ptr, "test", 2);
    model_.MarkReady();
  }

  void Upsert(const ::mongo::BSONObj& doc) {
    bool _;
    uint32_t __;
    model_.Upsert(doc, __, __, _, _);
  }

  void Upsert(
      std::string&& primary_key,
      typename am::BucketLockedLRUModel<Traits>::ElementPtr&& parsed_doc,
      ::mongo::Timestamp_t&& revision, const bool force = true) {
    model_.Upsert(std::move(primary_key), std::move(parsed_doc),
                  std::move(revision), force);
  }

  auto FindByPrimary(const std::string& primary_key,
                     const bool change_priority = true) {
    return model_.FetchByPrimaryKey(primary_key, change_priority);
  }

  std::unordered_set<typename am::BucketLockedLRUModel<Traits>::ElementPtr>
  FindBySecondary(const std::string& key) {
    return model_.template FetchBySecondaryKey<0>(key);
  }

  size_t Size() const { return model_.Size(); }

 private:
  am::BucketLockedLRUModel<Traits>& model_;
};
}  // namespace utils

TEST(LRUCache, LRUmodel) {
  am::LRUCache<int> cache;
  cache.SetMaxSize(3);
  EXPECT_FALSE(cache.Upsert("1", std::make_shared<int>(1)).erased);
  // [{1:1}]
  auto found = cache.Find("1");
  // [{1:1}]
  EXPECT_TRUE(found);
  EXPECT_EQ(*found, 1);
  EXPECT_FALSE(cache.Upsert("2", std::make_shared<int>(2)).erased);
  // [{2:2}, {1:1}]
  found = cache.Find("1");
  // [{1:1}, {2:2}]
  EXPECT_TRUE(found);
  EXPECT_EQ(*found, 1);
  found = cache.Find("2");
  // [{2:2}, {1:1}]
  EXPECT_TRUE(found);
  EXPECT_EQ(*found, 2);
  EXPECT_FALSE(cache.Upsert("3", std::make_shared<int>(3)).erased);
  // [{3:3}, {2:2}, {1:1}]
  found = cache.Find("1");
  // [{1:1}, {3:3}, {2:2}]
  EXPECT_TRUE(found);
  EXPECT_EQ(*found, 1);
  found = cache.Find("2");
  // [{2:2}, {1:1}, {3:3}]
  EXPECT_TRUE(found);
  EXPECT_EQ(*found, 2);
  found = cache.Find("3");
  // [{3:3}, {2:2}, {1:1}]
  EXPECT_TRUE(found);
  EXPECT_EQ(*found, 3);
  EXPECT_FALSE(cache.Upsert("1", std::make_shared<int>(-1)).erased);
  // [{1:-1}, {3:3}, {2:2}]
  found = cache.Find("2");
  // [{2:2}, {1:-1}, {3:3}]
  EXPECT_TRUE(found);
  EXPECT_EQ(*found, 2);
  found = cache.Find("3");
  // [{3:3}, {2:2}, {1:-1}]
  EXPECT_TRUE(found);
  EXPECT_EQ(*found, 3);
  found = cache.Find("1");
  // [{1:-1}, {3:3}, {2:2}]
  EXPECT_TRUE(found);
  EXPECT_EQ(*found, -1);
  auto pair = cache.Upsert("4", std::make_shared<int>(4));
  // [{4,4}, {1:-1}, {3:3}]
  EXPECT_TRUE(pair.erased);
  EXPECT_EQ(*pair.erased, 2);
  found = cache.Find("1");
  // [{1:-1}, {4,4}, {3:3}]
  EXPECT_TRUE(found);
  EXPECT_EQ(*found, -1);
  found = cache.Find("4");
  // [{4,4}, {1:-1}, {3:3}]
  EXPECT_TRUE(found);
  EXPECT_EQ(*found, 4);
  found = cache.Find("3");
  // [{3:3}, {4,4}, {1:-1}]
  EXPECT_TRUE(found);
  EXPECT_EQ(*found, 3);
  pair = cache.Upsert("5", std::make_shared<int>(5));
  // [{5,5}, {3:3}, {4,4}]
  EXPECT_TRUE(pair.erased);
  EXPECT_EQ(*pair.erased, -1);
  pair = cache.Upsert("6", std::make_shared<int>(6));
  // [{6,6}, {5,5}, {3:3}]
  EXPECT_TRUE(pair.erased);
  EXPECT_EQ(*pair.erased, 4);
}

TEST(LRUCache, LRUCacheModel) {
  am::BucketLockedLRUModel<am::LRUTraitsTest> test_model;
  utils::BucketLockedLRUModelTestingHelper helper(test_model);
  for (int i = 0; i < 10; ++i) {
    std::string str = std::to_string(i);
    helper.Upsert(MakeTestDocument(str, str, str));
  }
  EXPECT_EQ(helper.Size(), size_t(10));
  for (int i = 0; i < 10; ++i) {
    std::string str = std::to_string(i);
    auto found = helper.FindByPrimary(str);
    EXPECT_TRUE(found);
    EXPECT_EQ(found->value, str);
    auto found_by_secondary = helper.FindBySecondary(str);
    EXPECT_EQ(found_by_secondary.size(), size_t(1));
    EXPECT_EQ((*found_by_secondary.begin())->value, str);
  }
  for (int i = 10; i < 15; ++i) {
    std::string str = std::to_string(i);
    helper.Upsert(MakeTestDocument(str, str, str));
  }
  EXPECT_EQ(helper.Size(), size_t(10));
  std::unordered_set<int> found_keys;
  for (int i = 0; i < 15; ++i) {
    std::string str = std::to_string(i);
    auto found = helper.FindByPrimary(str);
    auto found_by_secondary = helper.FindBySecondary(str);
    EXPECT_TRUE((!found and found_by_secondary.empty()) or
                (found and !found_by_secondary.empty()));
    if (found) {
      EXPECT_EQ(found->value, str);
      EXPECT_EQ(found_by_secondary.size(), size_t(1));
      EXPECT_EQ((*found_by_secondary.begin())->value, str);
      found_keys.insert(i);
    }
  }
  EXPECT_EQ(found_keys.size(), size_t(10));
  static const auto kCacheKeys =
      std::unordered_set<int>({14, 13, 12, 10, 9, 11, 0, 5, 6, 7});
  EXPECT_EQ(found_keys, kCacheKeys);
  // Revisions check, second upsert dont work cos old revision
  for (int i = 0; i < 2; ++i) {
    for (const auto& key : kCacheKeys) {
      std::string str = std::to_string(key);
      std::string value = std::to_string((2 - i) * key);
      auto ptr = std::make_shared<am::LRUTraitsTest::Element>(str, str, value);
      helper.Upsert(std::move(str), std::move(ptr), {1, 1}, false);
    }
    EXPECT_EQ(found_keys.size(), size_t(10));
    for (const auto& key : kCacheKeys) {
      std::string str = std::to_string(key);
      std::string value = std::to_string(2 * key);
      auto found = helper.FindByPrimary(str);
      auto found_by_secondary = helper.FindBySecondary(str);
      EXPECT_TRUE(found and !found_by_secondary.empty());
      EXPECT_EQ(found->value, value);
      EXPECT_EQ(found_by_secondary.size(), size_t(1));
      EXPECT_EQ((*found_by_secondary.begin())->value, value);
    }
  }
}
