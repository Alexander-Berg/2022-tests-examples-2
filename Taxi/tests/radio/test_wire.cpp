#include <gtest/gtest.h>

#include "mock_block.hpp"

#include <radio/blocks/commutation/entry_points.hpp>
#include <radio/blocks/utils/bypass.hpp>

namespace hejmdal::radio::blocks {

TEST(TestWire, TestRawWire) {
  DataEntryPoint entry("entry");
  auto bypass = std::make_shared<Bypass>("bypass");
  Counter result;

  entry.OnDataOut(bypass, WireType::kRaw);
  bypass->OnDataOut(&result);

  entry.DataIn(Meta::kNull, time::Now(), 0.);

  EXPECT_EQ(result.data_count, 1u);
}

TEST(TestWire, TestWeakWire) {
  DataEntryPoint entry("entry");
  auto bypass = std::make_shared<Bypass>("bypass");
  Counter result;

  entry.OnDataOut(bypass, WireType::kWeak);
  bypass->OnDataOut(&result);

  entry.DataIn(Meta::kNull, time::Now(), 0.);
  entry.DataIn(Meta::kNull, time::Now(), 1.);

  EXPECT_EQ(result.data_count, 2u);

  bypass = nullptr;

  // No push out should happen
  entry.DataIn(Meta::kNull, time::Now(), 2.);

  EXPECT_EQ(result.data_count, 2u);
}

}  // namespace hejmdal::radio::blocks
