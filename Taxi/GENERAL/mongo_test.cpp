// todo move to agl

#include <agl/core/path.hpp>
#include <agl/core/path/mongo.hpp>

#include <userver/utest/utest.hpp>

namespace agl::core {

TEST(PathMongo, Serialization) {
  Path path;

  path.Push("order_info");
  path.Push("statistics");
  path.Push("status_updates");
  path.Push(-1);
  path.Push("q");

  EXPECT_EQ("order_info.statistics.status_updates.q",
            path::ToMongoProjectionKey(path));

  Path empty;
  EXPECT_EQ("", path::ToMongoProjectionKey(empty));

  Path single;
  single.Push("order");
  EXPECT_EQ("order", path::ToMongoProjectionKey(single));
}

TEST(PathMongo, Variable) {
  Path path;
  path.Push("candidates");
  path.Push("$candidate_index");
  path.Push("udid");
  EXPECT_EQ("candidates.udid", path::ToMongoProjectionKey(path));
}

TEST(PathMongo, VariableFirstItem) {
  Path path;
  path.Push("$object");
  path.Push("value");
  EXPECT_THROW(path::ToMongoProjectionKey(path), std::runtime_error);
}

}  // namespace agl::core
