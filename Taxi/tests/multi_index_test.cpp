#include <gtest/gtest.h>

#include "api-over-data/models/bucket_locked_replica.hpp"
#include "api-over-data/utils/multi_index_testing_helper.hpp"

#include <mongo/bson/bsonmisc.h>
#include <mongo/mongo.hpp>
#include <utils/helpers/params.hpp>

namespace api_over_data::models {

struct ZeroSecondaryTraitsTest {
  struct Element {
    std::string key;
    std::string value;

    Element(const std::string& key, const std::string& value)
        : key(key), value(value) {}
  };

  static constexpr const char* kProviderName = "zero_provider";

  static constexpr const size_t kSecondaryIndicesCount = 0;
  static constexpr const size_t kBucketsCount = 1000;

  static std::shared_ptr<const Element> ParseDocument(
      const mongo::BSONObj& doc) {
    std::string key;
    utils::helpers::FetchMember(key, doc, "key");
    std::string value;
    utils::helpers::FetchMember(value, doc, "value");
    return std::make_shared<const Element>(key, value);
  }

  static std::string ComputePrimaryKey(const mongo::BSONObj& doc) {
    std::string key;
    utils::helpers::FetchMember(key, doc, "key");
    return key;
  }
};

class ModelTestZeroSecondary
    : public BucketLockedReplica<ZeroSecondaryTraitsTest> {
 public:
  std::shared_ptr<const ZeroSecondaryTraitsTest::Element> Get(
      const std::string& key) const {
    return GetByPrimaryKey(key, nullptr);
  }
};

struct TwoSecondaryTraitsTest {
  struct Element {
    std::string key;
    std::string secondary_key_1;
    std::string secondary_key_2;
    std::string value;

    Element(const std::string& key, const std::string& secondary_key_1,
            const std::string& secondary_key_2, const std::string& value)
        : key(key),
          secondary_key_1(secondary_key_1),
          secondary_key_2(secondary_key_2),
          value(value) {}
  };

  static constexpr const char* kProviderName = "two_provider";

  static constexpr const size_t kSecondaryIndicesCount = 2;
  static constexpr const size_t kBucketsCount = 1000;

  static std::shared_ptr<const Element> ParseDocument(
      const mongo::BSONObj& doc) {
    std::string key;
    utils::helpers::FetchMember(key, doc, "key");
    std::string secondary_key_1;
    utils::helpers::FetchMember(secondary_key_1, doc, "secondary_key_1");
    std::string secondary_key_2;
    utils::helpers::FetchMember(secondary_key_2, doc, "secondary_key_2");
    std::string value;
    utils::helpers::FetchMember(value, doc, "value");
    return std::make_shared<const Element>(key, secondary_key_1,
                                           secondary_key_2, value);
  }

  static std::string ComputePrimaryKey(const mongo::BSONObj& doc) {
    std::string key;
    utils::helpers::FetchMember(key, doc, "key");
    return key;
  }

  static std::array<std::string, kSecondaryIndicesCount> ComputeSecondaryKeys(
      const Element& model) {
    return {model.secondary_key_1, model.secondary_key_2};
  }
};

class ModelTestTwoSecondary
    : public BucketLockedReplica<TwoSecondaryTraitsTest> {
 public:
  std::shared_ptr<const TwoSecondaryTraitsTest::Element> GetByPrimaryKey(
      const std::string& key) const {
    return BucketLockedReplica<TwoSecondaryTraitsTest>::GetByPrimaryKey(
        key, nullptr);
  }

  std::unordered_set<std::string> GetValuesBySecondaryKey1(
      const std::string& key) const {
    auto models = GetBySecondaryKey<0>(key, nullptr);
    std::unordered_set<std::string> result;
    for (const auto& model : models) {
      result.emplace(model->value);
    }
    return result;
  }

  std::unordered_set<std::string> GetValuesBySecondaryKey2(
      const std::string& key) const {
    auto models = GetBySecondaryKey<1>(key, nullptr);
    std::unordered_set<std::string> result;
    for (const auto& model : models) {
      result.emplace(model->value);
    }
    return result;
  }
};

}  // namespace api_over_data::models

mongo::BSONObj MakeTestDocument(const std::string& key,
                                const std::string& value) {
  ::mongo::BSONObjBuilder builder;
  builder.append("key", key)
      .append("value", value)
      .append("updated_ts", mongo::Timestamp_t{0, 0});
  return builder.obj();
}

mongo::BSONObj MakeTestDocument(const std::string& key,
                                const std::string& secondary_key_1,
                                const std::string& secondary_key_2,
                                const std::string& value) {
  ::mongo::BSONObjBuilder builder;
  builder.append("key", key)
      .append("secondary_key_1", secondary_key_1)
      .append("secondary_key_2", secondary_key_2)
      .append("value", value)
      .append("updated_ts", mongo::Timestamp_t{0, 0});
  return builder.obj();
}

TEST(MultiIndex, ZeroFields) {
  api_over_data::models::ModelTestZeroSecondary model;
  auto helper = utils::BucketLockedReplicaTestingHelper(model);
  helper.MarkReady();
  helper.Upsert(MakeTestDocument("key1", "value1"));
  helper.Upsert(MakeTestDocument("key2", "value2"));

  EXPECT_EQ(model.Size(), 2ul);

  EXPECT_TRUE(model.Get("key1") != nullptr);
  EXPECT_EQ(model.Get("key1")->key, "key1");
  EXPECT_EQ(model.Get("key1")->value, "value1");

  EXPECT_TRUE(model.Get("key2") != nullptr);
  EXPECT_EQ(model.Get("key2")->key, "key2");
  EXPECT_EQ(model.Get("key2")->value, "value2");
}

TEST(MultiIndex, TwoFields) {
  api_over_data::models::ModelTestTwoSecondary model;
  auto helper = utils::BucketLockedReplicaTestingHelper(model);
  helper.MarkReady();
  helper.Upsert(MakeTestDocument("key1", "s1key1", "s2key1", "value1"));
  helper.Upsert(MakeTestDocument("key2", "s1key1", "s2key2", "value2"));
  helper.Upsert(MakeTestDocument("key3", "s1key2", "s2key1", "value3"));
  helper.Upsert(MakeTestDocument("key4", "s1key2", "s2key2", "value4"));

  EXPECT_EQ(model.Size(), 4ul);

  EXPECT_TRUE(model.GetByPrimaryKey("key1") != nullptr);
  EXPECT_EQ(model.GetByPrimaryKey("key1")->key, "key1");
  EXPECT_EQ(model.GetByPrimaryKey("key1")->secondary_key_1, "s1key1");
  EXPECT_EQ(model.GetByPrimaryKey("key1")->secondary_key_2, "s2key1");
  EXPECT_EQ(model.GetByPrimaryKey("key1")->value, "value1");

  EXPECT_EQ(model.GetValuesBySecondaryKey1("s1key1"),
            std::unordered_set<std::string>({"value1", "value2"}));
  EXPECT_EQ(model.GetValuesBySecondaryKey1("s1key2"),
            std::unordered_set<std::string>({"value3", "value4"}));
  EXPECT_EQ(model.GetValuesBySecondaryKey1("s2key1"),
            std::unordered_set<std::string>({}));

  EXPECT_EQ(model.GetValuesBySecondaryKey2("s2key1"),
            std::unordered_set<std::string>({"value1", "value3"}));
  EXPECT_EQ(model.GetValuesBySecondaryKey2("s2key2"),
            std::unordered_set<std::string>({"value2", "value4"}));
  EXPECT_EQ(model.GetValuesBySecondaryKey2("s1key1"),
            std::unordered_set<std::string>({}));
}
