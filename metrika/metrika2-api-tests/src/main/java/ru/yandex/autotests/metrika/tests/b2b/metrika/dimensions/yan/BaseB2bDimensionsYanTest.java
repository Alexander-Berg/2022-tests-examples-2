package ru.yandex.autotests.metrika.tests.b2b.metrika.dimensions.yan;

import com.google.common.collect.ImmutableList;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bYanTest;

import java.util.Collection;

import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;

public class BaseB2bDimensionsYanTest extends BaseB2bYanTest {

    @Parameterized.Parameter()
    public String dimensionName;

    @Parameterized.Parameter(1)
    public String metricName;

    private static final String METRIC_YAN = "ym:s:yanRenders";

    @Parameterized.Parameters(name = "Измерение {0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .addAll(CombinatorialBuilder.builder()
                        .values(userOnTest.onMetadataSteps().getDimensionsRaw(
                                dimension(table(TableEnum.VISITS).and(yan()))))
                        .value(METRIC_YAN)
                        .build())
                .build();
    }
}
