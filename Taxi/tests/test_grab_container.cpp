#include <userver/utest/utest.hpp>

#include <utils/grab.hpp>

namespace hejmdal {

UTEST(TestGrabContainer, TestGrabVectorSinglePush) {
  utils::GrabVector<std::string> vec;
  vec.Push("hello");
  vec.Push("world");
  auto data = vec.GrabData();
  ASSERT_EQ(data.size(), 2u);
  EXPECT_EQ(data[0], "hello");
  EXPECT_EQ(data[1], "world");
  vec.Push("foo");
  data = vec.GrabData();
  ASSERT_EQ(data.size(), 1u);
  EXPECT_EQ(data[0], "foo");
}

UTEST(TestGrabContainer, TestGrabVectorMultiPush) {
  utils::GrabVector<std::string> vec;
  std::vector<std::string> values = {"hello", "world"};
  vec.Push(std::move(values));
  auto data = vec.GrabData();
  ASSERT_EQ(data.size(), 2u);
  EXPECT_EQ(data[0], "hello");
  EXPECT_EQ(data[1], "world");
}

UTEST(TestGrabContainer, TestGrabSetSingleInsert) {
  utils::GrabSet<std::string> set;
  set.Insert("hello");
  set.Insert("world");
  auto data = set.GrabData();
  ASSERT_EQ(data.size(), 2u);
  EXPECT_TRUE(data.find("hello") != data.end());
  EXPECT_TRUE(data.find("world") != data.end());
}

UTEST(TestGrabContainer, TestGrabSetMultiInsert) {
  utils::GrabSet<std::string> set;
  std::unordered_set<std::string> values = {"hello", "world"};
  set.Insert(values);
  auto data = set.GrabData();
  ASSERT_EQ(data.size(), 2u);
  EXPECT_TRUE(data.find("hello") != data.end());
  EXPECT_TRUE(data.find("world") != data.end());
}

UTEST(TestGrabContainer, TestGrabMapSingleInsert) {
  utils::GrabMap<std::string, int> set;
  set.Insert({"hello", 5});
  set.Insert({"world", 10});
  auto data = set.GrabData();
  ASSERT_EQ(data.size(), 2u);
  {
    auto hello_iter = data.find("hello");
    EXPECT_TRUE(hello_iter != data.end());
    EXPECT_EQ(hello_iter->second, 5);
  }
  {
    auto world_iter = data.find("world");
    EXPECT_TRUE(world_iter != data.end());
    EXPECT_EQ(world_iter->second, 10);
  }
}

}  // namespace hejmdal
