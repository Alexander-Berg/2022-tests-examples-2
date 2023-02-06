#include <gtest/gtest.h>

#include "bucket.hpp"

namespace {

using Bucket = tags::models::Bucket;
using Type = tags::models::EntityType;
using Entity = tags::models::Entity;
using Id = tags::models::Names::Id;

const std::string kValue{"value"};
const Entity kEntity{Type::kCarNumber, kValue};

const std::vector<Id> kEmptyIds{};
const std::vector<Id> kTestTagIds{34u, 52u, 128u};

}  // namespace

TEST(TagsBucket, SetTagIds) {
  Bucket bucket;

  ASSERT_EQ(bucket.GetSize(), 0u);
  ASSERT_EQ(bucket.GetTagIds(kEntity), kEmptyIds);

  // .GetSize() counts entities
  bucket.SetTags(kEntity, std::vector<Id>(kTestTagIds));
  ASSERT_EQ(bucket.GetSize(), 1u);
  ASSERT_EQ(bucket.GetTagIds(kEntity), kTestTagIds);

  // should remove entity record without tags
  bucket.SetTags(kEntity, std::vector<Id>());
  ASSERT_EQ(bucket.GetSize(), 0u);
  ASSERT_EQ(bucket.GetTagIds(kEntity), kEmptyIds);
}
