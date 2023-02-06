#include <gtest/gtest.h>

#include "../src/metrics.h"

namespace
{

using yanet::fatality::histogram;

TEST(histogram, median)
{
	histogram<std::uint64_t, 64> hist;
	for (int i = 0; i < 64; ++i)
	{
		hist[i] = i;
	}

	EXPECT_EQ(45, hist.quantile(0.5));
}

} // namespace
