package ru.yandex.autotests.metrika.tests.b2b.metrika.particulars;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bParticularTest;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.Collections;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA_2_0;

@Title("B2B на отобранных вручную параметрах internal запросов")
@Stories(Requirements.Story.Internal.JSON_VALIDATION)

public class ParticularsB2bInternalTest extends BaseB2bParticularTest {

    private static final Counter COUNTER = YANDEX_METRIKA_2_0;
    private static final Long counterID = COUNTER.getId();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return Collections.singletonList(
                createParams("Comparison of last hit date in publishers",
                        RequestTypes.addCounterToPublishersLastVisitSchema(counterID),
                        new CommonReportParameters()
                )
        );
    }

    @Override
    public void check() {
        Object referenceBean = userOnRef.onReportSteps().getRawReport(requestType, reportParameters);
        Object testingBean = userOnTest.onReportSteps().getRawReport(requestType, reportParameters);

        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);

        assertThat("ответы совпадают", testingBean, beanEquivalent(referenceBean).fields(getIgnore()).withVariation(doubleWithAccuracy));
    }
}
