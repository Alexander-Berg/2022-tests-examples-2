#include <gtest/gtest.h>
#include <redis/base.hpp>

using namespace redis;

TEST(CmdArgs, TestConstruct) {
  const std::string str = "ARG2";
  CmdArgs args("ARG1", str, 10);
  ASSERT_EQ(args.args.size(), 1u);
  ASSERT_EQ(args.args[0].size(), 3u);
  ASSERT_EQ(args.args[0][0], "ARG1");
  ASSERT_EQ(args.args[0][1], "ARG2");
  ASSERT_EQ(args.args[0][2], "10");
}

TEST(CmdArgs, TestThen) {
  const std::string str = "ARG2";
  CmdArgs args("ARG1", str, 10);
  ASSERT_EQ(args.args.size(), 1u);
  ASSERT_EQ(args.args[0].size(), 3u);
  ASSERT_EQ(args.args[0][0], "ARG1");
  ASSERT_EQ(args.args[0][1], "ARG2");
  ASSERT_EQ(args.args[0][2], "10");
  args.Then("ARG4", 5);
  ASSERT_EQ(args.args.size(), 2u);
  ASSERT_EQ(args.args[0].size(), 3u);
  ASSERT_EQ(args.args[0][0], "ARG1");
  ASSERT_EQ(args.args[0][1], "ARG2");
  ASSERT_EQ(args.args[0][2], "10");
  ASSERT_EQ(args.args[1].size(), 2u);
  ASSERT_EQ(args.args[1][0], "ARG4");
  ASSERT_EQ(args.args[1][1], "5");
}

TEST(CmdArgs, TestConstructPerformance) {
  auto start = std::chrono::high_resolution_clock::now();
  for (auto i = 0; i < 100000; ++i) {
    static const std::string str = "ARG2";
    CmdArgs args("ARG1", str, 10);
  }
  auto end = std::chrono::high_resolution_clock::now();

  ASSERT_LT(end - start, std::chrono::seconds(1));
}
