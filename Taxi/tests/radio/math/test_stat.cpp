#include <gtest/gtest.h>

#include <userver/formats/json/inline.hpp>

#include <radio/blocks/block_factory.hpp>
#include <radio/blocks/commutation/entry_points.hpp>
#include <radio/blocks/math/stat/sum.hpp>
#include <radio/blocks/math/stat/var.hpp>
#include <radio/blocks/utils/buffers.hpp>

namespace hejmdal::radio::blocks {

TEST(TestStatBlocks, TestSumSample) {
  auto entry = std::make_shared<DataEntryPoint>("");
  auto sum = std::make_shared<SumSample>("", 5);
  auto exit = std::make_shared<DataBuffer>("");
  entry->OnDataOut(sum);
  sum->OnDataOut(exit);

  entry->DataIn(Meta::kNull, time::Now(), 1);
  EXPECT_EQ(exit->LastValue(), 1);

  entry->DataIn(Meta::kNull, time::Now(), 3);
  EXPECT_EQ(exit->LastValue(), 4);

  entry->DataIn(Meta::kNull, time::Now(), 5);
  EXPECT_EQ(exit->LastValue(), 9);

  entry->DataIn(Meta::kNull, time::Now(), 7);
  EXPECT_EQ(exit->LastValue(), 16);

  entry->DataIn(Meta::kNull, time::Now(), 9);
  EXPECT_EQ(exit->LastValue(), 25);

  // sum.buffer is full now

  entry->DataIn(Meta::kNull, time::Now(), 11);
  EXPECT_EQ(exit->LastValue(), 35);

  entry->DataIn(Meta::kNull, time::Now(), 13);
  EXPECT_EQ(exit->LastValue(), 45);

  entry->DataIn(Meta::kNull, time::Now(), 15);
  EXPECT_EQ(exit->LastValue(), 55);
}

TEST(TestStatBlocks, TestSumValueToMeta) {
  auto entry = std::make_shared<DataEntryPoint>("");
  auto sum = std::make_shared<SumSample>(formats::json::MakeObject(
      "id", "test_sum", "sample_size", 5, "write_data_to_meta", true));
  auto exit = std::make_shared<DataBuffer>("");
  entry->OnDataOut(sum);
  sum->OnDataOut(exit);

  entry->DataIn(Meta::kNull, time::Now(), 1);
  EXPECT_EQ(exit->LastValue(), 1);
  EXPECT_EQ(exit->LastMeta().Get(),
            (formats::json::MakeObject(
                "block_params",
                formats::json::MakeObject(
                    "test_sum", formats::json::MakeObject("data", 1.0)))))
      << formats::json::ToString(exit->LastMeta().Get());

  entry->DataIn(Meta::kNull, time::Now(), 3);
  EXPECT_EQ(exit->LastValue(), 4);

  EXPECT_EQ(exit->LastMeta().Get(),
            (formats::json::MakeObject(
                "block_params",
                formats::json::MakeObject(
                    "test_sum", formats::json::MakeObject("data", 4.0)))))
      << formats::json::ToString(exit->LastMeta().Get());
}

TEST(TestStatBlocks, TestAvgWindow) {
  auto block_config = formats::json::MakeObject(
      "type", "avg_window", "id", "test", "duration_ms", 10000,  // 10 seconds
      "max_sample_size", 10000, "min_sample_size", 2);
  auto block = BlockFactory::CreateBlock(block_config);
  EXPECT_EQ("avg_window", block->GetType());

  auto exit = std::make_shared<DataBuffer>("");
  auto entry = std::make_shared<DataEntryPoint>("");

  entry->OnDataOut(block);
  block->OnDataOut(exit);

  auto now = time::From<time::Seconds>(0);
  const auto k1Sec = time::Seconds{1};

  entry->DataIn(Meta::kNull, now, 1);
  EXPECT_EQ(time::TimePoint{}, exit->LastTp());

  now += 3 * k1Sec;

  entry->DataIn(Meta::kNull, now, 3);
  EXPECT_EQ(2.0, exit->LastValue());

  now += 9 * k1Sec;

  entry->DataIn(Meta::kNull, now, 5);
  EXPECT_EQ(4.0, exit->LastValue());

  now += time::Milliseconds{1};

  entry->DataIn(Meta::kNull, now, 1);
  EXPECT_EQ(3.0, exit->LastValue());
}

TEST(TestStatBlocks, TestSumWindow) {
  auto block_config = formats::json::MakeObject(
      "type", "sum_window", "id", "test", "duration_ms", 10000,  // 10 seconds
      "max_sample_size", 10000);
  auto block = BlockFactory::CreateBlock(block_config);
  EXPECT_EQ("sum_window", block->GetType());

  auto exit = std::make_shared<DataBuffer>("");
  auto entry = std::make_shared<DataEntryPoint>("");

  entry->OnDataOut(block);
  block->OnDataOut(exit);

  auto now = time::From<time::Seconds>(0);
  const auto k1Sec = time::Seconds{1};

  entry->DataIn(Meta::kNull, now, 1);
  EXPECT_EQ(1.0, exit->LastValue());

  now += 3 * k1Sec;

  entry->DataIn(Meta::kNull, now, 3);
  EXPECT_EQ(4.0, exit->LastValue());

  now += 9 * k1Sec;

  entry->DataIn(Meta::kNull, now, 5);
  EXPECT_EQ(8.0, exit->LastValue());

  now += time::Milliseconds{1};

  entry->DataIn(Meta::kNull, now, 1);
  EXPECT_EQ(9.0, exit->LastValue());
}

TEST(TestStatBlocks, TestAvgSample) {
  {
    //проверяем вычисления
    auto entry = std::make_shared<DataEntryPoint>("");
    auto avg = std::make_shared<AvgSample>("", 5);
    auto exit = std::make_shared<DataBuffer>("");
    entry->OnDataOut(avg);
    avg->OnDataOut(exit);

    entry->DataIn(Meta::kNull, time::Now(), 1);
    EXPECT_EQ(exit->LastValue(), 1);

    entry->DataIn(Meta::kNull, time::Now(), 3);
    EXPECT_EQ(exit->LastValue(), 2);

    entry->DataIn(Meta::kNull, time::Now(), 5);
    EXPECT_EQ(exit->LastValue(), 3);

    entry->DataIn(Meta::kNull, time::Now(), 7);
    EXPECT_EQ(exit->LastValue(), 4);

    entry->DataIn(Meta::kNull, time::Now(), 9);
    EXPECT_EQ(exit->LastValue(), 5);

    // avg.buffer is full now

    entry->DataIn(Meta::kNull, time::Now(), 11);
    EXPECT_EQ(exit->LastValue(), 7);

    entry->DataIn(Meta::kNull, time::Now(), 13);
    EXPECT_EQ(exit->LastValue(), 9);

    entry->DataIn(Meta::kNull, time::Now(), 15);
    EXPECT_EQ(exit->LastValue(), 11);
  }

  {
    //проверяем переключение стейтв при наполнении
    auto entry = std::make_shared<DataEntryPoint>("");
    auto exit_reset = std::make_shared<StateEntryPoint>("");
    auto avg = std::make_shared<AvgSample>("", 5);
    auto exit = std::make_shared<StateBuffer>("");
    entry->OnDataOut(avg);
    exit_reset->OnStateOut(exit);
    avg->OnStateOut(exit);

    EXPECT_EQ(exit->LastState(), State::kNoData);
    entry->DataIn(Meta::kNull, time::Now(), 1);
    EXPECT_EQ(exit->LastState(), State::kNoData);
    entry->DataIn(Meta::kNull, time::Now(), 3);
    EXPECT_EQ(exit->LastState(), State::kNoData);
    entry->DataIn(Meta::kNull, time::Now(), 5);
    EXPECT_EQ(exit->LastState(), State::kNoData);
    entry->DataIn(Meta::kNull, time::Now(), 7);
    EXPECT_EQ(exit->LastState(), State::kNoData);

    time::TimePoint tp = time::From<time::Milliseconds>(1337);
    entry->DataIn(Meta::kNull, tp, 9);
    EXPECT_EQ(exit->LastTp(), tp);
    EXPECT_EQ(exit->LastState(), State::kOk);

    // avg.buffer наполнился, больше стейт не переключится
    tp = time::From<time::Milliseconds>(1338);
    exit_reset->StateIn(Meta::kNull, tp, State::kNoData);
    EXPECT_EQ(exit->LastTp(), tp);
    EXPECT_EQ(exit->LastState(), State::kNoData);
    entry->DataIn(Meta::kNull, time::Now(), 11);
    entry->DataIn(Meta::kNull, time::Now(), 13);
    entry->DataIn(Meta::kNull, time::Now(), 15);
    entry->DataIn(Meta::kNull, time::Now(), 15);
    entry->DataIn(Meta::kNull, time::Now(), 15);
    entry->DataIn(Meta::kNull, time::Now(), 15);
    entry->DataIn(Meta::kNull, time::Now(), 15);
    entry->DataIn(Meta::kNull, time::Now(), 15);
    entry->DataIn(Meta::kNull, time::Now(), 15);
    EXPECT_EQ(exit->LastTp(), tp);
    EXPECT_EQ(exit->LastState(), State::kNoData);
  }
}

TEST(TestStatBlocks, TestVarSample) {
  auto entry = std::make_shared<DataEntryPoint>("");
  auto var = std::make_shared<VarSample>("", 3);
  auto exit = std::make_shared<DataBuffer>("");
  entry->OnDataOut(var);
  var->OnDataOut(exit);

  entry->DataIn(Meta::kNull, time::Now(), 1);
  EXPECT_NEAR(exit->LastValue(), 0, 0.00001);

  entry->DataIn(Meta::kNull, time::Now(), 3);
  EXPECT_NEAR(exit->LastValue(), 1, 0.00001);

  entry->DataIn(Meta::kNull, time::Now(), 5);
  EXPECT_NEAR(exit->LastValue(), 1.63299, 0.00001);

  // var.buffer is full now

  entry->DataIn(Meta::kNull, time::Now(), 7);
  EXPECT_NEAR(exit->LastValue(), 1.63299, 0.00001);

  entry->DataIn(Meta::kNull, time::Now(), 9);
  EXPECT_NEAR(exit->LastValue(), 1.63299, 0.00001);

  entry->DataIn(Meta::kNull, time::Now(), 8);
  EXPECT_NEAR(exit->LastValue(), 0.81649, 0.00001);
}

}  // namespace hejmdal::radio::blocks
