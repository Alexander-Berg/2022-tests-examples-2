#include <gtest/gtest.h>

#include <cmath>

#include "radio/blocks/commutation/entry_points.hpp"
#include "radio/blocks/math/sigma_bounds.hpp"
#include "radio/blocks/utils/buffers.hpp"

namespace hejmdal::radio::blocks {

TEST(TestSigmaBoundsBlocks, TestSigmaBoundsGeneratorSample) {
  auto meta = Meta::kNull;
  auto tp = time::Now();
  auto coeff = 4.0;

  auto entry = std::make_shared<DataEntryPoint>("");
  auto bnd_generator =
      std::make_shared<SigmaBoundsGeneratorSample>("", 10, coeff);
  auto exit = std::make_shared<BoundsBuffer>("");
  entry->OnDataOut(bnd_generator);
  bnd_generator->OnBoundsOut(exit);

  {
    //    EXPECT_EQ(bnd_generator->IsFrozen(), true);
    EXPECT_EQ(exit->LastLower(), std::numeric_limits<double>::lowest());
    EXPECT_EQ(exit->LastUpper(), std::numeric_limits<double>::max());

    entry->DataIn(meta, tp, 1.0);
    entry->DataIn(meta, tp, 2.0);
    entry->DataIn(meta, tp, 1.0);
    entry->DataIn(meta, tp, 2.0);
    entry->DataIn(meta, tp, 1.0);
    entry->DataIn(meta, tp, 2.0);
    entry->DataIn(meta, tp, 1.0);
    entry->DataIn(meta, tp, 2.0);
    entry->DataIn(meta, tp, 1.0);
    entry->DataIn(meta, tp, 2.0);

    auto avg = 1.5;
    auto var = std::sqrt(0.25);
    EXPECT_NEAR(exit->LastLower(), avg - coeff * var, 0.00001);
    EXPECT_NEAR(exit->LastUpper(), avg + coeff * var, 0.00001);
  }

  {
    entry->DataIn(meta, tp, 4.0);
    entry->DataIn(meta, tp, 4.0);
    entry->DataIn(meta, tp, 4.0);
    entry->DataIn(meta, tp, 4.0);

    // last 10 values are: 1,2,1,2,1,2,4,4,4,4
    auto avg = 2.5;
    auto var = std::sqrt(1.65);
    EXPECT_NEAR(exit->LastLower(), avg - coeff * var, 0.00001);
    EXPECT_NEAR(exit->LastUpper(), avg + coeff * var, 0.00001);

    entry->DataIn(meta, tp, 4.0);
    entry->DataIn(meta, tp, 5.0);
    entry->DataIn(meta, tp, 5.0);
    entry->DataIn(meta, tp, 5.0);
    entry->DataIn(meta, tp, 5.0);
    entry->DataIn(meta, tp, 5.0);
    // last 10 values are: 4,4,4,4,4,5,5,5,5,5
    avg = 4.5;
    var = std::sqrt(0.25);
    EXPECT_NEAR(exit->LastLower(), avg - coeff * var, 0.00001);
    EXPECT_NEAR(exit->LastUpper(), avg + coeff * var, 0.00001);
  }
}

}  // namespace hejmdal::radio::blocks
