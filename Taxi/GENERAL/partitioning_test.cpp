#include <gtest/gtest.h>

#include <models/partitioning.hpp>

using models::Partitioning;

TEST(Partitioning, GetPartitionCount) {
  EXPECT_EQ((Partitioning{0, 100}.GetPartitionCount()), 0);
  EXPECT_EQ((Partitioning{1, 100}.GetPartitionCount()), 1);
  EXPECT_EQ((Partitioning{100, 100}.GetPartitionCount()), 1);
  EXPECT_EQ((Partitioning{101, 100}.GetPartitionCount()), 2);
  EXPECT_EQ((Partitioning{100, 1}.GetPartitionCount()), 100);
  EXPECT_EQ((Partitioning{1001, 100}.GetPartitionCount()), 11);
  EXPECT_EQ((Partitioning{900, 30}.GetPartitionCount()), 30);
}

TEST(Partitioning, GetPartitionSize) {
  EXPECT_EQ((Partitioning{13, 100}.GetPartitionSize(0)), 13);

  EXPECT_EQ((Partitioning{13, 7}.GetPartitionSize(0)), 7);
  EXPECT_EQ((Partitioning{13, 7}.GetPartitionSize(1)), 6);

  const std::size_t size = 58;
  Partitioning sample{size, 7};

  std::size_t sum = 0;
  for (std::size_t i = 0; i < sample.GetPartitionCount(); i++) {
    sum += sample.GetPartitionSize(i);
  }
  EXPECT_EQ(sum, size);
}
