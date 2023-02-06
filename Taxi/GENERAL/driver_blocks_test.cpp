#include "driver_blocks.hpp"
#include "models/blocks_test_helpers.hpp"

#include <userver/utest/utest.hpp>

namespace cf = candidates::filters;
namespace helpers = blocks_test_helpers;

const cf::FilterInfo kEmptyInfo;

UTEST(DriverBlocksTest, Sample) {
  using caches::driver_status::CompressionType;

  auto blocks_storage = helpers::CreateBlocksStorage();
  cf::infrastructure::DriverBlocks filter(kEmptyInfo, blocks_storage);
  helpers::BlockReason block1{"DriverId1", "ParkId1", "reason"};
  helpers::BlockReason block2{"DriverId", "ParkId", "reason"};

  candidates::GeoMember member;
  cf::Context context;
  member.id = "ParkId_DriverId";
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);

  const auto data1 = helpers::PackBlockReasons(
      &block1, &block1 + 1, std::chrono::microseconds::zero());
  models::UnpackInto(*blocks_storage, data1, CompressionType::kGzip);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);

  const auto data2 = helpers::PackBlockReasons(
      &block2, &block2 + 1, std::chrono::microseconds::zero());
  models::UnpackInto(*blocks_storage, data2, CompressionType::kGzip);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kDisallow);
}
