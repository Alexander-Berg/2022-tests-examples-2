#include <userver/utest/utest.hpp>

#include <string>

#include "quota_distribution_graph.hpp"

TEST(TestQuotaDistributionGraph, TestValidAddition) {
  internal::QuotaDistributionGraph graph;
  graph.Enable();

  graph.AddQuotaUsage("1", "2", 10);
  graph.AddQuotaUsage("1", "3", 20);
  graph.AddQuotaUsage("2", "3", 30);

  ASSERT_TRUE(graph.IsEnabled());
  ASSERT_EQ(graph.GetQuotaUsage("1"), -30);
  ASSERT_EQ(graph.GetQuotaUsage("2"), -20);
  ASSERT_EQ(graph.GetQuotaUsage("3"), 50);

  graph.Disable();
  ASSERT_FALSE(graph.IsEnabled());
  ASSERT_EQ(graph.GetQuotaUsage("1"), 0);
  ASSERT_EQ(graph.GetQuotaUsage("2"), 0);
  ASSERT_EQ(graph.GetQuotaUsage("3"), 0);
}

TEST(TestQuotaDistributionGraph, TestValidRelease) {
  internal::QuotaDistributionGraph graph;
  graph.Enable();

  graph.AddQuotaUsage("1", "2", 10);
  graph.AddQuotaUsage("1", "3", 20);
  graph.AddQuotaUsage("2", "3", 30);

  graph.ReleaseDonations("1", std::nullopt, std::nullopt);
  ASSERT_EQ(graph.GetQuotaUsage("1"), 0);
  ASSERT_EQ(graph.GetQuotaUsage("2"), -30);
  ASSERT_EQ(graph.GetQuotaUsage("3"), 30);

  graph.ReleaseDonations("2", 14, std::nullopt);
  ASSERT_EQ(graph.GetQuotaUsage("1"), 0);
  ASSERT_EQ(graph.GetQuotaUsage("2"), -16);
  ASSERT_EQ(graph.GetQuotaUsage("3"), 16);

  graph.ReleaseDonations("2", 2, {{{"3", 4}}});
  ASSERT_EQ(graph.GetQuotaUsage("1"), 0);
  ASSERT_EQ(graph.GetQuotaUsage("2"), -14);
  ASSERT_EQ(graph.GetQuotaUsage("3"), 14);

  graph.ReleaseDonations("2", std::nullopt, {{{"3", 10}}});
  ASSERT_EQ(graph.GetQuotaUsage("1"), 0);
  ASSERT_EQ(graph.GetQuotaUsage("2"), -4);
  ASSERT_EQ(graph.GetQuotaUsage("3"), 4);

  graph.ReleaseDonations("2", std::nullopt, std::nullopt);
  ASSERT_EQ(graph.GetQuotaUsage("1"), 0);
  ASSERT_EQ(graph.GetQuotaUsage("2"), 0);
  ASSERT_EQ(graph.GetQuotaUsage("3"), 0);

  graph.ReleaseDonations("3", std::nullopt, std::nullopt);
  ASSERT_EQ(graph.GetQuotaUsage("1"), 0);
  ASSERT_EQ(graph.GetQuotaUsage("2"), 0);
  ASSERT_EQ(graph.GetQuotaUsage("3"), 0);
}
