package ru.yandex.autotests.metrika.tests.ft.report.metrika.authorization;

import org.junit.Test;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.*;

/**
 * Created by okunev on 21.11.2014.
 */
public abstract class AuthorizationBaseTest {

    private static final Counter publicCounter = METRIKA_DEMO;
    protected static final Counter ownCounter = YANDEX_BY_TESTER;
    protected static final Counter accessibleCounter = TEST_COUNTER;
    protected static final Counter privateCounter = KVAZI_KAZINO;

    private static final String METRIC_NAME = "ym:s:visits";
    private static final String DIMENSION_NAME = "ym:s:age";
    private static final String DATE = "2014-09-01";

    protected static UserSteps user = new UserSteps().withDefaultAccuracy();

    protected TableReportParameters getReportParameters() {
        return new TableReportParameters()
                .withDimension(DIMENSION_NAME)
                .withMetric(METRIC_NAME)
                .withDate1(DATE)
                .withDate2(DATE);
    }

    @Test
    public void tableAuthorizationCheckPublicCounter() {
        user.onReportSteps().getTableReportAndExpectSuccess(getReportParameters().withId(publicCounter.get(ID)));
    }
}
