#include <userver/utest/utest.hpp>

#include <views/common/common.hpp>

using handlers::common::ContentKey;

TEST(ContentKey, Basic) {
  {
    ContentKey key{"taxi_surge", "econom", "default"};
    EXPECT_EQ("taxi_surge/econom/default", key.AsString());
    EXPECT_EQ("taxi_surge", key.GetContentType());
    EXPECT_EQ("econom", key.GetCategory());
    EXPECT_EQ("default", key.GetLayer());
  }

  {
    ContentKey key{"taxi_surge/econom/default"};
    EXPECT_EQ("taxi_surge/econom/default", key.AsString());
    EXPECT_EQ("taxi_surge", key.GetContentType());
    EXPECT_EQ("econom", key.GetCategory());
    EXPECT_EQ("default", key.GetLayer());
  }
}

TEST(ContentKey, Errors) {
  EXPECT_THROW((ContentKey{""}), std::runtime_error);
  EXPECT_THROW((ContentKey{"/"}), std::runtime_error);
  EXPECT_THROW((ContentKey{"//"}), std::runtime_error);
  EXPECT_THROW((ContentKey{"taxi_surge"}), std::runtime_error);
  EXPECT_THROW((ContentKey{"taxi_surge/"}), std::runtime_error);
  EXPECT_THROW((ContentKey{"taxi_surge/econom"}), std::runtime_error);
  EXPECT_THROW((ContentKey{"taxi_surge/econom/"}), std::runtime_error);
  EXPECT_THROW((ContentKey{"taxi_surge/econom/econom/default"}),
               std::runtime_error);
  EXPECT_THROW((ContentKey{"taxi_surge/econom", "econom", "default"}),
               std::runtime_error);
  EXPECT_THROW((ContentKey{"taxi_surge", "econom/default", "default"}),
               std::runtime_error);
  EXPECT_THROW((ContentKey{"taxi_surge", "econom/default", ""}),
               std::runtime_error);
  EXPECT_THROW((ContentKey{"", "econom", "default"}), std::runtime_error);
  EXPECT_THROW((ContentKey{"taxi_surge", "", "default"}), std::runtime_error);
  EXPECT_THROW((ContentKey{"taxi_surge", "econom", ""}), std::runtime_error);
}
