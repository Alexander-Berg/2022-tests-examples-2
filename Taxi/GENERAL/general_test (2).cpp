#include <gtest/gtest.h>

#include <candidates/result_storages/general/general.hpp>

using GeneralStorage = candidates::result_storages::General;
using GeoMember = candidates::GeoMember;
using candidates::filters::Context;

TEST(GeneralStorage, NoLimit) {
  formats::json::Value params;
  EXPECT_ANY_THROW(GeneralStorage res(params));
}

TEST(GeneralStorage, MemberOrder) {
  formats::json::ValueBuilder params;
  const size_t limit = 3;
  params[GeneralStorage::kLimit] = limit;
  GeneralStorage storage(params.ExtractValue());
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 0);
  EXPECT_EQ(storage.expected_count(), limit);
  EXPECT_EQ(storage.worst_score(), std::nullopt);

  storage.Add(GeoMember{{}, "id1"}, Context(9));
  storage.Add(GeoMember{{}, "id2"}, Context(8));
  storage.Add(GeoMember{{}, "id3"}, Context(6));
  storage.Add(GeoMember{{}, "id4"}, Context(7));
  EXPECT_TRUE(storage.full());
  EXPECT_EQ(storage.size(), limit);
  EXPECT_EQ(storage.expected_count(), 0);
  EXPECT_EQ(storage.worst_score().value(), 8);

  storage.Finish();
  const auto& result = storage.Get();
  ASSERT_EQ(result.size(), limit);
  EXPECT_EQ(result[0].member.id, "id3");
  EXPECT_EQ(result[1].member.id, "id4");
  EXPECT_EQ(result[2].member.id, "id2");
}
