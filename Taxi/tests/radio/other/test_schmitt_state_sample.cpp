#include <gtest/gtest.h>

#include <memory>

#include "radio/blocks/block.hpp"
#include "radio/blocks/commutation/entry_points.hpp"
#include "radio/blocks/meta.hpp"
#include "radio/blocks/other/schmitt_state_sample.hpp"
#include "radio/blocks/utils/buffers.hpp"
#include "utils/time.hpp"

namespace hejmdal::radio::blocks {

namespace {

time::TimePoint FromMillis(std::int64_t milliseconds_count) {
  return time::From<time::Milliseconds>(milliseconds_count);
}

}  // namespace

TEST(TestSchmittStateSampleBlocks, TestSchmittStateSample) {
  auto entry = std::make_shared<StateEntryPoint>("");
  auto test = std::make_shared<SchmittStateSample>("", 10, 5, 7);
  auto exit = std::make_shared<StateBuffer>("");
  entry->OnStateOut(test);
  test->OnStateOut(exit);

  {
    EXPECT_EQ(exit->LastTp(), FromMillis(0));
    EXPECT_EQ(exit->LastState(), State::kNoData);
  }

  {
    // заполняем все 10 значений
    entry->StateIn(Meta::kNull, FromMillis(100), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(100));
    EXPECT_EQ(exit->LastState(), State::kNoData);
    entry->StateIn(Meta::kNull, FromMillis(101), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(101));
    EXPECT_EQ(exit->LastState(), State::kNoData);
    entry->StateIn(Meta::kNull, FromMillis(102), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(102));
    EXPECT_EQ(exit->LastState(), State::kNoData);
    entry->StateIn(Meta::kNull, FromMillis(103), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(103));
    EXPECT_EQ(exit->LastState(), State::kNoData);
    entry->StateIn(Meta::kNull, FromMillis(104), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(104));
    EXPECT_EQ(exit->LastState(), State::kNoData);
    entry->StateIn(Meta::kNull, FromMillis(105), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(105));
    EXPECT_EQ(exit->LastState(), State::kNoData);
    entry->StateIn(Meta::kNull, FromMillis(106), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(106));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(107), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(107));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(108), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(108));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(109), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(109));
    EXPECT_EQ(exit->LastState(), State::kOk);
  }

  {
    //ломаем стейт
    entry->StateIn(Meta::kNull, FromMillis(110), State::kWarn);
    EXPECT_EQ(exit->LastTp(), FromMillis(110));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(111), State::kError);
    EXPECT_EQ(exit->LastTp(), FromMillis(111));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(112), State::kError);
    EXPECT_EQ(exit->LastTp(), FromMillis(112));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(113), State::kError);
    EXPECT_EQ(exit->LastTp(), FromMillis(113));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(114), State::kError);
    EXPECT_EQ(exit->LastTp(), FromMillis(114));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(115), State::kError);
    EXPECT_EQ(exit->LastTp(), FromMillis(115));
    EXPECT_EQ(exit->LastState(), State::kOk);
    // 4 ока, 1 варн и 5 ерроров. Следющий стейт >ok переключит в варн, тк
    // варна+ будет 70%
    entry->StateIn(Meta::kNull, FromMillis(116), State::kError);
    EXPECT_EQ(exit->LastTp(), FromMillis(116));
    EXPECT_EQ(exit->LastState(), State::kWarn);
    entry->StateIn(Meta::kNull, FromMillis(117), State::kWarn);
    EXPECT_EQ(exit->LastTp(), FromMillis(117));
    EXPECT_EQ(exit->LastState(), State::kWarn);
    // 7-ой еррор переключит к еррор
    entry->StateIn(Meta::kNull, FromMillis(118), State::kError);
    EXPECT_EQ(exit->LastTp(), FromMillis(118));
    EXPECT_EQ(exit->LastState(), State::kError);
    entry->StateIn(Meta::kNull, FromMillis(119), State::kError);
    EXPECT_EQ(exit->LastTp(), FromMillis(119));
    EXPECT_EQ(exit->LastState(), State::kError);
  }

  {
    // восстанавливаем все 10 значений
    entry->StateIn(Meta::kNull, FromMillis(120), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(121), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(122), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(123), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(124), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(125), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(126), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(127), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(128), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(129), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(129));
    EXPECT_EQ(exit->LastState(), State::kOk);
  }

  {
    // тестируем резки скачок стейта все 10 значений
    entry->StateIn(Meta::kNull, FromMillis(130), State::kCritical);
    EXPECT_EQ(exit->LastTp(), FromMillis(130));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(131), State::kCritical);
    EXPECT_EQ(exit->LastTp(), FromMillis(131));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(132), State::kCritical);
    EXPECT_EQ(exit->LastTp(), FromMillis(132));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(133), State::kCritical);
    EXPECT_EQ(exit->LastTp(), FromMillis(133));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(134), State::kCritical);
    EXPECT_EQ(exit->LastTp(), FromMillis(134));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(135), State::kCritical);
    EXPECT_EQ(exit->LastTp(), FromMillis(135));
    EXPECT_EQ(exit->LastState(), State::kOk);
    // сейчас будет седьмой
    entry->StateIn(Meta::kNull, FromMillis(136), State::kCritical);
    EXPECT_EQ(exit->LastTp(), FromMillis(136));
    EXPECT_EQ(exit->LastState(), State::kCritical);
    entry->StateIn(Meta::kNull, FromMillis(137), State::kCritical);
    EXPECT_EQ(exit->LastTp(), FromMillis(137));
    EXPECT_EQ(exit->LastState(), State::kCritical);
    entry->StateIn(Meta::kNull, FromMillis(138), State::kCritical);
    EXPECT_EQ(exit->LastTp(), FromMillis(138));
    EXPECT_EQ(exit->LastState(), State::kCritical);
    entry->StateIn(Meta::kNull, FromMillis(139), State::kCritical);
    EXPECT_EQ(exit->LastTp(), FromMillis(139));
    EXPECT_EQ(exit->LastState(), State::kCritical);
  }

  {
    // резкое возвращение
    entry->StateIn(Meta::kNull, FromMillis(140), State::kWarn);
    EXPECT_EQ(exit->LastTp(), FromMillis(140));
    EXPECT_EQ(exit->LastState(), State::kCritical);
    entry->StateIn(Meta::kNull, FromMillis(141), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(141));
    EXPECT_EQ(exit->LastState(), State::kCritical);
    entry->StateIn(Meta::kNull, FromMillis(142), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(142));
    EXPECT_EQ(exit->LastState(), State::kCritical);
    entry->StateIn(Meta::kNull, FromMillis(143), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(143));
    EXPECT_EQ(exit->LastState(), State::kCritical);
    // 1 варн и 3 ока. Червервый ок переключит в варн, а пятый в ок
    entry->StateIn(Meta::kNull, FromMillis(144), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(144));
    EXPECT_EQ(exit->LastState(), State::kWarn);
    entry->StateIn(Meta::kNull, FromMillis(145), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(145));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(146), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(146));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(147), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(147));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(148), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(148));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(149), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(149));
    EXPECT_EQ(exit->LastState(), State::kOk);
  }
}

}  // namespace hejmdal::radio::blocks
