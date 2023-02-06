#include <gtest/gtest.h>

#include "api_base/utils.hpp"

TEST(ApiOverDbProjection, TestProjection) {
  api_over_db::utils::Projection projection;
  projection.AddProjection("api.over.data.test");
  EXPECT_TRUE(projection.CheckMember({"api", "over"}));
  EXPECT_TRUE(projection.CheckMember({"api", "over", "data"}));
  EXPECT_TRUE(projection.CheckMember({"api", "over", "data", "test"}));
  EXPECT_TRUE(projection.CheckMember({"api", "over", "data", "test", "test2"}));
  EXPECT_FALSE(projection.CheckMember({"api", "over", "data", "test1"}));
}

TEST(ApiOverDbProjection, TestEmptyProjection) {
  api_over_db::utils::Projection projection;
  EXPECT_FALSE(projection.CheckMember({"any"}));
}

TEST(ApiOverDbProjection, TestProjectionSubset) {
  api_over_db::utils::Projection master{
      {"id", "timestamp", "revision", "data.field1", "data.field2",
       "data.field2.field2subfield", "data.field3.field3subfield1",
       "data.field3.field3subfield2"}};

  EXPECT_TRUE(master.IsSubset(master));

  {
    api_over_db::utils::Projection good{{"id"}};
    EXPECT_TRUE(good.IsSubset(master));
  }

  {
    api_over_db::utils::Projection good{{"id", "timestamp"}};
    EXPECT_TRUE(good.IsSubset(master));
  }

  {
    api_over_db::utils::Projection good{
        {"id", "timestamp", "data.field2.field2subfield"}};
    EXPECT_TRUE(good.IsSubset(master));
  }

  {
    api_over_db::utils::Projection good{{"id", "timestamp", "data.field2",
                                         "data.field2.field2subfield",
                                         "data.field3"}};
    EXPECT_TRUE(good.IsSubset(master));
  }

  {
    api_over_db::utils::Projection bad{{"bad_field"}};
    EXPECT_FALSE(bad.IsSubset(master));
  }

  {
    api_over_db::utils::Projection bad{{"id", "bad_field", "data.field2",
                                        "data.field2.field2subfield",
                                        "data.field3"}};
    EXPECT_FALSE(bad.IsSubset(master));
  }

  {
    api_over_db::utils::Projection bad{
        {"id", "timestamp", "data.field2", "data.field2.bad_subfield"}};
    EXPECT_FALSE(bad.IsSubset(master));
  }

  {
    api_over_db::utils::Projection bad{
        {"id", "timestamp", "data.field2", "data.field3.bad_subfield"}};
    EXPECT_FALSE(bad.IsSubset(master));
  }
}
