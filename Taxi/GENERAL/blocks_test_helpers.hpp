#include "blocks.hpp"

#include <algorithm>
#include <iterator>
#include <memory>

#include <gzip/gzip.hpp>

#include <driver-status/blocks_v2.fbs.h>

namespace blocks_test_helpers {
namespace fbs = ::driver_status::fbs::v2::blocks;

struct BlockReason {
  std::string driver_id;
  std::string park_id;
  std::string reason;
};

template <class Inserter>
void GenerateBlockReasons(Inserter inserter, std::size_t first_idx,
                          std::size_t last_idx,
                          const std::string& driver_id_prefix = "driver",
                          const std::string& park_id_prefix = "park",
                          const std::string& reason_prefix = "reason") {
  for (auto i = first_idx; i < last_idx; ++i) {
    const auto idx_str = std::to_string(i);
    *inserter = BlockReason{
        driver_id_prefix + idx_str, park_id_prefix + idx_str,
        (reason_prefix.empty() ? reason_prefix : reason_prefix + idx_str)};
  }
}

template <class InputIterator>
std::string PackBlockReasons(InputIterator begin, InputIterator end,
                             std::chrono::microseconds revision) {
  flatbuffers::FlatBufferBuilder fbb;
  std::vector<::flatbuffers::Offset<fbs::Item>> items_offset;
  for (auto i = begin; i < end; ++i) {
    auto driver_id_off = fbb.CreateString(i->driver_id);
    auto park_id_off = fbb.CreateString(i->park_id);
    auto reason_off = fbb.CreateString(i->reason);
    items_offset.push_back(::driver_status::fbs::v2::blocks::CreateItem(
        fbb, driver_id_off, park_id_off, reason_off, 0));
  }
  flatbuffers::Offset<fbs::List> list_offset =
      fbs::CreateListDirect(fbb, revision.count(), &items_offset);
  fbb.Finish(list_offset);
  return gzip::Compress(reinterpret_cast<const char*>(fbb.GetBufferPointer()),
                        fbb.GetSize());
}

inline std::shared_ptr<models::DriverBlocks> CreateBlocksStorage() {
  return std::make_shared<models::DriverBlocks>();
}
}  // namespace blocks_test_helpers
