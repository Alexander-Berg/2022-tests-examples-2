#include <gtest/gtest.h>

#include <userver/formats/json/value_builder.hpp>

#include <radio/blocks/commutation/entry_points.hpp>
#include <radio/blocks/meta.hpp>
#include <radio/blocks/other/peak_indicator.hpp>
#include <radio/blocks/utils/buffers.hpp>
#include <utils/time.hpp>

namespace hejmdal::radio::blocks {

utils::RingQueue<double> MakeQueue(const std::vector<double>& shape) {
  utils::RingQueue<double> result(shape.size());
  for (auto value : shape) {
    result.Push(value);
  }
  return result;
}

TEST(TestPeakIndicator, TestCheckShape) {
  {
    std::vector<double> shape{1.0, 2.0, 3.0, 2.0, 1.0};
    EXPECT_TRUE(PeakIndicator::CheckShape(MakeQueue(shape)));
  }
  {
    std::vector<double> shape{1.0, 2.0, 3.0};
    EXPECT_FALSE(PeakIndicator::CheckShape(MakeQueue(shape)));
  }

  {
    std::vector<double> shape{3.0, 2.0, 1.0};
    EXPECT_TRUE(PeakIndicator::CheckShape(MakeQueue(shape)));
  }

  {
    std::vector<double> shape{1.0, 2.0, 3.0, 2.0, 1.0, 2.0};
    EXPECT_FALSE(PeakIndicator::CheckShape(MakeQueue(shape)));
  }
}

TEST(TestPeakIndicator, TestHappyPath) {
  auto entry_point = std::make_shared<blocks::DataEntryPoint>("entry");

  formats::json::ValueBuilder builder;
  builder["type"] = "peak_indicator";
  builder["id"] = "peak_indicator_test";
  builder["sample_size"] = 5;

  auto block = std::make_shared<blocks::PeakIndicator>(builder.ExtractValue());

  auto buffer = std::make_shared<blocks::DataBuffer>("data buffer");

  entry_point->OnDataOut(block);
  block->OnDataOut(buffer);

  auto curent_time = time::From<time::Milliseconds>(100);

  entry_point->DataIn(Meta::kNull, curent_time, 1.0);
  EXPECT_DOUBLE_EQ(0.0, buffer->LastValue());

  curent_time += time::Milliseconds{1000};

  entry_point->DataIn(Meta::kNull, curent_time, 2.0);
  EXPECT_DOUBLE_EQ(0.0, buffer->LastValue());

  curent_time += time::Milliseconds{1000};

  entry_point->DataIn(Meta::kNull, curent_time, 3.0);
  EXPECT_DOUBLE_EQ(0.0, buffer->LastValue());

  curent_time += time::Milliseconds{1000};

  entry_point->DataIn(Meta::kNull, curent_time, 2.0);
  EXPECT_DOUBLE_EQ(1.0, buffer->LastValue());

  curent_time += time::Milliseconds{1000};

  entry_point->DataIn(Meta::kNull, curent_time, 1.0);
  EXPECT_DOUBLE_EQ(1.0, buffer->LastValue());
}
}  // namespace hejmdal::radio::blocks
