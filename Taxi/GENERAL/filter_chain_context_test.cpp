#include <gtest/gtest.h>

#include <candidates/processors/utils/filter_chain_context.hpp>

using candidates::filters::Context;
using candidates::filters::Result;
using candidates::processors::FilterChainContext;

TEST(FilterChainContext, Ctor) {
  FilterChainContext ctx({{}, "id"}, Context(10), 5);
  EXPECT_EQ(ctx.member.id, "id");
  EXPECT_EQ(ctx.context.score, 10);
  ASSERT_EQ(ctx.statuses.size(), 5);
  EXPECT_FALSE(ctx.statuses.front().processed);
  EXPECT_EQ(ctx.statuses.front().result, Result::kAllow);
  EXPECT_EQ(ctx.statuses.front().start_time,
            std::chrono::steady_clock::time_point{});
  EXPECT_EQ(ctx.delayed_filter_count, 0);
  EXPECT_EQ(ctx.start_time, std::chrono::steady_clock::time_point{});
}

TEST(FilterChainContext, SetResult) {
  FilterChainContext ctx({{}, "id"}, Context(10), 2);
  EXPECT_FALSE(ctx.GetStatus(0).processed);
  EXPECT_FALSE(ctx.GetStatus(1).processed);
  EXPECT_FALSE(ctx.GetStatus(0).IsFinished());
  EXPECT_FALSE(ctx.GetStatus(1).IsFinished());
  ctx.SetResult(1, Result::kIgnore);
  EXPECT_FALSE(ctx.GetStatus(0).processed);
  EXPECT_TRUE(ctx.GetStatus(1).processed);
  EXPECT_FALSE(ctx.GetStatus(0).IsFinished());
  EXPECT_TRUE(ctx.GetStatus(1).IsFinished());
  EXPECT_EQ(ctx.GetResult(1), Result::kIgnore);
  EXPECT_EQ(ctx.delayed_filter_count, 0);

  ctx.SetResult(0, Result::kRepeat);
  EXPECT_FALSE(ctx.GetStatus(0).IsFinished());
  EXPECT_EQ(ctx.delayed_filter_count, 1);
  ctx.SetResult(0, Result::kRepeat);
  EXPECT_FALSE(ctx.GetStatus(0).IsFinished());
  EXPECT_EQ(ctx.delayed_filter_count, 1);
  ctx.SetResult(0, Result::kAllow);
  EXPECT_TRUE(ctx.GetStatus(0).IsFinished());
  EXPECT_EQ(ctx.delayed_filter_count, 0);
}

TEST(FilterChainContext, IsReady) {
  FilterChainContext ctx({{}, "id"}, Context(10), 5);
  ctx.SetResult(1, Result::kAllow);
  ctx.SetResult(2, Result::kDisallow);
  ctx.SetResult(3, Result::kRepeat);
  ctx.SetResult(4, Result::kIgnore);
  EXPECT_TRUE(ctx.IsReadyToProcess(0, {}));
  EXPECT_FALSE(ctx.IsReadyToProcess(1, {}));
  EXPECT_TRUE(ctx.IsReadyToProcess(0, {1, 4}));
  EXPECT_FALSE(ctx.IsReadyToProcess(0, {1, 2, 4}));
  EXPECT_FALSE(ctx.IsReadyToProcess(0, {1, 2, 3, 4}));
}
