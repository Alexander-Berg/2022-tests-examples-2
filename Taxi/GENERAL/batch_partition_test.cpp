#include <userver/utest/utest.hpp>

#include <utils/batch_partition.hpp>

namespace utils {

TEST(BatchPartitionTest, UniformBatches) {
  BatchPartition partition(200, 100);
  EXPECT_EQ(partition.GetCount(), 2);
  EXPECT_EQ(partition.GetAt(0), 100);
  EXPECT_EQ(partition.GetAt(1), 100);
  EXPECT_EQ(partition.GetAt(2), 0);
}

TEST(BatchPartitionTest, DifferentBatches1) {
  BatchPartition partition(199, 100);
  EXPECT_EQ(partition.GetCount(), 2);
  EXPECT_EQ(partition.GetAt(0), 100);
  EXPECT_EQ(partition.GetAt(1), 99);
  EXPECT_EQ(partition.GetAt(2), 0);
}

TEST(BatchPartitionTest, DifferentBatches2) {
  BatchPartition partition(201, 100);
  EXPECT_EQ(partition.GetCount(), 3);
  EXPECT_EQ(partition.GetAt(0), 67);
  EXPECT_EQ(partition.GetAt(1), 67);
  EXPECT_EQ(partition.GetAt(2), 67);
  EXPECT_EQ(partition.GetAt(3), 0);
}

TEST(BatchPartitionTest, ZeroTotalSize) {
  BatchPartition partition(0, 100);
  EXPECT_EQ(partition.GetCount(), 0);
  EXPECT_EQ(partition.GetAt(0), 0);
}

TEST(BatchPartitionTest, ZeroBatchSize) {
  EXPECT_THROW(BatchPartition(100, 0), std::invalid_argument);
}

}  // namespace utils
