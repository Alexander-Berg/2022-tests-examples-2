#include "filters/infrastructure/driver_blocks/models/blocks.hpp"
#include <userver/utest/utest.hpp>
#include "blocks_test_helpers.hpp"

#include <models/driverid.hpp>

namespace helpers = blocks_test_helpers;
using caches::driver_status::CompressionType;
using models::driver_blocks::ReasonMapper;

TEST(BlocksCache, UnpackEmtpyString) {
  auto data = helpers::CreateBlocksStorage();
  EXPECT_ANY_THROW(models::UnpackInto(*data, "", CompressionType::kGzip));
}

TEST(BlocksCache, UnpackWithoutItems) {
  auto data = helpers::CreateBlocksStorage();

  namespace fbs = ::driver_status::fbs::v2::blocks;
  fbs::ListT list;
  list.revision = 0;
  flatbuffers::FlatBufferBuilder fbb;
  auto packed_list = fbs::List::Pack(fbb, &list);
  fbb.Finish(packed_list);
  std::string buf(gzip::Compress(
      reinterpret_cast<const char*>(fbb.GetBufferPointer()), fbb.GetSize()));

  EXPECT_THROW(models::UnpackInto(*data, buf, CompressionType::kGzip),
               std::runtime_error);
}

TEST(BlocksCache, UnpackWithEmptyBlocks) {
  auto data = helpers::CreateBlocksStorage();

  namespace fbs = ::driver_status::fbs::v2::blocks;
  flatbuffers::FlatBufferBuilder fbb;
  std::vector<::flatbuffers::Offset<fbs::Item>> items_offset;
  flatbuffers::Offset<fbs::List> list_offset =
      fbs::CreateListDirect(fbb, 0, &items_offset);
  fbb.Finish(list_offset);
  std::string buf(gzip::Compress(
      reinterpret_cast<const char*>(fbb.GetBufferPointer()), fbb.GetSize()));
  EXPECT_NO_THROW(models::UnpackInto(*data, buf, CompressionType::kGzip));
}

UTEST(BlocksCache, UnpackWrongItems) {
  auto data = helpers::CreateBlocksStorage();

  namespace fbs = ::driver_status::fbs::v2::blocks;
  {
    fbs::ListT list;
    fbs::ItemT item;
    item.park_id = "park01";
    item.reason = "reason01";
    list.revision = 0;
    list.item.push_back(std::make_unique<fbs::ItemT>(item));

    flatbuffers::FlatBufferBuilder fbb;
    auto packed_list = fbs::List::Pack(fbb, &list);
    fbb.Finish(packed_list);
    std::string buf(gzip::Compress(
        reinterpret_cast<const char*>(fbb.GetBufferPointer()), fbb.GetSize()));
    EXPECT_THROW(models::UnpackInto(*data, buf, CompressionType::kGzip),
                 std::runtime_error);
  }  // namespace fbs=::driver_status::fbs::v2::blocks;
  {
    fbs::ListT list;
    fbs::ItemT item;
    item.driver_id = "driver_id";
    item.reason = "reason01";
    list.revision = 0;
    list.item.push_back(std::make_unique<fbs::ItemT>(item));

    flatbuffers::FlatBufferBuilder fbb;
    auto packed_list = fbs::List::Pack(fbb, &list);
    fbb.Finish(packed_list);
    std::string buf(gzip::Compress(
        reinterpret_cast<const char*>(fbb.GetBufferPointer()), fbb.GetSize()));
    EXPECT_THROW(models::UnpackInto(*data, buf, CompressionType::kGzip),
                 std::runtime_error);
  }
  {
    fbs::ListT list;
    fbs::ItemT item;
    item.driver_id = "driver_id";
    item.park_id = "park01";
    list.revision = 0;
    list.item.push_back(std::make_unique<fbs::ItemT>(item));

    flatbuffers::FlatBufferBuilder fbb;
    auto packed_list = fbs::List::Pack(fbb, &list);
    fbb.Finish(packed_list);
    std::string buf(gzip::Compress(
        reinterpret_cast<const char*>(fbb.GetBufferPointer()), fbb.GetSize()));
    EXPECT_NO_THROW(models::UnpackInto(*data, buf, CompressionType::kGzip));
  }
  {
    fbs::ListT list;
    fbs::ItemT item;
    item.reason = "reason";
    item.driver_id = "driver_id";
    item.park_id = "park01";
    list.revision = 0;
    list.item.push_back(std::make_unique<fbs::ItemT>(item));

    flatbuffers::FlatBufferBuilder fbb;
    auto packed_list = fbs::List::Pack(fbb, &list);
    fbb.Finish(packed_list);
    std::string buf(gzip::Compress(
        reinterpret_cast<const char*>(fbb.GetBufferPointer()), fbb.GetSize()));
    EXPECT_NO_THROW(models::UnpackInto(*data, buf, CompressionType::kGzip));
  }
}

UTEST(BlocksCache, UnpackDrivers) {
  auto data = helpers::CreateBlocksStorage();

  namespace fbs = ::driver_status::fbs::v2::blocks;
  const std::size_t kBlocksCount = 10;
  const std::chrono::microseconds kRevisionExpected(15);

  {
    std::vector<helpers::BlockReason> block_reasons;
    GenerateBlockReasons(std::back_inserter(block_reasons), 0, kBlocksCount);
    block_reasons.push_back(helpers::BlockReason{"driver11", "park11", ""});

    std::string buf(PackBlockReasons(block_reasons.begin(), block_reasons.end(),
                                     kRevisionExpected));
    auto result = models::UnpackInto(*data, buf, CompressionType::kGzip);

    EXPECT_EQ(result.reads_count, kBlocksCount + 1);
    EXPECT_EQ(result.erases_count, 0);
    EXPECT_EQ(result.errors_count, 0);
    EXPECT_EQ(result.revision, kRevisionExpected);
    EXPECT_EQ(data->size(), kBlocksCount);

    for (const auto& item : block_reasons) {
      const auto dbid_uuid =
          models::DriverId::MakeDbidUuid(item.park_id, item.driver_id);
      if (item.park_id != "park11") {
        EXPECT_TRUE(data->count(dbid_uuid) > 0);
        EXPECT_EQ(ReasonMapper::GetName(data->at(dbid_uuid)), item.reason);
      } else {
        EXPECT_FALSE(data->count(dbid_uuid) > 0);
      }
    }
  }
  // adding new reasons
  {
    std::vector<helpers::BlockReason> block_reasons;
    GenerateBlockReasons(std::back_inserter(block_reasons), 0, kBlocksCount,
                         "driver", "park", "new_reason");
    std::string buf(PackBlockReasons(block_reasons.begin(), block_reasons.end(),
                                     kRevisionExpected));
    auto result = models::UnpackInto(*data, buf, CompressionType::kGzip);

    EXPECT_EQ(result.reads_count, kBlocksCount);
    EXPECT_EQ(result.erases_count, 0);
    EXPECT_EQ(result.errors_count, 0);
    EXPECT_EQ(result.revision, kRevisionExpected);
    EXPECT_EQ(data->size(), kBlocksCount);

    for (const auto& item : block_reasons) {
      const auto dbid_uuid =
          models::DriverId::MakeDbidUuid(item.park_id, item.driver_id);
      if (item.park_id != "park11") {
        EXPECT_TRUE(data->count(dbid_uuid) > 0);
        EXPECT_EQ(ReasonMapper::GetName(data->at(dbid_uuid)), item.reason);
      } else {
        EXPECT_FALSE(data->count(dbid_uuid) > 0);
      }
    }
  }
  // removing half reasons
  {
    std::vector<helpers::BlockReason> block_reasons;
    GenerateBlockReasons(std::back_inserter(block_reasons), 0, kBlocksCount / 2,
                         "driver", "park", "");
    GenerateBlockReasons(std::back_inserter(block_reasons), kBlocksCount / 2,
                         kBlocksCount);
    std::string buf(PackBlockReasons(block_reasons.begin(), block_reasons.end(),
                                     kRevisionExpected));
    auto result = models::UnpackInto(*data, buf, CompressionType::kGzip);

    EXPECT_EQ(result.reads_count, kBlocksCount);
    EXPECT_EQ(result.erases_count, kBlocksCount / 2);
    EXPECT_EQ(result.errors_count, 0);
    EXPECT_EQ(result.revision, kRevisionExpected);
    EXPECT_EQ(data->size(), kBlocksCount / 2);

    for (const auto& item : block_reasons) {
      const auto dbid_uuid =
          models::DriverId::MakeDbidUuid(item.park_id, item.driver_id);
      const auto idx = std::stoul(item.park_id.substr(4));
      if (item.park_id != "park11" && idx >= kBlocksCount / 2) {
        EXPECT_TRUE(data->count(dbid_uuid) > 0);
        EXPECT_EQ(ReasonMapper::GetName(data->at(dbid_uuid)), item.reason);
      } else {
        EXPECT_FALSE(data->count(dbid_uuid) > 0);
      }
    }
  }
}
