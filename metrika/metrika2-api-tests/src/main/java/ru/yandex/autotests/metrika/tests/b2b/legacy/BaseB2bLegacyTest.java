package ru.yandex.autotests.metrika.tests.b2b.legacy;

import org.apache.commons.lang3.StringUtils;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.metadata.legacy.LegacyPresetWrapper;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest;

import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;

/**
 * Created by konkov on 10.08.2015.
 */
public class BaseB2bLegacyTest extends BaseB2bTest {

    protected static final List<Counter> counters = asList(
            SENDFLOWERS_RU,
            Counters.SHATURA_COM);

    private static final String START_DATE = "2015-02-16";
    private static final String END_DATE = "2015-03-16";

    @Parameterized.Parameter(value = 0)
    public LegacyPresetWrapper preset;

    @Parameterized.Parameter(value = 1)
    public Counter counter;

    @Parameterized.Parameter(value = 2)
    public String goalId;

    protected IFormParameters getReportParameters() {
        IFormParameters reportParameters = new TableReportParameters()
                .withId(counter.get(ID))
                .withPreset(preset.getPreset().getName())
                .withDate1(START_DATE)
                .withDate2(END_DATE);

        if (StringUtils.isNotEmpty(goalId)) {
            reportParameters = makeParameters(ParametrizationTypeEnum.GOAL_ID.getParameterName(), goalId)
                    .append(reportParameters);
        }

        return reportParameters;
    }

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
    }
}
