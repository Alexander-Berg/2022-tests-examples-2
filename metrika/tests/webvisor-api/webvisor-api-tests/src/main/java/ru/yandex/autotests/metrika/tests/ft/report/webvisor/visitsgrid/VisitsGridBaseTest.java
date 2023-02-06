package ru.yandex.autotests.metrika.tests.ft.report.webvisor.visitsgrid;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2DataVisitsGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.webvisor.v2.VisitsGridParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;

import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static com.google.common.collect.ImmutableList.of;
import static java.lang.String.format;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.iterableWithSize;
import static org.junit.runners.Parameterized.Parameter;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.AT_NEW_WEBVISOR;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.matchers.Matchers.iterableHasDimensionValuesFilled;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by konkov on 10.12.2014.
 */
public abstract class VisitsGridBaseTest {
    protected static final List<Counter> COUNTERS = of(SENDFLOWERS_RU, AT_NEW_WEBVISOR);

    private static final String VISIT_ID = "ym:s:visitID";
    private static final String WEB_VISOR_VIEWED = "ym:s:webVisorViewed";
    private static final String WEB_VISOR_SELECTED = "ym:s:webVisorSelected";
    private static final String DATE_TIME = "ym:s:dateTime";

    private static final String START_DATE = "14daysAgo";
    private static final String END_DATE = "7daysAgo";

    protected final static UserSteps user = new UserSteps();

    private VisitsGridParameters reportParameters;

    @Parameter()
    public List<String> dimensions;

    @Parameter(1)
    public Counter counter;

    protected WebvisorV2DataVisitsGETSchema report;

    @Before
    public void setup() {
        reportParameters = new VisitsGridParameters();
        reportParameters.setId(counter.get(ID));
        reportParameters.setDimensions(dimensions);
        reportParameters.setDate1(START_DATE);
        reportParameters.setDate2(END_DATE);

        report = user.onWebVisorSteps().getVisitsGridAndExpectSuccess(reportParameters);

        assumeThat("данные для теста присутствуют", report,
                having(on(WebvisorV2DataVisitsGETSchema.class).getData(), iterableWithSize(greaterThan(0))));

    }

    @Test
    public void visitsGridVisitIDTest() {
        List<String> dimensionValues = user.onResultSteps().getDimensionValues(VISIT_ID, report);

        assertThat(format("поле %s заполнено", VISIT_ID), dimensionValues,
                iterableHasDimensionValuesFilled());
    }

    @Test
    public void visitsGridDateTimeTest() {
        List<String> dimensionValues = user.onResultSteps().getDimensionValues(DATE_TIME, report);

        assertThat(format("поле %s заполнено", DATE_TIME), dimensionValues,
                iterableHasDimensionValuesFilled());
    }

    @Test
    public void visitsGridViewedTest() {
        List<String> dimensionValues = user.onResultSteps().getDimensionValues(WEB_VISOR_VIEWED, report);

        assertThat(format("поле %s заполнено", WEB_VISOR_VIEWED), dimensionValues,
                iterableHasDimensionValuesFilled());
    }

    @Test
    public void visitsGridSelectedTest() {
        List<String> dimensionValues = user.onResultSteps().getDimensionValues(WEB_VISOR_SELECTED, report);

        assertThat(format("поле %s заполнено", WEB_VISOR_SELECTED), dimensionValues,
                iterableHasDimensionValuesFilled());
    }
}
