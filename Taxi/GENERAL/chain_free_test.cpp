#include <gtest/gtest.h>

#include <filters/efficiency/fetch_chain_info/fetch_chain_info.hpp>
#include "chain_free.hpp"

namespace cf = candidates::filters;
namespace cfe = cf::efficiency;

static cf::FilterInfo kEmptyInfo;

TEST(ChainFree, NoInfo) {
  cfe::ChainFree filter(kEmptyInfo, false);

  cf::Context context;
  EXPECT_EQ(filter.Process({}, context), cf::Result::kDisallow);
}

TEST(ChainFree, WithInfo) {
  cfe::ChainFree filter(kEmptyInfo, false);

  cf::Context context;
  cfe::FetchChainInfo::Set(context,
                           std::make_shared<models::ChainBusyDriver>());
  EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
}
