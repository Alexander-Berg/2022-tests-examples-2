#include <taxi/tools/dorblu/lib/tests/testbase.h>

#include <taxi/tools/dorblu/lib/include/yasm_metrics.h>

#include <string>
#include <iostream>
#include <sstream>
#include <iomanip>

TEST(Yasm, YasmMetricsTestCase)
{
    YasmMetrics metrics;

    HgramYasmMetric metric1("m0_hgram");
    metric1.addBucket(HgramYasmMetric::HgramBucket{0.0, 2});
    metric1.addBucket(HgramYasmMetric::HgramBucket{0.5, 1});
    metrics.addMetric(std::move(metric1));

    NumericalYasmMetric metric2("m1_summ", 100500);
    metrics.addMetric(std::move(metric2));

    NumericalYasmMetric metric3("m2_max", 3.1);
    metrics.addMetric(std::move(metric3));

    std::stringstream ss;
    ss << metrics;

    auto correct = "[[\"m0_hgram\",[[0,2],[0.5,1]]],[\"m1_summ\",100500],[\"m2_max\",3.1]]";
    EXPECT_EQ(ss.str(), correct);
}
