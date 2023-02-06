#include <gmock/gmock.h>
#include <userver/utils/datetime.hpp>
#include "views/v1/internal/admin/assign_tasks_to_segments/post/view.hpp"

using namespace handlers::v1_internal_admin_assign_tasks_to_segments::post;

TEST(TestParseTableName, TestBadNames) {
  EXPECT_THROW(ParseTableName("segment"), std::runtime_error);
  EXPECT_THROW(ParseTableName(""), std::runtime_error);
  EXPECT_THROW(ParseTableName("segment_1"), std::runtime_error);
  EXPECT_THROW(ParseTableName("segment_1/"), std::runtime_error);
  EXPECT_THROW(ParseTableName("segment-1asdf"), std::runtime_error);
}

TEST(TestParseTableName, TestName) {
  auto res = ParseTableName("segment-1");
  ASSERT_EQ(res.segment, "segment");
  ASSERT_EQ(res.level, "1");
}

TEST(TestParseTableName, Test0Name) {
  auto res = ParseTableName("segment-0");
  ASSERT_EQ(res.segment, "segment");
  ASSERT_EQ(res.level, "0");
}

TEST(TestParseTableName, TestMoreThan10) {
  auto res = ParseTableName("segment-15");
  ASSERT_EQ(res.segment, "segment");
  ASSERT_EQ(res.level, "15");
}

TEST(TestParseTableName, TestComplexSegmentNameMoreThan10) {
  auto res = ParseTableName("segment-lol_kek-5-3");
  ASSERT_EQ(res.segment, "segment-lol_kek-5");
  ASSERT_EQ(res.level, "3");
}
