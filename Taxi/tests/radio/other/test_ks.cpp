#include <gtest/gtest.h>

#include <chrono>
#include <vector>

#include <userver/formats/json/value.hpp>
#include <userver/formats/parse/common_containers.hpp>

#include <models/time_data.hpp>
#include <radio/blocks/commutation/entry_points.hpp>
#include <radio/blocks/meta.hpp>
#include <radio/blocks/other/ks.hpp>
#include <radio/blocks/utils/buffers.hpp>

#include "../../tools/testutils.hpp"

namespace hejmdal::radio::blocks {

static const std::int64_t kMsInHour = 3600000l;
static const std::int64_t kMsInDay = 86400000l;

TEST(TestKs, TestBlock) {
  auto json_test_data = formats::json::blocking::FromFile(
      testutils::kStasticDir + "/ks_test_inputs/ks_block_test.json");
  auto data = testutils::LoadJsonTS(json_test_data["data"]);
  auto p_values = testutils::LoadJsonTS(json_test_data["ks"]);

  auto entry_point = std::make_shared<blocks::DataEntryPoint>("entry");

  auto ks = std::make_shared<blocks::KsTest>("ks_test", kMsInDay, kMsInHour,
                                             true, 5, 1000);

  auto buffer = std::make_shared<blocks::DataBuffer>("data buffer");

  entry_point->OnDataOut(ks);
  ks->OnDataOut(buffer);

  size_t current_data_index = 0;
  size_t current_p_value_index = 0;

  bool p_values_started = false;

  while (current_data_index < data.size()) {
    auto sample = data.at(current_data_index);
    entry_point->DataIn(Meta::kNull, sample.GetTime(), sample.GetValue());
    if (!p_values_started) {
      p_values_started = buffer->LastTp() == sample.GetTime();
    }
    if (p_values_started) {
      auto p_value_sample = p_values.at(current_p_value_index);
      EXPECT_EQ(buffer->LastTp(), p_value_sample.GetTime());
      EXPECT_NEAR(buffer->LastValue(), p_value_sample.GetValue(), 1e-15);
      ++current_p_value_index;
    }
    ++current_data_index;
  }

  EXPECT_TRUE(p_values_started);
  EXPECT_EQ(p_values.size(), current_p_value_index);
}

}  // namespace hejmdal::radio::blocks
