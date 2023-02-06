// todo move to agl

#include <agl/core/path.hpp>
#include <agl/core/path/json-pointer.hpp>

#include <userver/utest/utest.hpp>

namespace agl::core {

TEST(TestPathJsonPointer, Serialization) {
  Path path;

  path.Push("foo");
  path.Push(0);
  path.Push("a/b");
  path.Push("c%d");
  path.Push("e^f");
  path.Push("g|h");
  path.Push("i\\j");
  path.Push("k\"l");
  path.Push(" ");
  path.Push("m~n");
  path.Push(-8);

  std::string json_pointer = path::ToJsonPointer(path);
  EXPECT_EQ("/foo/0/a~1b/c%d/e^f/g|h/i\\j/k\"l/ /m~0n/-8", json_pointer);
}

TEST(TestPathJsonPointer, Deserialization) {
  Path path = path::FromJsonPointer(
      "/foo/0/a~1b/c%d/e^f/g|h/i\\j/k\"l/ /m~0n/ютиэф8/-8");

  EXPECT_FALSE(path.IsEmpty());
  EXPECT_EQ(path.Size(), 12);

  EXPECT_EQ(path.PopFront<std::string>(), "foo");
  EXPECT_EQ(path.PopFront<int64_t>(), 0);
  EXPECT_EQ(path.PopFront<std::string>(), "a/b");
  EXPECT_EQ(path.PopFront<std::string>(), "c%d");
  EXPECT_EQ(path.PopFront<std::string>(), "e^f");
  EXPECT_EQ(path.PopFront<std::string>(), "g|h");
  EXPECT_EQ(path.PopFront<std::string>(), "i\\j");
  EXPECT_EQ(path.PopFront<std::string>(), "k\"l");
  EXPECT_EQ(path.PopFront<std::string>(), " ");
  EXPECT_EQ(path.PopFront<std::string>(), "m~n");
  EXPECT_EQ(path.PopFront<std::string>(), "ютиэф8");
  EXPECT_EQ(path.PopFront<int64_t>(), -8);

  EXPECT_TRUE(path.IsEmpty());
  EXPECT_EQ(path.Size(), 0);
}

TEST(TestPathJsonPointer, Errors) {
  EXPECT_THROW(path::FromJsonPointer("foo/bar"), std::runtime_error);
}

}  // namespace agl::core
